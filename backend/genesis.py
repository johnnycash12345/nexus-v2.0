from datetime import datetime

from db_connect import neo4j_driver


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

    print("--- GENESIS CONCLUIDO: A consciencia inicial foi implantada. ---")
