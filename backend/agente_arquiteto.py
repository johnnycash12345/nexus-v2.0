import json
import os
from typing import List

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


class ProjectStructure(BaseModel):
    name: str = Field(..., description="Nome curto e técnico para o projeto")
    description: str = Field(..., description="Descrição clara de uma frase do objetivo")
    tech_stack: List[str] = Field(
        ..., description="Lista de 3-5 tecnologias principais (ex: ['React', 'FastAPI', 'Neo4j'])"
    )
    initial_tasks: List[str] = Field(
        ..., description="Lista de 3-5 primeiras tarefas para o MVP"
    )
    mvp_summary: str = Field(
        ..., description="Resumo de 2 parágrafos do que será o MVP funcional"
    )


def structure_idea(raw_idea: str) -> ProjectStructure:
    """Analisa um texto desestruturado (chat ou ideia) e retorna uma estrutura de projeto."""
    print(f"[Agente Arquiteto] Estruturando ideia: {raw_idea[:50]}...")

    system_prompt = (
        "Você é um Arquiteto de Software Sênior. Sua tarefa é ler uma ideia vaga "
        "e transformá-la em um plano de projeto estruturado para um MVP. "
        "Seja técnico, realista e minimalista (foco no MVP). "
        "Retorne APENAS um JSON que siga esta estrutura: "
        "{'name': '...', 'description': '...', 'tech_stack': [], 'initial_tasks': [], 'mvp_summary': '...'}"
    )
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"IDEIA BRUTA:\n{raw_idea}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return ProjectStructure(**data)
    except Exception as error:
        print(f"[Agente Arquiteto] ERRO: {error}")
        return ProjectStructure(
            name="Projeto_Novo",
            description="Ideia importada (precisa de refinamento)",
            tech_stack=["TBD"],
            initial_tasks=["Definir escopo"],
            mvp_summary="Erro ao gerar resumo automático.",
        )
