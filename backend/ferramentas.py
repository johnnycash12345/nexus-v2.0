from __future__ import annotations

import json
import os
from typing import Any, Dict, Tuple, Type

import requests
from duckduckgo_search import DDGS
from pydantic import ValidationError, create_model
from tavily import TavilyClient

import usage_tracker

AVAILABLE_TOOLS: Dict[str, Dict[str, Any]] = {}

TYPE_MAPPING: Dict[str, Type[Any]] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


def register_tool(
    name: str,
    description: str,
    func,
    required_env_var: str | None = None,
    limit_key: str | None = None,
    parameters: Dict[str, Dict[str, Any]] | None = None,
):
    if required_env_var and not os.getenv(required_env_var):
        return

    if limit_key:

        def wrapped_func(*args, **kwargs):
            if not usage_tracker.can_use_api(limit_key):
                print(
                    f"[Tool {name}] BLOQUEADA: limite diario de '{limit_key}' atingido."
                )
                return f"ERRO: limite diario de uso atingido para {limit_key}. Tente novamente amanha."
            usage_tracker.track_usage(limit_key)
            return func(*args, **kwargs)

        final_func = wrapped_func
    else:
        final_func = func

    AVAILABLE_TOOLS[name] = {
        "description": description,
        "function": final_func,
        "parameters": parameters or {},
    }


def get_tool_descriptions() -> Dict[str, str]:
    """
    Retorna descricoes detalhadas das ferramentas (nome, assinatura e parametros).
    """
    descriptions: Dict[str, str] = {}
    for name, data in AVAILABLE_TOOLS.items():
        params = data.get("parameters", {})
        if params:
            signature = []
            details = []
            for param_name, meta in params.items():
                param_type = meta.get("type", "str")
                required = meta.get("required", False)
                signature.append(f"{param_name}: {param_type}{'!' if required else ''}")
                details.append(
                    f"  - {param_name} ({param_type}, {'obrigatorio' if required else 'opcional'}): "
                    f"{meta.get('description', 'Sem descricao')}"
                )
            formatted = (
                f"{name}({', '.join(signature)}) - {data.get('description', 'Sem descricao')}\n"
                + "\n".join(details)
            )
            descriptions[name] = formatted
        else:
            descriptions[name] = (
                f"{name}() - {data.get('description', 'Sem descricao')}"
            )
    return descriptions


def get_tools_prompt() -> str:
    if not AVAILABLE_TOOLS:
        return "FERRAMENTAS DISPONIVEIS:\n- Nenhuma ferramenta ativa."

    lines = ["FERRAMENTAS DISPONIVEIS:"]
    for name, info in AVAILABLE_TOOLS.items():
        params = info.get("parameters") or {}
        if params:
            signature = ", ".join(
                f"{param} ({meta.get('type', 'str')})" for param, meta in params.items()
            )
            lines.append(f"- '{name}({signature})': {info['description']}")
        else:
            lines.append(f"- '{name}': {info['description']}")
    return "\n".join(lines)


def _build_argument_model(tool_name: str):
    tool = AVAILABLE_TOOLS.get(tool_name)
    if not tool:
        raise ValueError(f"Ferramenta '{tool_name}' nao foi registrada.")

    params = tool.get("parameters") or {}
    fields: Dict[str, Tuple[Any, Any]] = {}
    for param_name, meta in params.items():
        type_name = meta.get("type", "str")
        py_type = TYPE_MAPPING.get(type_name, str)
        required = meta.get("required", False)
        default = meta.get("default", None)
        if required:
            fields[param_name] = (py_type, ...)
        else:
            fields[param_name] = (py_type, default)

    if not fields:
        fields["__dummy"] = (str, None)

    model = create_model(f"{tool_name.title()}Arguments", **fields)  # type: ignore[arg-type]
    return model, "__dummy" in fields


def validate_tool_arguments(
    tool_name: str, arguments: Dict[str, Any]
) -> Dict[str, Any]:
    model, has_dummy = _build_argument_model(tool_name)
    cleaned_args = arguments or {}

    try:
        result = model(**cleaned_args)
        data = result.model_dump()
        if has_dummy:
            data.pop("__dummy", None)
        return data
    except ValidationError as error:
        raise ValueError(error.errors()) from error


def _tool_tavily(query: str) -> str:
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        result = client.search(query=query, search_depth="advanced", max_results=5)
        return json.dumps(result.get("results", []))
    except Exception as error:  # noqa: BLE001
        return f"ERRO Tavily: {error}"


register_tool(
    "tavily_search",
    "Use para pesquisas complexas, tecnicas ou cientificas que exigem fontes de alta qualidade.",
    _tool_tavily,
    required_env_var="TAVILY_API_KEY",
    limit_key="tavily",
    parameters={
        "query": {
            "type": "str",
            "required": True,
            "description": "Pergunta completa a ser repassada a API Tavily.",
        },
    },
)


def _tool_nasa(query: str | None = None) -> str:
    try:
        api_key = os.getenv("NASA_API_KEY")
        url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        title = data.get("title", "Sem titulo")
        explanation = data.get("explanation", "Sem descricao")
        image_url = data.get("url", "")
        return f"NASA APOD: {title} - {explanation}\nLink: {image_url}"
    except Exception as error:  # noqa: BLE001
        return f"ERRO NASA: {error}"


register_tool(
    "nasa_search",
    "Use para buscar dados astronomicos ou imagens fornecidas pela NASA.",
    _tool_nasa,
    required_env_var="NASA_API_KEY",
    limit_key="nasa",
    parameters={
        "query": {
            "type": "str",
            "required": False,
            "description": "Tema ou palavra-chave desejada (opcional).",
            "default": None,
        },
    },
)


def _tool_ddg_news(query: str, max_results: int = 5) -> str:
    try:
        results = []
        with DDGS() as ddgs:
            for record in ddgs.news(query, region="br-pt", max_results=max_results):
                results.append(record)
        return json.dumps(results)
    except Exception as error:  # noqa: BLE001
        return f"ERRO DDG: {error}"


register_tool(
    "news_search",
    "Use apenas para noticias recentes, manchetes do dia ou eventos em tempo real.",
    _tool_ddg_news,
    parameters={
        "query": {
            "type": "str",
            "required": True,
            "description": "Assunto ou palavra-chave a ser consultada nas noticias.",
        },
        "max_results": {
            "type": "int",
            "required": False,
            "description": "Numero maximo de resultados (padrao 5).",
            "default": 5,
        },
    },
)
