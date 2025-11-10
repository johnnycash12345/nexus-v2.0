import json
import os
from typing import Dict, List

from openai import OpenAI
from pydantic import BaseModel, Field

import database
from db_connect import chroma_client

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


class ProjectStructure(BaseModel):
    name: str = Field(..., description="Nome curto e técnico para o projeto")
    description: str = Field(
        ..., description="Descrição clara de uma frase do objetivo"
    )
    tech_stack: List[str] = Field(
        ...,
        description="Lista de 3-5 tecnologias principais (ex: ['React', 'FastAPI', 'Neo4j'])",
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


def manage_chroma_memory(max_documents: int = 1000) -> str:
    """
    Evita que a memoria de curto prazo do ChromaDB cresça indefinidamente.
    """
    try:
        total_documents = 0
        collections = chroma_client.list_collections()
        for collection_info in collections:
            try:
                collection = chroma_client.get_collection(collection_info.name)
            except TypeError:
                collection = chroma_client.get_collection(
                    name=collection_info.name,
                )
            total_documents += collection.count()
    except Exception as error:
        return f"[GMH] Falha ao consultar o ChromaDB: {error}"

    if total_documents <= max_documents:
        return f"[GMH] Memoria atual ({total_documents} documentos) dentro do limite ({max_documents})."

    candidates = database.get_least_activated_documents(limit=100)
    if not candidates:
        return "[GMH] Nenhum documento com baixa ativacao encontrado para arquivar."

    preview_ids = ", ".join(candidates[:5]) + ("..." if len(candidates) > 5 else "")
    system_prompt = (
        "Você é o gestor de memória hierárquica do Nexus. "
        "Explique de forma objetiva qual ação será tomada para otimizar o ChromaDB."
    )
    user_prompt = (
        f"Documentos atuais: {total_documents}\n"
        f"Limite configurado: {max_documents}\n"
        f"Quantidade selecionada para arquivamento: {len(candidates)}\n"
        f"IDs (amostra): {preview_ids}\n"
        "Descreva o plano de arquivamento em 2 frases."
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        plan = response.choices[0].message.content.strip()
    except Exception as error:  # noqa: BLE001
        plan = (
            f"[GMH] Arquivando {len(candidates)} documentos para reduzir o uso do ChromaDB. "
            f"(Falha ao gerar plano detalhado: {error})"
        )

    try:
        database.delete_chroma_documents(candidates)
    except Exception as error:  # noqa: BLE001
        return f"{plan} Contudo, houve erro ao remover documentos: {error}"

    return plan


def incubate_idea(idea_content: str) -> Dict[str, str]:
    """
    Gera entidades-chave para uma nova ideia utilizando DeepSeek.
    """
    system_prompt = (
        "Você é o Incubador de Ideias do Nexus. Analise a ideia e gere três entidades-chave "
        "em JSON estrito: 'objective', 'next_action', 'resources_needed'."
    )
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": idea_content},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        entities = json.loads(response.choices[0].message.content)
        return {
            "objective": str(entities.get("objective", "")).strip(),
            "next_action": str(entities.get("next_action", "")).strip(),
            "resources_needed": str(entities.get("resources_needed", "")).strip(),
        }
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Arquiteto] Falha ao incubar ideia: {error}")
        return {
            "objective": "Refinar o objetivo da ideia.",
            "next_action": "Agendar uma sessão para detalhar a ideia.",
            "resources_needed": "Listar recursos necessários após o refinamento.",
        }


def process_new_idea(idea_content: str) -> None:
    """
    Persiste entidades-chave e cria lembrete proativo.
    """
    entities = incubate_idea(idea_content)
    try:
        database.save_idea_entities(idea_content, entities)
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Arquiteto] Falha ao salvar entidades da ideia: {error}")

    next_action = entities.get("next_action") or "Revisar a ideia incubada."
    try:
        database.create_inbox_item(next_action, "Lembrete Proativo")
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Arquiteto] Falha ao criar lembrete proativo: {error}")
