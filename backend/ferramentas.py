import json
import os
from typing import Any, Dict

import requests
from tavily import TavilyClient
from ddgs import DDGS

import usage_tracker

AVAILABLE_TOOLS: Dict[str, Dict[str, Any]] = {}


def register_tool(
    name: str,
    description: str,
    func,
    required_env_var: str | None = None,
    limit_key: str | None = None,
    parameters: Dict[str, str] | None = None,
):
    if required_env_var and not os.getenv(required_env_var):
        return

    if limit_key:
        def wrapped_func(*args, **kwargs):
            if not usage_tracker.can_use_api(limit_key):
                print(f"[Tool {name}] BLOQUEADA: Limite diario de '{limit_key}' atingido.")
                return f"ERRO: Limite diario de uso atingido para {limit_key}. Tente novamente amanha."
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
    Retorna descrições legíveis das ferramentas para o DeepSeek.
    """
    descriptions: Dict[str, str] = {}
    for name, data in AVAILABLE_TOOLS.items():
        params = data.get("parameters", {})
        if params:
            signature = ", ".join(params.keys())
            params_details = "; ".join(f"{param}: {desc}" for param, desc in params.items())
            formatted = (
                f"{name}({signature}) - {data.get('description', 'Sem descrição')} "
                f"Parâmetros: {params_details}"
            )
        else:
            formatted = f"{name}() - {data.get('description', 'Sem descrição')}"
        descriptions[name] = formatted
    return descriptions


def _tool_tavily(query: str) -> str:
    try:
        client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
        result = client.search(query=query, search_depth='advanced', max_results=5)
        return json.dumps(result.get('results', []))
    except Exception as error:
        return f'ERRO Tavily: {error}'


register_tool(
    'tavily_search',
    'Use para pesquisas complexas, tecnicas ou cientificas que exigem fontes de alta qualidade.',
    _tool_tavily,
    required_env_var='TAVILY_API_KEY',
    limit_key='tavily',
    parameters={
        "query": "Pergunta ou instrução detalhada para a API Tavily (str, obrigatório)."
    },
)


def _tool_nasa(query: str) -> str:
    try:
        api_key = os.getenv('NASA_API_KEY')
        url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}'
        response = requests.get(url, timeout=10)
        data = response.json()
        title = data.get('title', 'Sem titulo')
        explanation = data.get('explanation', 'Sem descricao')
        image_url = data.get('url', '')
        return f'NASA APOD: {title} - {explanation}\nLink: {image_url}'
    except Exception as error:
        return f'ERRO NASA: {error}'


register_tool(
    'nasa_search',
    'Use para buscar dados astronomicos ou imagens fornecidas pela NASA.',
    _tool_nasa,
    required_env_var='NASA_API_KEY',
    limit_key='nasa',
    parameters={
        "query": "Tema ou palavra-chave de astronomia desejada (str, opcional; por padrão retorna o APOD do dia)."
    },
)


def _tool_ddg_news(query: str) -> str:
    try:
        results = []
        with DDGS() as ddgs:
            for record in ddgs.news(query, region='br-pt', max_results=5):
                results.append(record)
        return json.dumps(results)
    except Exception as error:
        return f'ERRO DDG: {error}'


register_tool(
    'news_search',
    'Use apenas para noticias recentes, manchetes do dia ou eventos em tempo real.',
    _tool_ddg_news,
    parameters={
        "query": "Assunto ou palavra-chave a ser consultada nas notícias (str, obrigatório)."
    },
)


def get_tools_prompt() -> str:
    if not AVAILABLE_TOOLS:
        return 'FERRAMENTAS DISPONIVEIS:\n- Nenhuma ferramenta ativa.'

    lines = ['FERRAMENTAS DISPONIVEIS:']
    for name, data in AVAILABLE_TOOLS.items():
        params = data.get("parameters") or {}
        if params:
            param_list = "; ".join(f"{param}" for param in params.keys())
            lines.append(f"- '{name}({param_list})': {data['description']}")
        else:
            lines.append(f"- '{name}': {data['description']}")
    return '\n'.join(lines)

