from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence

from openai import OpenAI

import database
from models import SystemSettings

try:  # pragma: no cover - optional dependency
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover - environment may not provide the package
    genai = None  # type: ignore

DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"
DEFAULT_GEMINI_MODEL = "gemini-1.5-pro"
HIGH_CONFIDENCE_THRESHOLD = 0.75


class NexusQuantumReasoning:
    """
    Orquestrador central responsavel por planejar pesquisas, reordenar resultados
    e realizar auto-correcao cognitiva do pipeline RAG.
    """

    def __init__(self) -> None:
        self._deepseek_client: OpenAI | None = None
        self._low_confidence_alert: bool = False

    # ------------------------------------------------------------------
    # Planejamento
    # ------------------------------------------------------------------
    def plan_research_4_0(
        self,
        query: str,
        available_tools: Sequence[str],
    ) -> Dict[str, str]:
        """
        Executa o planejamento da missao de pesquisa via LLM, retornando JSON estrito.
        """
        if self._is_introspection_query(query):
            return {
                "tool": "quantum_search",
                "search_query": "SELF identidade e configuracao do Nexus",
                "context_of_use": "Auto-Introspeccao do Sistema",
            }

        tools_block = (
            "\n".join(f"- {tool}" for tool in available_tools)
            or "- Nenhuma ferramenta cadastrada."
        )
        system_prompt = (
            "Voce e o Nexus-Quantum-Reasoning (NQR), orquestrador central do Nexus.\n"
            "Analise a solicitacao do usuario, escolha a melhor ferramenta disponivel e\n"
            "elabore um termo de busca otimizado acompanhado do contexto de uso.\n"
            "Responda estritamente no seguinte formato JSON:\n"
            "{\n"
            '  "tool": "nome_da_ferramenta",\n'
            '  "search_query": "termo otimizado",\n'
            '  "context_of_use": "Contexto Determinado"\n'
            "}\n"
            "Ferramentas disponiveis:\n"
            f"{tools_block}\n"
            "Nao adicione texto extra, apenas o JSON."
        )

        response_payload: Dict[str, str] = {}
        try:
            raw_response = self._run_chat_completion(
                system_prompt=system_prompt,
                user_prompt=query,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            response_payload = json.loads(raw_response)
        except Exception as error:  # noqa: BLE001
            print(f"[NQR] Falha ao planejar pesquisa: {error}")
            response_payload = {}

        fallback_tool = available_tools[0] if available_tools else "tavily_search"

        normalized = {
            "tool": response_payload.get("tool") or fallback_tool,
            "search_query": response_payload.get("search_query") or query,
            "context_of_use": response_payload.get("context_of_use")
            or "Pesquisa Geral",
        }
        return normalized

    # ------------------------------------------------------------------
    # Re-ranqueamento
    # ------------------------------------------------------------------
    def re_rank_by_confidence(self, documents: Sequence[Any]) -> List[Any]:
        """
        Reordena documentos calculando Score Final = Intrinseca + Externa.
        """
        if not documents:
            self._low_confidence_alert = True
            return []

        self._low_confidence_alert = False
        scored_docs: List[Any] = []
        for document in documents:
            intrinsic = self._get_numeric_attr(
                document, "confianca_intrinseca", default=0.0
            )
            external_raw = self._get_attr(document, "confianca_externa", default=None)
            try:
                external = float(external_raw) if external_raw is not None else None
            except (TypeError, ValueError):
                external = None

            if external is None:
                if intrinsic <= 0.0:
                    external = self._estimate_external_confidence(document)
                else:
                    external = 0.0

            external = max(0.0, min(float(external), 1.0))
            intrinsic = max(0.0, min(float(intrinsic), 1.0))
            final_score = (intrinsic * 0.7) + (external * 0.3)

            self._set_attr(document, "confianca_externa", external)
            self._set_attr(document, "score_final", final_score)
            scored_docs.append(document)

        scored_docs.sort(
            key=lambda doc: self._get_numeric_attr(doc, "score_final", default=0.0),
            reverse=True,
        )

        if scored_docs:
            best_score = self._get_numeric_attr(
                scored_docs[0], "score_final", default=0.0
            )
            self._low_confidence_alert = best_score < 0.5
        else:
            self._low_confidence_alert = True

        best_doc_id = self._get_attr(scored_docs[0], "id") if scored_docs else None
        for document in scored_docs:
            intrinsic_value = self._get_numeric_attr(
                document, "confianca_intrinseca", default=0.0
            )
            if intrinsic_value <= 0.0:
                continue
            node_id = self._get_attr(document, "id")
            if not node_id:
                continue
            confidence_delta = 0.05 if node_id == best_doc_id else 0.01
            try:
                database.register_memory_activation(
                    node_id,
                    boost=confidence_delta,
                )
            except Exception as error:  # noqa: BLE001
                print(
                    f"[NQR] Aviso: nao foi possivel reforcar memoria {node_id}: {error}"
                )
        return scored_docs

    # ------------------------------------------------------------------
    # Auto-correcao
    # ------------------------------------------------------------------
    def self_correct_rag(
        self, final_response: str, context_facts: Sequence[Any]
    ) -> str:
        """
        Detecta contradicoes com fatos de alta confianca e corrige a resposta final.
        """
        if not final_response or not context_facts:
            return final_response

        high_confidence_docs = [
            doc
            for doc in context_facts
            if self._get_numeric_attr(doc, "confianca_intrinseca", default=0.0)
            >= HIGH_CONFIDENCE_THRESHOLD
        ]
        if not high_confidence_docs:
            return final_response

        corrected_response = final_response
        for document in high_confidence_docs:
            if not self._quick_validate_fact(corrected_response, document):
                continue

            analysis = self._diagnose_contradiction(corrected_response, document)
            if not analysis.get("contradiction"):
                continue

            proposed_response = analysis.get("corrected_response") or corrected_response
            dissonance = analysis.get("dissonance") or ""
            node_id = self._get_attr(document, "id")
            if node_id:
                dissonance_text = (
                    dissonance or "Dissonancia cognitiva detectada pelo NQR."
                )
                try:
                    database.register_cognitive_dissonance(node_id, dissonance_text)
                except Exception as error:  # noqa: BLE001
                    print(
                        f"[NQR] Aviso: nao foi possivel registrar dissonancia para {node_id}: {error}"
                    )
                try:
                    database.register_memory_activation(node_id, boost=-0.1)
                except Exception as error:  # noqa: BLE001
                    print(
                        f"[NQR] Aviso: nao foi possivel reduzir confianca de {node_id}: {error}"
                    )
            if proposed_response:
                self._register_meta_knowledge(
                    original_response=corrected_response,
                    corrected_response=proposed_response,
                    document=document,
                    dissonance=dissonance,
                )
                corrected_response = proposed_response
                break

        return corrected_response

    # ------------------------------------------------------------------
    # Planejamento preditivo
    # ------------------------------------------------------------------
    def predictive_replan(
        self,
        task_descriptor: Dict[str, Any],
        simulated_result: str,
    ) -> Dict[str, Any] | None:
        """
        Analisa resultados simulados e decide se um replanejamento e necessario.
        """
        if not simulated_result:
            return None

        system_prompt = (
            "Você é o Nexus-Quantum-Reasoning responsável pelo Motor de Simulação de Realidade. "
            "Analise o comando e o resultado simulado e decida se é necessário replanejar. "
            "Retorne APENAS JSON no formato:\n"
            "{\n"
            '  "should_replan": true|false,\n'
            '  "new_command": "opcional",\n'
            '  "message": "justificativa concisa"\n'
            "}"
        )
        user_prompt = (
            f"TAREFA:\n{json.dumps(task_descriptor, ensure_ascii=False)}\n\n"
            f"RESULTADO_SIMULADO:\n{simulated_result}\n"
            "Avalie riscos, inconsistências e proponha ajustes se necessário."
        )

        try:
            raw = self._run_chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            parsed = json.loads(raw)
        except Exception as error:  # noqa: BLE001
            print(f"[NQR] Falha no predictive_replan: {error}")
            return None

        should_replan = bool(parsed.get("should_replan"))
        payload = {
            "should_replan": should_replan,
            "new_command": (parsed.get("new_command") or "").strip(),
            "message": (parsed.get("message") or "").strip(),
        }
        if not should_replan:
            return None
        return payload

    # ------------------------------------------------------------------
    # Compressao de contexto
    # ------------------------------------------------------------------
    def compress_chat_history(
        self,
        session_id: str,
        history: List[Dict[str, str]],
    ) -> None:
        """
        Resumo sinaptico do historico de conversa para armazenamento no Neo4j.
        """
        if not session_id or not history:
            return

        transcript = "\n".join(
            f"{item.get('role', 'desconhecido').upper()}: {item.get('content', '')}"
            for item in history
        )
        if len(transcript) <= 4000:
            return

        system_prompt = (
            "Você é o compressor sináptico do Nexus. Resuma o histórico de conversas a seguir "
            "em um parágrafo conciso, focando em fatos, decisões e tópicos importantes."
        )

        try:
            summary = self._run_chat_completion(
                system_prompt=system_prompt,
                user_prompt=transcript,
                temperature=0.2,
            )
        except Exception as error:  # noqa: BLE001
            print(f"[NQR] Falha ao comprimir histórico da sessão {session_id}: {error}")
            return

        summary_text = summary.strip()
        if not summary_text:
            return

        try:
            database.save_context_summary(session_id, summary_text)
        except Exception as error:  # noqa: BLE001
            print(f"[NQR] Falha ao persistir resumo da sessão {session_id}: {error}")

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------
    def _diagnose_contradiction(self, response: str, document: Any) -> Dict[str, Any]:
        fact_text = self._extract_document_text(document)
        url = self._get_attr(document, "url", default="Desconhecida")

        system_prompt = (
            "Voce e o modulo de Auto-Correcao do Nexus-Quantum-Reasoning. Sua funcao e garantir a integridade da memoria. Analise se a resposta fornecida contradiz o FATO CONSOLIDADO de ALTA CONFIANCA informado.\n"
            "Analise se a resposta fornecida contradiz o fato consolidado informado.\n"
            "Responda obrigatoriamente em JSON estrito no formato:\n"
            "{\n"
            '  "contradiction": true | false,\n'
            '  "corrected_response": "texto",\n'
            '  "dissonance": "explicacao resumida"\n'
            "}\n"
            "Se nao houver contradicao, defina 'contradiction' como false e mantenha os demais campos vazios."
        )

        user_prompt = (
            f"RESPOSTA ATUAL:\n{response}\n\n"
            f"FATO CONSOLIDADO (alta confianca, fonte {url}):\n{fact_text}\n\n"
            "Caso haja conflito, corrija a resposta seguindo o fato e explique resumidamente a dissonancia."
        )

        try:
            raw = self._run_chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            return json.loads(raw)
        except Exception as error:  # noqa: BLE001
            print(f"[NQR] Falha ao diagnosticar contradicao: {error}")
            return {"contradiction": False}

    def _quick_validate_fact(self, response: str, document: Any) -> bool:
        fact_text = self._extract_document_text(document)
        system_prompt = (
            "Voce e o modulo de validacao rapida do NQR.\n"
            "Analise a declaracao do usuario e o fato consolidado informado.\n"
            "Responda apenas com SIM ou NAO indicando se existe contradicao direta."
        )
        user_prompt = (
            f"Fato Consolidado: {fact_text}\n"
            f"Resposta Gerada: {response}\n"
            "Existe contradicao direta? (SIM/NAO)"
        )
        try:
            raw = self._run_chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.0,
            )
            answer = raw.strip().split()[0].lower()
            return answer.startswith("sim")
        except Exception as error:  # noqa: BLE001
            print(f"[NQR] Falha na validacao rapida: {error}")
            return False

    def _register_meta_knowledge(
        self,
        *,
        original_response: str,
        corrected_response: str,
        document: Any,
        dissonance: str,
    ) -> None:
        try:
            payload = {
                "id": str(uuid.uuid4()),
                "tipo": "META_CONHECIMENTO",
                "registrado_em": datetime.now(timezone.utc).isoformat(),
                "resposta_original": original_response,
                "resposta_corrigida": corrected_response,
                "dissonancia": dissonance,
                "fonte_url": self._get_attr(document, "url", default=""),
                "fonte_titulo": self._get_attr(
                    document,
                    "title",
                    default=self._get_attr(document, "titulo", default=""),
                ),
            }
            database.save_meta_knowledge([payload])
        except Exception as error:  # noqa: BLE001
            print(f"[NQR] Falha ao registrar meta-conhecimento: {error}")

    def _estimate_external_confidence(self, document: Any) -> float:
        content = self._extract_document_text(document)
        url = self._get_attr(document, "url", default="Desconhecida")

        system_prompt = (
            "Voce e o modulo de avaliacao externa do NQR. "
            "Atribua uma confianca entre 0.0 e 1.0 ao documento informado, "
            "considerando coerencia, fonte e verificabilidade. "
            "Responda SOMENTE com um numero decimal neste intervalo."
        )
        user_prompt = f"DOCUMENTO:\n{content}\n\nFONTE: {url}"

        try:
            raw = self._run_chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
            )
            return self._parse_confidence_value(raw)
        except Exception as error:  # noqa: BLE001
            print(f"[NQR] Falha ao estimar confianca externa: {error}")
            return 0.0

    def _parse_confidence_value(self, value: str) -> float:
        try:
            parsed = float(value.strip().split()[0])
        except Exception:
            parsed = 0.0
        return max(0.0, min(parsed, 1.0))

    def _run_chat_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        response_format: Dict[str, str] | None = None,
    ) -> str:
        provider = self._pick_provider()
        if provider == "gemini" and genai is not None:
            return self._run_gemini_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )

        client, model = self._get_deepseek_client()
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            response_format=response_format,
        )
        return completion.choices[0].message.content

    def _run_gemini_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> str:
        settings = self._load_settings()
        api_key = (
            settings.ai.google.api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        if not api_key or genai is None:
            client, model = self._get_deepseek_client()
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return completion.choices[0].message.content

        model_name = settings.ai.google.model_name or DEFAULT_GEMINI_MODEL
        try:
            genai.configure(api_key=api_key)
            generation_config = {
                "temperature": temperature,
            }
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt,
            )
            response = model.generate_content(
                user_prompt, generation_config=generation_config
            )
            if hasattr(response, "text") and response.text:
                return response.text
            if response.candidates:
                return response.candidates[0].content.parts[0].text  # type: ignore[index]
            return ""
        except Exception as error:  # noqa: BLE001
            print(
                f"[NQR] Falha na chamada Gemini ({model_name}): {error}. Fallback para DeepSeek."
            )
            client, model = self._get_deepseek_client()
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return completion.choices[0].message.content

    def _pick_provider(self) -> str:
        try:
            settings = self._load_settings()
            if settings.ai.google.enabled:
                key_available = (
                    settings.ai.google.api_key
                    or os.getenv("GEMINI_API_KEY")
                    or os.getenv("GOOGLE_API_KEY")
                )
                if key_available and genai is not None:
                    return "gemini"
            if settings.ai.deepseek.enabled and os.getenv("DEEPSEEK_API_KEY"):
                return "deepseek"
        except Exception as error:  # noqa: BLE001
            print(
                f"[NQR] Aviso: falha ao carregar configuracoes de IA ({error}). Usando DeepSeek."
            )
        return "deepseek"

    def _get_deepseek_client(self) -> tuple[OpenAI, str]:
        if self._deepseek_client is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise RuntimeError("DEEPSEEK_API_KEY nao configurada.")
            self._deepseek_client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com",
            )

        settings = self._load_settings()
        model = settings.ai.deepseek.model_name or DEFAULT_DEEPSEEK_MODEL
        return self._deepseek_client, model

    def _load_settings(self) -> SystemSettings:
        try:
            return database.get_settings()
        except Exception as error:  # noqa: BLE001
            print(
                f"[NQR] Nao foi possivel carregar configuracoes. Usando padrao. Detalhe: {error}"
            )
            return SystemSettings()

    # Attribute helpers ------------------------------------------------
    def _get_attr(self, document: Any, name: str, default: Any = None) -> Any:
        if isinstance(document, dict):
            return document.get(name, default)
        return getattr(document, name, default)

    def _set_attr(self, document: Any, name: str, value: Any) -> None:
        if isinstance(document, dict):
            document[name] = value
        else:
            setattr(document, name, value)

    def _get_numeric_attr(
        self, document: Any, name: str, default: float = 0.0
    ) -> float:
        value = self._get_attr(document, name, default)
        try:
            return float(value)
        except Exception:
            return float(default)

    def _extract_document_text(self, document: Any) -> str:
        candidates = [
            "content",
            "texto",
            "summary",
            "descricao",
            "description",
            "body",
        ]
        for key in candidates:
            value = self._get_attr(document, key)
            if value:
                return str(value)
        return str(document)

    def _is_introspection_query(self, query: str) -> bool:
        lowered = query.lower()
        introspection_signals = (
            "quem e voce",
            "quem eh voce",
            "quem e o nexus",
            "quem eh o nexus",
            "o que voce e",
            "qual e a sua missao",
            "qual eh a sua missao",
            "sua missao",
            "seu proposito",
            "sobre voce",
            "sobre o nexus",
            "identidade do nexus",
            "identidade do sistema",
            "self",
            "modelo voce usa",
            "modelo voce utiliza",
            "seu modelo",
            "sua arquitetura",
            "sua configuracao",
            "meu modelo principal",
            "meu modelo de ia",
            "qual o seu modelo",
            "qual seu modelo",
            "seu orquestrador",
        )
        return any(signal in lowered for signal in introspection_signals)

    @property
    def last_low_confidence(self) -> bool:
        return self._low_confidence_alert
