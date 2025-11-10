from __future__ import annotations

import os
import socket
from typing import Dict, List, Tuple

from openai import OpenAI

import database
from models import AISettings, OperationMode

# Clientes pre-configurados
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def has_internet(timeout: int = 3) -> bool:
    """Verifica conectividade basica com a internet."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False


def get_best_model_for_task(
    task_type: str,
    settings: AISettings,
) -> Tuple[str, str | None]:
    """
    Decide qual IA usar com base no modo de operacao e no tipo de tarefa.
    """
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
            return "deepseek", settings.deepseek.model_name
        return "ollama", settings.ollama_model

    if settings.mode == OperationMode.ECONOMIC:
        if settings.deepseek.enabled:
            return "deepseek", settings.deepseek.model_name
        return "ollama", settings.ollama_model

    return "ollama", settings.ollama_model


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
    )
    return response.choices[0].message.content.strip()


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
        ["oi", "ola", "como vai", "tudo bem", "conversar", "bate papo"],
    ):
        return "Chat Pessoal"

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
) -> str:
    print(f"[Agente Central] Analisando intencao: '{user_content}'")
    settings = _load_ai_settings()
    provider, model_name = get_best_model_for_task("reasoning", settings)
    print(f"[Roteador] Provider selecionado: {provider} (modelo: {model_name})")

    conversation_history = conversation_history or []
    history_text = _build_history_prompt(conversation_history)
    system_prompt = (
        "Voce e o Cerebro Central do Nexus. Classifique a intencao do usuario com base no historico abaixo. "
        "Responda APENAS com o nome da categoria.\n"
        f"Historico Recente:\n{history_text}\n\n"
        f"Pergunta Atual: {user_content}\n"
        "Categorias disponiveis: 'Noticias', 'Pesquisa Profunda', 'Lembrete', 'Projeto', 'Nota Simples', 'Chat Pessoal'."
    )

    try:
        if provider == "deepseek":
            classified_intent = _classify_with_deepseek(
                user_content,
                model_name,
                system_prompt,
            )
        elif provider == "openai":
            classified_intent = _classify_with_openai(
                user_content,
                model_name,
                settings.openai.api_key,
                system_prompt,
            )
            if classified_intent is None:
                classified_intent = _classify_with_deepseek(
                    user_content,
                    settings.deepseek.model_name,
                    system_prompt,
                )
        elif provider == "ollama":
            print("[Agente Central] Utilizando heuristica local (modo offline/economico).")
            classified_intent = _heuristic_classification(
                user_content,
                conversation_history,
            )
        else:
            print(
                f"[Agente Central] Provedor '{provider}' ainda nao suportado. Fallback para DeepSeek."
            )
            classified_intent = _classify_with_deepseek(
                user_content,
                settings.deepseek.model_name,
                system_prompt,
            )

        valid_intents = [
            "Noticias",
            "Pesquisa Profunda",
            "Lembrete",
            "Projeto",
            "Nota Simples",
            "Chat Pessoal",
        ]
        for intent in valid_intents:
            if intent.lower() in classified_intent.lower():
                print(f"[Agente Central] Intencao detectada: {intent}")
                return intent

        print(
            f"[Agente Central] Resultado fora do padrao ('{classified_intent}'). Retornando 'Nota Simples'."
        )
        return "Nota Simples"
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Central] ERRO: {error}. Fallback heuristico.")
        return _heuristic_classification(user_content, conversation_history)
