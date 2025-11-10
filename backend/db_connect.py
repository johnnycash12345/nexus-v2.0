import time
import os

from neo4j import GraphDatabase
import chromadb

# --- Conexao Neo4j (Memoria Sinaptica) ---
# Lemos as variaveis de ambiente que definimos no docker-compose.yml
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "nexuspassword123")

# Inicializa o driver de conexao com o Neo4j
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def close_neo4j_connection():
    """Fecha a conexao do driver do Neo4j."""
    neo4j_driver.close()


# --- Conexao ChromaDB (Memoria Media) ---
# Lemos as variaveis de ambiente do docker-compose.yml
# O backend (Python) se conecta ao ChromaDB pelo nome do servico 'chromadb'
# na porta 8000, como definido no environment.
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8005))

# Inicializa o cliente de conexao com o ChromaDB usando um loop de tentativa
max_retries = 5
retry_delay = 5  # Segundos
chroma_client = None
for attempt in range(max_retries):
    try:
        print(
            f"Tentativa {attempt + 1}/{max_retries}: Conectando ao ChromaDB em "
            f"{CHROMA_HOST}:{CHROMA_PORT}..."
        )
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        chroma_client.heartbeat()
        print("SUCESSO: Conexao ChromaDB estabelecida.")
        break
    except Exception as error:
        print(
            f"Aviso: Falha na conexao ChromaDB. Esperando {retry_delay}s. "
            f"Erro: {error}"
        )
        time.sleep(retry_delay)

if not chroma_client:
    raise ConnectionError(
        "Falha critica: Nao foi possivel conectar ao ChromaDB apos multiplas tentativas."
    )

print("--- Conexoes de Banco de Dados Inicializadas ---")
print(f"Neo4j Driver: {neo4j_driver}")
print(f"Chroma Client: {chroma_client}")
print("------------------------------------------------")
