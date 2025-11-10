import datetime


def execute_task(item_type: str, item_content: str) -> str:
    """
    Mock executor agent that records requested actions in a persistent log.
    """
    print(f"[Agente Executor] Recebida tarefa: {item_type} - {item_content}")

    log_message = f"[{datetime.datetime.now().isoformat()}] - TAREFA EXECUTADA:\n"
    status_report = ""

    if "Lembrete" in item_type or "Chat Pessoal" in item_type:
        log_message += (
            f"  Tipo: Lembrete\n"
            f"  Conteúdo: {item_content}\n"
        )
        status_report = (
            f"Entendido. O lembrete '{item_content}' foi registrado com sucesso."
        )
    elif "Projeto" in item_type:
        log_message += (
            f"  Tipo: Projeto\n"
            f"  Conteúdo: {item_content}\n"
            f"  Ação: Iniciando pesquisa de viabilidade (simulado).\n"
        )
        status_report = (
            "Confirmado. Iniciei a pesquisa de viabilidade para o projeto. "
            "Acompanhe na aba 'Timeline'."
        )
    else:
        log_message += (
            f"  Tipo: {item_type}\n"
            f"  Conteúdo: {item_content}\n"
        )
        status_report = (
            f"Sua nota '{item_content}' foi processada pelo Agente Executor."
        )

    try:
        with open("executor_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(log_message + "--------------------------------------------------\n")
        print("[Agente Executor] Tarefa registrada em executor_log.txt")
    except Exception as error:
        print(f"[Agente Executor] ERRO ao escrever no log: {error}")
        return f"Ocorreu um erro ao tentar executar a tarefa: {error}"

    return status_report
