from __future__ import annotations

import json
import os
import socket
from typing import Any, Dict, List, Tuple

from openai import OpenAI

import agente_guardiao
import ferramentas
import database
from models import AISettings, OperationMode

# Clientes pre-configurados
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

META_PROMPT_TASK = "CLASSIFICACAO_INTENCAO"
DEFAULT_CLASSIFIER_PROMPT_TEMPLATE = (
    "Voce e o Cerebro Central do Nexus. Analise o historico e determine a intencao, "
    "a complexidade e a confianca do pedido atual.\n"
    "Historico Recente:\n{{HISTORY}}\n\n"
    "Pergunta Atual: {{QUESTION}}\n"
        "Responda ESTRITAMENTE com o seguinte JSON:\n"
        "{\n"
        '  "intent": "NomeDaCategoria",\n'
        '  "complexity": "Baixo|Médio|Alto",\n'
        '  "confidence": 0.0\n'
        "}\n"
        "Intencoes permitidas: 'Noticias', 'Pesquisa Profunda', 'Lembrete', 'Projeto', "
        "'Nota Simples', 'Chat Pessoal', 'Código', 'Arquitetura', 'Ideia'.\n"
        "Nao adicione texto extra. 'confidence' deve ser um numero decimal entre 0.0 e 1.0."
    )


