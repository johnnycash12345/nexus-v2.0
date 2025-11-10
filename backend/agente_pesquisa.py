import json
import os
import traceback
from typing import Any, Dict, List, Sequence, Tuple

from openai import OpenAI

import ferramentas
from agente_nqr import NexusQuantumReasoning

try:  # pragma: no cover - modulo pode nao existir durante desenvolvimento
    from nexus_graph import NexusGraph  # type: ignore
except Exception:  # pragma: no cover
    NexusGraph = None  # type: ignore[assignment]


llm_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

nqr = NexusQuantumReasoning()


def _safe_get(document: Any, key: str, default: Any = None) -> Any:
    if isinstance(document, dict):
        return document.get(key, default)
    return getattr(document, key, default)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _document_text(document: Any) -> str:
    for field in ("content", "texto", "summary", "descricao", "description", "body"):
        value = _safe_get(document, field)
        if value:
            return str(value)
    return str(document)


def _attempt_quantum_search(context_of_use: str, search_query: str) -> List[Any]:
    if NexusGraph is None:
        return []

    try:
        return NexusGraph.quantum_search(  # type: ignore[attr-defined]
            query=search_query,
            context_of_use=context_of_use,
        )
    except TypeError:
        try:
            return NexusGraph.quantum_search(search_query, context_of_use)  # type: ignore[attr-defined]
        except Exception as error:  # noqa: BLE001
            print(f"[Orquestrador] Falha no quantum_search fallback: {error}")
            return []
    except Exception as error:  # noqa: BLE001
        print(f"[Orquestrador] Erro ao consultar NexusGraph.quantum_search: {error}")
        return []


def _serialize_documents(documents: Sequence[Any]) -> Tuple[str, List[Dict[str, str]]]:
    context_lines: List[str] = []
    sources: List[Dict[str, str]] = []

    for index, document in enumerate(documents, start=1):
        title = (
            _safe_get(document, "title")
            or _safe_get(document, "titulo")
            or f"Documento {index}"
        )
        url = _safe_get(document, "url") or ""
        score = _safe_float(
            _safe_get(document, "score_final", _safe_get(document, "confianca_intrinseca", 0.0)),
            default=0.0,
        )
        snippet = _document_text(document)
        context_lines.append(f"[{index}] {title} (score={score:.2f}): {snippet}")
        if url:
            sources.append({"title": str(title), "url": str(url)})

    return "\n".join(context_lines), sources


def _synthesize_answer(
    *,
    user_query: str,
    context: str,
    context_of_use: str,
    low_confidence_alert: bool = False,
) -> str:
    system_prompt = (
        "Voce e o Nexus. Utilize o contexto fornecido pelo NQR e responda de forma direta, "
        "citando fontes quando aplicavel. Considere o contexto de uso informado pelo orquestrador."
    )
    if low_confidence_alert:
        system_prompt += " ALERTA: Informacao com baixa confianca detectada. Avise o usuario sobre a incerteza."
    user_block = (
        f"INTENCAO / CONTEXTO: {context_of_use}\n"
        f"PERGUNTA: {user_query}\n\n"
        f"CONTEXTOS PRIORIZADOS:\n{context}"
    )

    response = llm_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_block},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def _normalize_tool_output(raw_result: Any) -> Dict[str, Any]:
    context_lines: List[str] = []
    sources: List[Dict[str, str]] = []

    if not raw_result:
        return {"context": "", "sources": []}

    if isinstance(raw_result, str):
        try:
            data = json.loads(raw_result)
        except Exception:
            if raw_result.startswith("ERRO"):
                return {"context": raw_result, "sources": []}
            return {"context": raw_result, "sources": []}
    else:
        data = raw_result

    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                context_lines.append(str(item))
                continue
            title = item.get("title", "Sem titulo")
            url = item.get("url", "")
            content = item.get("content", "")
            context_lines.append(f"- [{title}]({url}): {content}")
            if url:
                sources.append({"title": title, "url": url})
        return {"context": "\n".join(context_lines), "sources": sources}

    if isinstance(data, dict):
        context_lines.append(json.dumps(data, ensure_ascii=False))
        title = data.get("title")
        url = data.get("url")
        if title and url:
            sources.append({"title": title, "url": url})
        return {"context": "\n".join(context_lines), "sources": sources}

    return {"context": str(data), "sources": []}


