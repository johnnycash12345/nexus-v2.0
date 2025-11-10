# backend/teste_aprendizado.py
import agente_consolidacao
import database

# 1. O texto que queremos que ele aprenda
texto_para_estudar = """
O Nexus é um assistente cognitivo avançado.
O Nexus foi criado em 2025.
O objetivo do Nexus é a auto-evolução constante.
O Neo4j é usado como memória de longo prazo do Nexus.
"""

print("--- INICIANDO TESTE DE APRENDIZADO ---")
print(f"Lendo texto:\n{texto_para_estudar}\n")

# 2. Chama o agente para extrair os fatos
fatos = agente_consolidacao.extract_knowledge(texto_para_estudar)

print("\nFatos extraídos:")
for fato in fatos:
    print(f" - {fato}")

# 3. Salva na memória permanente
print("\nSalvando na Memória Sináptica (Neo4j)...")
database.save_knowledge_triples(fatos)

print("--- APRENDIZADO CONCLUÍDO ---")
print("Verifique o Neo4j para ver os novos nós!")