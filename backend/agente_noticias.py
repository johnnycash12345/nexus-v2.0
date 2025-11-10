import os
from datetime import datetime
from typing import Dict, List

from duckduckgo_search import DDGS
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def search_news(topic: str) -> dict:
    """Busca noticias recentes e usa IA para gerar um resumo explicativo."""
    print(f"[Agente Noticias] Buscando ultimas noticias sobre: '{topic}'...")

    news_results: List[str] = []
    try:
        with DDGS() as ddgs:
            for result in ddgs.news(
                topic,
                region="br-pt",
                safesearch="off",
                max_results=5,
            ):
                news_results.append(
                    "- Título: {title}\n"
                    "  Fonte: {source}\n"
                    "  Data: {date}\n"
                    "  Link: {url}\n"
                    "  Snippet: {body}".format(
                        title=result.get("title", "Sem título"),
                        source=result.get("source", "Desconhecida"),
                        date=result.get("date", datetime.now().isoformat()),
                        url=result.get("url", ""),
                        body=result.get("body", ""),
                    )
                )

        if not news_results:
            return {
                "answer": f"Nao encontrei noticias recentes sobre '{topic}'.",
                "sources": [],
            }

        print(
            f"[Agente Noticias] Encontradas {len(news_results)} noticias. Lendo e sintetizando..."
        )
        raw_news_text = "\n\n".join(news_results)

        system_prompt = (
            "Voce e um Jornalista Pessoal IA. Sua funcao e ler as manchetes brutas fornecidas "
            "e criar um resumo coeso, informativo e facil de entender para o usuario. "
            "Se as noticias estiverem em outro idioma, TRADUZA para Portugues do Brasil. "
            "Se o assunto for complexo, explique de forma simples o contexto. "
            "Nao invente noticias, use apenas o que foi fornecido no texto bruto."
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"NOTICIAS BRUTAS:\n{raw_news_text}"},
            ],
            temperature=0.2,
        )

        summary = response.choices[0].message.content
        formatted_sources: List[Dict[str, str]] = []
        for item in news_results:
            title = item.split("\n")[0].replace("- Título: ", "")
            link_part = [
                line for line in item.split("\n") if line.strip().startswith("Link: ")
            ]
            url = link_part[0].replace("Link: ", "").strip() if link_part else ""
            formatted_sources.append({"title": title, "url": url})

        return {
            "answer": summary,
            "sources": formatted_sources,
        }
    except Exception as error:
        print(f"[Agente Noticias] ERRO: {error}")
        return {"answer": "Erro ao processar noticias.", "sources": []}