def has_internet(timeout: int = 3) -> bool:
    """Verifica conectividade basica com a internet."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False


def _get_deepseek_model_name(complexity: str) -> str:
    """
    Retorna o modelo DeepSeek mais adequado conforme a complexidade informada.
    """
    normalized = (complexity or "").strip().lower()
    normalized = normalized.replace("é", "e")
    if normalized == "baixo":
        return "deepseek-light"
    return "deepseek-chat"


def get_best_model_for_task(
    task_type: str,
    settings: AISettings,
    complexity: str | None = None,
) -> Tuple[str, str | None]:
    """
    Decide qual IA usar com base no modo de operacao e no tipo de tarefa.
    """
    complexity_hint = (complexity or "").strip()

    if settings.mode == OperationMode.OFFLINE or (
        settings.fallback_enabled and not has_internet()
    ):
        print("[Roteador] Modo Offline ativo. Usando Ollama.")
        return "ollama", settings.ollama_model

    if settings.mode == OperationMode.TURBO:
        if task_type == "reasoning":
            return "openai", settings.openai.model_name
        if task_type == "search":
            return "perplexity", settings.perplexity.model_name
        return "openai", settings.openai.model_name

    if settings.mode == OperationMode.BALANCED:
        if task_type == "complex_reasoning":
            return "openai", settings.openai.model_name
        if settings.deepseek.enabled:
            selected_model = _get_deepseek_model_name(complexity_hint or "")
            if selected_model == "deepseek-chat":
                selected_model = settings.deepseek.model_name or selected_model
            elif selected_model == "deepseek-light":
                light_override = os.getenv("DEEPSEEK_LIGHT_MODEL")
                if light_override:
                    selected_model = light_override
                else:
                    selected_model = settings.deepseek.model_name or "deepseek-chat"
            return "deepseek", selected_model
        return "ollama", settings.ollama_model

    if settings.mode == OperationMode.ECONOMIC:
        if settings.deepseek.enabled:
            selected_model = _get_deepseek_model_name(complexity_hint or "")
            if selected_model == "deepseek-chat":
                selected_model = settings.deepseek.model_name or selected_model
            elif selected_model == "deepseek-light":
                light_override = os.getenv("DEEPSEEK_LIGHT_MODEL")
                if light_override:
                    selected_model = light_override
                else:
                    selected_model = settings.deepseek.model_name or "deepseek-chat"
            return "deepseek", selected_model
        return "ollama", settings.ollama_model

    return "ollama", settings.ollama_model


def _apply_prompt_template(
    template: str,
    history_text: str,
    question: str,
) -> str:
    prompt = template or DEFAULT_CLASSIFIER_PROMPT_TEMPLATE
    if "{{HISTORY}}" in prompt:
        prompt = prompt.replace("{{HISTORY}}", history_text)
    else:
        prompt = f"{prompt}\n\nHistorico Recente:\n{history_text}"

    if "{{QUESTION}}" in prompt:
        prompt = prompt.replace("{{QUESTION}}", question)
    else:
        prompt = f"{prompt}\n\nPergunta Atual: {question}"

    return prompt


def _handle_prompt_failure(template_used: str, failure_result: str) -> None:
    if not template_used or not failure_result:
        return
    try:
        optimized_prompt = agente_guardiao.optimize_prompt(template_used, failure_result)
        optimized_prompt = optimized_prompt.strip()
        if optimized_prompt and optimized_prompt != template_used.strip():
            database.save_meta_prompt(META_PROMPT_TASK, optimized_prompt)
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Central] Falha ao otimizar prompt: {error}")


def _load_ai_settings() -> AISettings:
    try:
        return database.get_settings().ai
    except Exception as error:  # noqa: BLE001
        print(f"[Roteador] Erro ao carregar configuracoes. Usando padrao. Detalhe: {error}")
        return AISettings()


def _classify_with_deepseek(
    user_content: str,
    model_name: str | None,
    system_prompt: str,
) -> str:
    response = deepseek_client.chat.completions.create(
        model=model_name or "deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=50,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()


def _classify_with_openai(
    user_content: str,
    model_name: str | None,
    api_key: str | None,
    system_prompt: str,
) -> str | None:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        print("[Agente Central] OPENAI_API_KEY nao configurada. Fallback para DeepSeek.")
        return None

    openai_client = OpenAI(api_key=key)
    response = openai_client.chat.completions.create(
        model=model_name or "gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=50,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()


def generate_diagnostic_message(failed_services: Dict[str, str]) -> str:
    """
    Produz uma mensagem proativa sobre servicos indisponiveis.
    """
    if not failed_services:
        return "Todos os serviços operacionais."

    summary_lines = [f"- {name}: {reason}" for name, reason in failed_services.items()]
    summary_text = "\n".join(summary_lines)
    system_prompt = (
        "Voce e o supervisor de infraestrutura do Nexus. Gere uma mensagem concisa "
        "em portugues explicando o impacto dos servicos indisponiveis e sugerindo "
        "acoes imediatas."
    )
    user_prompt = (
        "Servicos com falha detectados:\n"
        f"{summary_text}\n\n"
        "Produza uma mensagem curta (3 frases no maximo) para o operador."
    )

    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        message = response.choices[0].message.content.strip()
        return message or f"Falhas detectadas: {summary_text}"
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Central] Falha ao gerar mensagem de diagnostico: {error}")
        return f"Falhas detectadas: {summary_text}"


def orchestrate_tool_use(
    user_query: str,
    available_tools: Dict[str, str],
) -> Dict[str, Any]:
    """
    Decide qual ferramenta deve ser usada e com quais argumentos.
    """
    if not available_tools:
        return {"tool_needed": False, "tool_name": None, "arguments": {}}

    tool_lines = "\n".join(
        f"- {name}: {description}" for name, description in available_tools.items()
    )
    system_prompt = (
        "Você é o Orquestrador de Ferramentas do Nexus. "
        "Analise a pergunta do usuário e decida se alguma ferramenta precisa ser acionada. "
        "Sempre responda EXCLUSIVAMENTE com JSON no formato:\n"
        "{\n"
        '  "tool_needed": true|false,\n'
        '  "tool_name": "nome_da_ferramenta",\n'
        '  "arguments": {"param": "valor"}\n'
        "}\n"
        "Ferramentas disponíveis:\n"
        f"{tool_lines}"
    )

    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        payload = json.loads(response.choices[0].message.content)
        payload.setdefault("tool_needed", False)
        payload.setdefault("tool_name", None)
        payload.setdefault("arguments", {})
        return payload
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Central] Falha ao orquestrar ferramentas: {error}")
        return {"tool_needed": False, "tool_name": None, "arguments": {}}


def _heuristic_classification(
    user_content: str,
    conversation_history: List[Dict[str, str]] | None = None,
) -> str:
    lowered_user = user_content.lower()
    lowered_history = ""
    if conversation_history:
        history_contents = " ".join(
            message.get("content", "") for message in conversation_history[-5:]
        )
        lowered_history = history_contents.lower()

    def _contains_any(text: str, keywords: List[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    combined_text = f"{lowered_user} {lowered_history}"

    if _contains_any(
        combined_text,
        ["noticias", "noticias", "ultimas", "novidades", "aconteceu", "breaking"],
    ):
        return "Noticias"

    if _contains_any(
        combined_text,
        ["pesquisar", "explique", "o que e", "como funciona", "analise", "por que"],
    ):
        return "Pesquisa Profunda"

    if _contains_any(
        combined_text,
        ["amanha", "lembre", "lembrete", "no dia", "agenda", "na sexta", "me avise"],
    ):
        return "Lembrete"

    if "projeto" in combined_text or "mvp" in combined_text or "planejar" in combined_text:
        return "Projeto"

    if _contains_any(
        combined_text,
        [
            "escreva codigo",
            "escreva código",
            "crie funcao",
            "crie função",
            "bug",
            "refatore",
            "python",
            "javascript",
            "html",
            "css",
            "typescript",
        ],
    ):
        return "Código"

    if _contains_any(
        combined_text,
        [
            "planejamento",
            "estrutura",
            "diagrama",
            "servicos",
            "serviços",
            "infraestrutura",
            "microsservicos",
            "microsserviços",
        ],
    ):
        return "Arquitetura"

    if _contains_any(
        combined_text,
        ["oi", "ola", "como vai", "tudo bem", "conversar", "bate papo"],
    ):
        return "Chat Pessoal"

    if _contains_any(
        combined_text,
        ["ideia", "pensei em", "brainstorm", "conceito"],
    ):
        return "Ideia"

    return "Nota Simples"


def _build_history_prompt(conversation_history: List[Dict[str, str]] | None) -> str:
    if not conversation_history:
        return "Nenhum historico disponivel."

    recent_messages = conversation_history[-10:]
    lines: List[str] = []
    for message in recent_messages:
        role = message.get("role", "desconhecido")
        content = message.get("content", "")
        lines.append(f"{role.upper()}: {content}")
    return "\n".join(lines)


def classify_intent(
    user_content: str,
    conversation_history: List[Dict[str, str]] | None,
) -> Tuple[str, Dict[str, Any] | None]:
    print(f"[Agente Central] Analisando intencao: '{user_content}'")
    settings = _load_ai_settings()
    provider, model_name = get_best_model_for_task("reasoning", settings)
    print(f"[Roteador] Provider selecionado: {provider} (modelo: {model_name})")

    conversation_history = conversation_history or []
    history_text = _build_history_prompt(conversation_history)
    meta_prompt_template = database.get_meta_prompt(META_PROMPT_TASK)
    prompt_template = meta_prompt_template or DEFAULT_CLASSIFIER_PROMPT_TEMPLATE
    system_prompt = _apply_prompt_template(prompt_template, history_text, user_content)

    try:
        classification_payload: str | None
        if provider == "deepseek":
            classification_payload = _classify_with_deepseek(
                user_content,
                model_name,
                system_prompt,
            )
        elif provider == "openai":
            classification_payload = _classify_with_openai(
                user_content,
                model_name,
                settings.openai.api_key,
                system_prompt,
            )
            if classification_payload is None:
                classification_payload = _classify_with_deepseek(
                    user_content,
                    settings.deepseek.model_name,
                    system_prompt,
                )
        elif provider == "ollama":
            print("[Agente Central] Utilizando heuristica local (modo offline/economico).")
            heuristic_intent = _heuristic_classification(
                user_content,
                conversation_history,
            )
            return heuristic_intent, None
        else:
            print(
                f"[Agente Central] Provedor '{provider}' ainda nao suportado. Fallback para DeepSeek."
            )
            classification_payload = _classify_with_deepseek(
                user_content,
                settings.deepseek.model_name,
                system_prompt,
            )

        if not classification_payload:
            raise ValueError("Resposta vazia do classificador remoto.")

        try:
            result = json.loads(classification_payload)
        except json.JSONDecodeError as error:
            print(f"[Agente Central] JSON invalido recebido: {error}. Fallback heuristico.")
            _handle_prompt_failure(prompt_template, f"JSON invalido: {error}")
            heuristic_intent = _heuristic_classification(user_content, conversation_history)
            return heuristic_intent, None

        classified_intent = str(result.get("intent") or "").strip()
        complexity = str(result.get("complexity") or "").strip()
        raw_confidence = result.get("confidence", 0.0)
        try:
            confidence = float(raw_confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        if not classified_intent:
            raise ValueError("Intent vazia retornada pelo classificador.")

        provider, model_name = get_best_model_for_task(
            "reasoning",
            settings,
            complexity,
        )
        print(
            "[Roteador] Ajuste dinamico pelo RMD: "
            f"provider={provider} model={model_name} complexidade='{complexity or 'desconhecida'}'"
        )

        tool_payload: Dict[str, Any] | None = None

        if classified_intent in ("Pesquisa Profunda", "Chat Pessoal"):
            try:
                available_tool_descriptions = ferramentas.get_tool_descriptions()
                plan = orchestrate_tool_use(user_content, available_tool_descriptions)
                tool_payload = plan
                if plan.get("tool_needed"):
                    print(f"[Agente Central] Orquestrador solicitou ferramenta: {plan}")
                    return "Executar Ferramenta", plan
            except Exception as error:  # noqa: BLE001
                print(f"[Agente Central] Falha ao orquestrar ferramenta: {error}")

        if confidence < 0.6:
            classified_intent = "Introspecção"

        if classified_intent == "Projeto" and complexity.lower() == "alto":
            classified_intent = "Arquitetura"

        valid_intents = [
            "Noticias",
            "Pesquisa Profunda",
            "Lembrete",
            "Projeto",
            "Código",
            "Arquitetura",
            "Ideia",
            "Introspecção",
            "Nota Simples",
            "Chat Pessoal",
        ]
        for intent in valid_intents:
            if intent.lower() in classified_intent.lower():
                print(
                    f"[Agente Central] Intencao detectada: {intent} "
                    f"(conf: {confidence:.2f}, complexidade: {complexity})"
                )
                return intent, tool_payload

        print(
            f"[Agente Central] Resultado fora do padrao ('{classified_intent}'). Retornando 'Nota Simples'."
        )
        _handle_prompt_failure(
            prompt_template,
            f"Classificacao invalida recebida: {classified_intent}",
        )
        return "Nota Simples", tool_payload
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Central] ERRO: {error}. Fallback heuristico.")
        _handle_prompt_failure(prompt_template, str(error))
        heuristic_intent = _heuristic_classification(user_content, conversation_history)
        return heuristic_intent, None