def _choose_fallback_tool() -> str:
    if "tavily_search" in ferramentas.AVAILABLE_TOOLS:
        return "tavily_search"
    if ferramentas.AVAILABLE_TOOLS:
        return next(iter(ferramentas.AVAILABLE_TOOLS.keys()))
    return ""


def _execute_tool_strategy(
    *,
    tool_name: str,
    search_query: str,
    user_query: str,
    context_of_use: str,
) -> Dict[str, Any]:
    tool_info = ferramentas.AVAILABLE_TOOLS.get(tool_name)
    if not tool_info:
        fallback_tool = _choose_fallback_tool()
        print(
            f"[Orquestrador] Ferramenta '{tool_name}' nao encontrada. Usando fallback: {fallback_tool}."
        )
        if not fallback_tool:
            return {
                "answer": "Nenhuma ferramenta disponivel para executar a pesquisa.",
                "sources": [],
            }
        tool_info = ferramentas.AVAILABLE_TOOLS[fallback_tool]

    raw_result = tool_info["function"](search_query)
    normalized = _normalize_tool_output(raw_result)
    context = normalized["context"]
    sources = normalized["sources"]

    if not context or context.startswith("ERRO"):
        return {
            "answer": context or "Nao encontrei informacoes suficientes.",
            "sources": sources,
        }

    try:
        answer = _synthesize_answer(
            user_query=user_query,
            context=context,
            context_of_use=context_of_use,
        )
        answer = nqr.self_correct_rag(answer, [])
    except Exception as error:  # noqa: BLE001
        print(f"[Orquestrador] Erro ao sintetizar (fallback): {error}\n{traceback.format_exc()}")
        return {
            "answer": "Erro ao sintetizar a resposta final.",
            "sources": sources,
        }

    return {"answer": answer, "sources": sources}


def search(user_query: str) -> Dict[str, Any]:
    print(f"[Orquestrador] Recebida missao: {user_query}")

    if not ferramentas.AVAILABLE_TOOLS and NexusGraph is None:
        print("[Orquestrador] Nenhuma ferramenta ou grafo disponivel. Configure as chaves de API.")
        return {
            "answer": "Nenhuma ferramenta de pesquisa esta ativa. Adicione chaves de API ao arquivo .env.",
            "sources": [],
        }

    available_tools = list(ferramentas.AVAILABLE_TOOLS.keys())
    plan = nqr.plan_research_4_0(user_query, available_tools)
    tool_name = plan.get("tool") or _choose_fallback_tool()
    optimized_query = plan.get("search_query", user_query)
    context_of_use = plan.get("context_of_use", "Pesquisa Geral")

    print(
        f"[Orquestrador] Plano NQR -> ferramenta: {tool_name}, contexto: '{context_of_use}', busca: '{optimized_query}'"
    )

    documents = _attempt_quantum_search(context_of_use, optimized_query)

    if documents:
        print(f"[Orquestrador] Quantum search retornou {len(documents)} documentos.")
        reranked_docs = nqr.re_rank_by_confidence(documents)
        low_confidence_alert = nqr.last_low_confidence
        context, sources = _serialize_documents(reranked_docs)

        if context:
            try:
                answer = _synthesize_answer(
                    user_query=user_query,
                    context=context,
                    context_of_use=context_of_use,
                    low_confidence_alert=low_confidence_alert,
                )
            except Exception as error:  # noqa: BLE001
                print(f"[Orquestrador] Erro ao sintetizar com documentos do grafo: {error}")
                return {
                    "answer": "Erro ao sintetizar a resposta final.",
                    "sources": sources,
                }

            corrected = nqr.self_correct_rag(answer, reranked_docs)
            return {
                "answer": corrected,
                "sources": sources,
            }

        print("[Orquestrador] Contexto vazio apos reordenacao. Fallback para ferramentas classicas.")

    return _execute_tool_strategy(
        tool_name=tool_name,
        search_query=optimized_query,
        user_query=user_query,
        context_of_use=context_of_use,
    )
