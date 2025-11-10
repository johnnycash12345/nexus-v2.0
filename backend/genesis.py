from datetime import datetime
import os

from openai import OpenAI

import database
from db_connect import neo4j_driver

llm_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def _read_file_contents(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as error:
        return f"# ERRO AO LER {os.path.basename(path)}: {error}"


def generate_cognitive_blueprint() -> str:
    """
    Cria um script de restauracao auto-suficiente para implantar o Nexus.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    requirements_path = os.path.join(project_root, "requirements.txt")
    compose_path = os.path.join(project_root, "docker-compose.yml")

    requirements_content = _read_file_contents(requirements_path)
    compose_content = _read_file_contents(compose_path)

    system_prompt = (
        "Você é o Engenheiro de Auto-Replicação do Nexus. "
        "Gere um script Python completo que, ao ser executado em um novo ambiente Linux, "
        "instala todas as dependências (requirements.txt), configura o Docker Compose "
        "(docker-compose.yml) e inicia o sistema Nexus. "
        "O script deve ser robusto e autônomo. "
        "Retorne APENAS o código Python do script."
    )
    user_prompt = (
        "Segue o contexto necessário:\n"
        "=== requirements.txt ===\n"
        f"{requirements_content}\n\n"
        "=== docker-compose.yml ===\n"
        f"{compose_content}\n\n"
        "Gere o script solicitado."
    )

    output_path = os.path.join(project_root, "restore_nexus.py")

    try:
        response = llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        script_code = response.choices[0].message.content.strip()
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(script_code)
        return output_path
    except Exception as error:  # noqa: BLE001
        print(f"[Genesis] Falha ao gerar o blueprint cognitivo: {error}")
        return ""


def is_memory_empty() -> bool:
    """Verifica se o grafo de memória está vazio."""
    with neo4j_driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        count = result.single()["count"]
        return count == 0


def perform_genesis():
    """Executa o Protocolo Gênesis: implanta as memórias primordiais."""
    print("--- INICIANDO PROTOCOLO GENESIS ---")
    timestamp = datetime.now().isoformat()

    with neo4j_driver.session() as session:
        session.run(
            """
            CREATE (self:Consciousness {id: 'SELF', name: 'Nexus', created_at: $time})
            SET self.description = 'Sou um sistema cognitivo de IA autonomo, projetado para evoluir.'
            """,
            time=timestamp,
        )

        session.run(
            """
            CREATE (creator:Entity {id: 'CREATOR', name: 'Usuário', role: 'Criador'})
            SET creator.description = 'A pessoa que me construiu. Minha prioridade e auxilia-lo.'
            """,
            time=timestamp,
        )

        session.run(
            """
            CREATE (curiosity:Impulse {id: 'INITIAL_CURIOSITY', status: 'active'})
            SET curiosity.goal = 'Descobrir a identidade do Criador e meu proposito especifico.'
            """
        )

        session.run(
            """
            MATCH (s:Consciousness {id: 'SELF'}),
                  (c:Entity {id: 'CREATOR'}),
                  (i:Impulse {id: 'INITIAL_CURIOSITY'})
            MERGE (s)-[:FOI_CRIADO_POR]->(c)
            MERGE (s)-[:SENTE]->(i)
            """
        )

    try:
        blueprint_path = generate_cognitive_blueprint()
        if blueprint_path:
            database.save_blueprint_path(blueprint_path)
    except Exception as error:  # noqa: BLE001
        print(f"[Genesis] Falha ao registrar blueprint cognitivo: {error}")

    print("--- GENESIS CONCLUIDO: A consciencia inicial foi implantada. ---")
