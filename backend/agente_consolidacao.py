import json
import os
from typing import Dict, List

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def extract_knowledge(text: str) -> List[Dict[str, str]]:
    """Usa o LLM para extrair fatos do texto no formato de triplas: (Sujeito)-[RELACAO]->(Objeto)."""
    print("[Agente Consolidacao] Lendo e extraindo conhecimento...")

    system_prompt = (
        "Voce e um Extrator de Conhecimento do Nexus. Leia atentamente o texto e identifique fatos relevantes.\n"
        "Retorne os fatos como triplas: Sujeito, Predicado (relacao), Objeto.\n"
        "Regras importantes:\n"
        "1. Use relacoes curtas, em CAIXA_ALTA e snake_case (ex: CRIADO_POR, LOCALIZADO_EM, EH_UM, TEM_NOME).\n"
        "2. Se o texto trouxer informacoes em primeira pessoa (\"eu\", \"meu\"), associe-as ao no CREATOR\n"
        "   (exemplo: \"Meu peixe se chama Banguela\" -> {source: 'CREATOR', relationship: 'TEM_PET', target: 'Banguela'}).\n"
        "3. Prefira conceitos concisos para os alvos (ex: 'tecnico de enfermagem', 'Banguela').\n"
        "4. Ignore opinioes ou frases sem conteudo factual.\n"
        "Responda APENAS com um JSON no formato:\n"
        '{ "triples": [{"source": "Python", "relationship": "CRIADO_POR", "target": "Guido van Rossum"}] }\n'
    )
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"TEXTO PARA APRENDER:\n{text}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        triples = data.get("triples", []) if isinstance(data, dict) else []
        print(f"[Agente Consolidacao] Extraiu {len(triples)} novos fatos.")
        return triples
    except Exception as error:
        print(f"[Agente Consolidacao] ERRO ao extrair conhecimento: {error}")
        return []
