from __future__ import annotations

from datetime import datetime, timezone

from db_connect import neo4j_driver

DECAY_RATE = 0.95
PROMOTION_THRESHOLD = 5.0
PRUNE_THRESHOLD = 0.1
MLP_CONFIDENCE = 0.95


def run_memory_consolidation_cycle() -> None:
    """
    Executa um ciclo de manutencao da memoria:
    - promove memorias MCP validadas para MLP;
    - reduz a forca sinaptica (decaimento);
    - remove memorias MCP muito fracas.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    with neo4j_driver.session() as session:
        # Garante que todos os conceitos possuam um identificador consistente
        session.run(
            """
            MATCH (concept:Conceito)
            WHERE concept.id IS NULL
            SET concept.id = randomUUID()
            """
        )

        # Decaimento: reduz forca sinaptica em 5%
        session.run(
            """
            MATCH (concept:Conceito)
            WHERE concept.forca_sinaptica IS NOT NULL
            SET concept.forca_sinaptica = coalesce(concept.forca_sinaptica, 0.0) * $decay
            """,
            decay=DECAY_RATE,
        )

        # Promocao: memorias MCP frequentemente acessadas e validadas pelo NQR
        session.run(
            """
            MATCH (concept:Conceito)
            WHERE concept.status_memoria = 'MCP'
              AND coalesce(concept.forca_sinaptica, 0.0) > $promotion_threshold
              AND (
                    coalesce(concept.validado_nqr, false) = true
                 OR concept.ultima_validacao_nqr IS NOT NULL
              )
            SET concept.status_memoria = 'MLP',
                concept.confianca_intrinseca = $mlp_confidence,
                concept.promovido_em = datetime($timestamp),
                concept.ultima_ativacao = coalesce(concept.ultima_ativacao, datetime($timestamp))
            """,
            promotion_threshold=PROMOTION_THRESHOLD,
            mlp_confidence=MLP_CONFIDENCE,
            timestamp=timestamp,
        )

        # Poda: remove memorias MCP que nao ganharam relevancia
        session.run(
            """
            MATCH (concept:Conceito)
            WHERE concept.status_memoria = 'MCP'
              AND coalesce(concept.forca_sinaptica, 0.0) < $prune_threshold
            DETACH DELETE concept
            """,
            prune_threshold=PRUNE_THRESHOLD,
        )

