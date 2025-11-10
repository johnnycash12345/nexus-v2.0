import json
import os
import requests
from tavily import TavilyClient
from ddgs import DDGS

import usage_tracker

AVAILABLE_TOOLS = {}


def register_tool(name, description, func, required_env_var=None, limit_key=None):
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
        'description': description,
        'function': final_func,
    }


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
)


def get_tools_prompt() -> str:
    if not AVAILABLE_TOOLS:
        return 'FERRAMENTAS DISPONIVEIS:\n- Nenhuma ferramenta ativa.'

    lines = ['FERRAMENTAS DISPONIVEIS:']
    for name, data in AVAILABLE_TOOLS.items():
        lines.append(f"- '{name}': {data['description']}")
    return '\n'.join(lines)

