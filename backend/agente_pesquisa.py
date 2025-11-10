import ast
import json
import os
import traceback
from typing import Any, Dict, List, Sequence, Tuple

from openai import OpenAI

import ferramentas
from agente_nqr import NexusQuantumReasoning
from nexus_graph import NexusGraph


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
    try:
        return NexusGraph.quantum_search(
            query=search_query,
            context_of_use=context_of_use,
        )
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


def _decompose_query(user_query: str) -> List[str]:
    system_prompt = (
        "Você é o Decompositor de Consultas do Nexus. "
        "Transforme a pergunta do usuário em 3 a 5 sub-perguntas de pesquisa independentes. "
        "Retorne APENAS uma lista Python de strings."
    )
    try:
        response = llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=0.2,
        )
        raw_list = response.choices[0].message.content.strip()
        try:
            parsed = json.loads(raw_list)
        except json.JSONDecodeError:
            parsed = ast.literal_eval(raw_list)
        if isinstance(parsed, list):
            cleaned = [str(item).strip() for item in parsed if str(item).strip()]
            return cleaned[:5]
    except Exception as error:  # noqa: BLE001
        print(f"[Orquestrador] Falha ao decompor consulta: {error}")
    return [user_query]


def _synthesize_multi_source(
    user_query: str,
    all_results: List[Dict[str, Any]],
) -> Tuple[str, List[Dict[str, str]]]:
    consolidated_sources: List[Dict[str, str]] = []
    seen_sources = set()
    context_blocks: List[str] = []

    for index, result in enumerate(all_results, start=1):
        context = result.get("context")
        if not context:
            continue
        label = result.get("label") or result.get("sub_query") or f"Fonte {index}"
        context_blocks.append(f"[{label}]\n{context}")
        for source in result.get("sources", []):
            if not source:
                continue
            key = (source.get("title"), source.get("url"))
            if key in seen_sources:
                continue
            seen_sources.add(key)
            consolidated_sources.append(source)

    combined_context = "\n\n".join(context_blocks)
    if not combined_context:
        return (
            "Não consegui reunir contexto suficiente para responder com confiança.",
            consolidated_sources,
        )

    system_prompt = (
        "Você é o Consolidador de Investigação do Nexus. "
        "Sintetize uma resposta abrangente para a pergunta do usuário, utilizando e citando todas as fontes fornecidas. "
        "Mantenha a resposta fluida e informativa."
    )
    user_prompt = (
        f"PERGUNTA DO USUARIO:\n{user_query}\n\n"
        f"CONTEXTOS E FONTES:\n{combined_context}"
    )

    response = llm_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    answer = response.choices[0].message.content.strip()
    return answer, consolidated_sources


def _check_for_hallucination(answer: str, context: str) -> Tuple[bool, str]:
    if not answer or not context:
        return True, "Contexto insuficiente para validacao."

    system_prompt = (
        "Você é o Verificador de Consistência Preditiva do Nexus. Analise se a RESPOSTA "
        "está 100% contida ou inferível a partir do CONTEXTO. "
        "Responda APENAS com um JSON: "
        '{"consistent": true, "reason": "justificativa"}'
    )
    user_prompt = f"RESPOSTA:\n{answer}\n\nCONTEXTO DISPONIVEL:\n{context}"

    try:
        completion = llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = completion.choices[0].message.content
        payload = json.loads(raw)
        consistent = bool(payload.get("consistent", True))
        reason = str(payload.get("reason", "") or "").strip()
        return consistent, reason
    except Exception as error:  # noqa: BLE001
        print(f"[Orquestrador][VCP] Falha ao verificar alucinacao: {error}")
        return True, "Verificacao indisponivel."


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
                "context": "Nenhuma ferramenta disponivel para executar a pesquisa.",
                "sources": [],
                "label": tool_name,
                "sub_query": search_query,
            }
        tool_info = ferramentas.AVAILABLE_TOOLS[fallback_tool]

    raw_result = tool_info["function"](search_query)
    normalized = _normalize_tool_output(raw_result)
    context = normalized["context"]
    sources = normalized["sources"]

    if not context or context.startswith("ERRO"):
        return {
            "context": context or "Nao encontrei informacoes suficientes.",
            "sources": sources,
            "label": f"{tool_name} :: {search_query}",
            "sub_query": search_query,
        }

    return {
        "context": context,
        "sources": sources,
        "label": f"{tool_name} :: {search_query}",
        "sub_query": search_query,
    }


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
    all_results: List[Dict[str, Any]] = []
    reranked_docs: List[Any] = []

    if documents:
        print(f"[Orquestrador] Quantum search retornou {len(documents)} documentos.")
        reranked_docs = nqr.re_rank_by_confidence(documents)
        low_confidence_alert = nqr.last_low_confidence
        context, sources = _serialize_documents(reranked_docs)
        if context:
            label = "Quantum Search (Baixa confiança)" if low_confidence_alert else "Quantum Search"
            all_results.append({"context": context, "sources": sources, "label": label})
        else:
            print("[Orquestrador] Contexto vazio apos reordenacao. Fallback para ferramentas classicas.")

    sub_queries = _decompose_query(user_query)
    if optimized_query not in sub_queries:
        sub_queries = [optimized_query] + sub_queries

    tool_results: List[Dict[str, Any]] = []
    for sub_query in sub_queries:
        tool_result = _execute_tool_strategy(
            tool_name=tool_name,
            search_query=sub_query,
            user_query=user_query,
            context_of_use=context_of_use,
        )
        if not tool_result.get("label"):
            tool_result["label"] = f"Subconsulta: {sub_query}"
        tool_results.append(tool_result)
        if tool_result.get("context"):
            all_results.append(
                {
                    "context": tool_result["context"],
                    "sources": tool_result.get("sources", []),
                    "label": tool_result["label"],
                }
            )

    if not all_results:
        fallback = tool_results[0] if tool_results else None
        if fallback:
            answer = fallback.get("context") or "Não foi possível coletar informações suficientes."
            return {
                "answer": answer,
                "sources": fallback.get("sources", []),
            }
        return {
            "answer": "Não foi possível coletar informações suficientes.",
            "sources": [],
        }

    answer, consolidated_sources = _synthesize_multi_source(user_query, all_results)
    combined_context_text = "\n\n".join(
        entry["context"] for entry in all_results if entry.get("context")
    )
    consistent, reason = _check_for_hallucination(answer, combined_context_text)
    if not consistent:
        print(f"[Orquestrador][VCP] Ajustando resposta consolidada: {reason}")
        augmented_results = all_results + [
            {"context": f"[ALERTA VCP] {reason}", "sources": [], "label": "VCP"}
        ]
        answer, consolidated_sources = _synthesize_multi_source(user_query, augmented_results)

    if reranked_docs:
        answer = nqr.self_correct_rag(answer, reranked_docs)

    return {
        "answer": answer,
        "sources": consolidated_sources,
    }
