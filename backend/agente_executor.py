import datetime
import os
import shlex
import subprocess
from typing import Any, Dict, List

from openai import OpenAI

import ferramentas
from agente_nqr import NexusQuantumReasoning

llm_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
nqr = NexusQuantumReasoning()
ALLOWED_COMMANDS = {
    "ls",
    "pwd",
    "whoami",
    "echo",
    "dir",
    "cat",
    "type",
}


def _is_command_allowed(command: str) -> bool:
    if not command:
        return False
    if any(token in command for token in ["&&", "||", ";", "|"]):
        return False
    try:
        first_token = shlex.split(command)[0].lower()
    except ValueError:
        return False
    return first_token in ALLOWED_COMMANDS


def _collect_current_state() -> str:
    cwd = os.getcwd()
    try:
        files = os.listdir(cwd)
    except Exception as error:
        files = [f"# ERRO AO LISTAR DIRETORIO: {error}"]

    env_snapshot = {
        key: os.environ.get(key, "")
        for key in ["USER", "USERNAME", "SHELL", "OS", "PATH", "VIRTUAL_ENV"]
        if os.environ.get(key)
    }
    state_lines = [
        f"DIRETORIO_ATUAL: {cwd}",
        f"ARQUIVOS({len(files)}): {', '.join(sorted(files)[:50])}",
        f"AMBIENTE: {env_snapshot}",
    ]
    return "\n".join(state_lines)


def simulate_command(command: str, current_state: str) -> str:
    """
    Consulta o Motor de Simulação de Realidade (DeepSeek) antes da execução real.
    """
    system_prompt = (
        "Você é o Motor de Simulação de Realidade do Nexus. "
        "Simule a execução do comando no estado atual do sistema. "
        "Retorne APENAS o resultado exato que o terminal ou navegador retornaria."
    )
    if not _is_command_allowed(command):
        return "Comando bloqueado pela politica de segurança do executor."

    user_prompt = (
        f"ESTADO ATUAL:\n{current_state}\n\n"
        f"COMANDO A SIMULAR:\n{command}"
    )
    try:
        response = llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as error:  # noqa: BLE001
        print(f"[Agente Executor] Falha ao simular comando: {error}")
        return f"# ERRO NA SIMULACAO: {error}"


def _run_command(command: str) -> str:
    if not _is_command_allowed(command):
        raise ValueError("Comando não permitido pelo executor seguro.")

    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=90,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            error_text = completed.stderr.strip()
            raise RuntimeError(error_text or output or f"Retorno {completed.returncode} sem saída")
        return output or "(comando executado sem saída)"
    except ValueError:
        raise
    except Exception as error:  # noqa: BLE001
        raise RuntimeError(f"Erro ao executar comando: {error}") from error


def _looks_like_command(item_type: str, item_content: str) -> bool:
    keywords = ["comando", "execucao", "shell", "terminal", "script"]
    lowered_type = (item_type or "").lower()
    if any(keyword in lowered_type for keyword in keywords):
        return True
    content = (item_content or "").strip()
    return bool(content.split() and content.split()[0] in {"python", "pip", "npm", "node", "git", "ls", "cd", "bash", "docker", "make"})


def execute_task(item_type: str, item_content: str) -> str:
    """
    Executor com Motor de Simulação de Realidade (MSR) integrado.
    """
    print(f"[Agente Executor] Recebida tarefa: {item_type} - {item_content}")

    if _looks_like_command(item_type, item_content):
        command = (item_content or "").strip()
        if not command:
            return "Nenhum comando fornecido para execução."

        current_state = _collect_current_state()
        simulated_result = simulate_command(command, current_state)

        task_descriptor: Dict[str, str] = {
            "type": item_type,
            "command": command,
            "state": current_state,
        }
        replanning = nqr.predictive_replan(task_descriptor, simulated_result)
        command_to_execute = command
        replanning_notes: List[str] = []

        if replanning and replanning.get("should_replan"):
            new_command = replanning.get("new_command") or command
            replanning_notes.append(replanning.get("message", "Plano ajustado pelo NQR."))
            command_to_execute = new_command

        try:
            real_result = _run_command(command_to_execute)
        except ValueError as error:
            return f"Comando bloqueado: {error}"
        except RuntimeError as error:
            return f"Falha ao executar comando real: {error}"

        log_message = (
            f"[{datetime.datetime.now().isoformat()}] - EXECUCAO DE COMANDO\n"
            f"  Tipo: {item_type}\n"
            f"  Comando original: {command}\n"
            f"  Comando executado: {command_to_execute}\n"
            f"  Simulado:\n{simulated_result}\n"
            f"  Resultado real:\n{real_result}\n"
        )
        if replanning_notes:
            log_message += f"  Observacoes NQR: {' | '.join(replanning_notes)}\n"

        try:
            with open("executor_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(log_message + "--------------------------------------------------\n")
        except Exception as error:  # noqa: BLE001
            print(f"[Agente Executor] ERRO ao escrever no log: {error}")

        human_message = (
            f"Comando executado após simulação.\n"
            f"Simulado: {simulated_result}\n"
            f"Resultado real: {real_result}"
        )
        if replanning_notes:
            human_message = (
                "O NQR ajustou o plano antes da execução.\n"
                + "\n".join(replanning_notes)
                + f"\nResultado final: {real_result}"
            )
        return human_message

    # Fluxo legado para lembretes/projetos/notas
    log_message = f"[{datetime.datetime.now().isoformat()}] - TAREFA EXECUTADA:\n"
    if "Lembrete" in item_type or "Chat Pessoal" in item_type:
        log_message += (
            f"  Tipo: Lembrete\n"
            f"  Conteúdo: {item_content}\n"
        )
        status_report = f"Entendido. O lembrete '{item_content}' foi registrado com sucesso."
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
        status_report = f"Sua nota '{item_content}' foi processada pelo Agente Executor."

    try:
        with open("executor_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(log_message + "--------------------------------------------------\n")
        print("[Agente Executor] Tarefa registrada em executor_log.txt")
    except Exception as error:
        print(f"[Agente Executor] ERRO ao escrever no log: {error}")
        return f"Ocorreu um erro ao tentar executar a tarefa: {error}"

    return status_report


def execute_dynamic_tool(tool_name: str, arguments: Dict[str, Any] | None = None) -> str:
    """
    Executa dinamicamente uma ferramenta registrada via DeepSeek Function Calling.
    """
    if not tool_name:
        raise ValueError("Nenhuma ferramenta especificada.")

    arguments = arguments or {}

    tool_function = getattr(ferramentas, tool_name, None)
    if not callable(tool_function):
        tool_info = ferramentas.AVAILABLE_TOOLS.get(tool_name)
        if tool_info:
            tool_function = tool_info.get("function")

    if not callable(tool_function):
        raise ValueError(f"A ferramenta '{tool_name}' não está disponível.")

    try:
        result = tool_function(**arguments)
    except TypeError as error:
        raise ValueError(f"Argumentos inválidos: {error}") from error
    except Exception as error:  # noqa: BLE001
        raise RuntimeError(f"Erro ao executar '{tool_name}': {error}") from error

    if isinstance(result, str):
        return result
    return str(result)
