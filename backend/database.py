from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from chromadb.utils import embedding_functions

from db_connect import chroma_client, neo4j_driver
from models import (
    ChatMessage,
    ChatSession,
    InboxItem,
    SystemLog,
    SystemSettings,
)

# Default embedding function used for chat storage in ChromaDB.
default_embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

DEFAULT_MEMORY_STATUS = "MCP"
DEFAULT_INTRINSIC_CONFIDENCE = 0.25
DEFAULT_SYNAPTIC_STRENGTH = 1.0
DEFAULT_REL_CONTEXTUAL_RELEVANCE = 1.0


def create_inbox_item(item: InboxItem) -> InboxItem:
    """Persist a new :InboxItem node in Neo4j."""
    with neo4j_driver.session() as session:
        session.run(
            "CREATE (i:InboxItem {id: $id, content: $content, type: $type, created_at: $created_at})",
            **item.model_dump(),
        )
    return item


def create_chat_session(title: str) -> ChatSession:
    """Create and store a new chat session node in Neo4j and link it to the CREATOR entity."""
    session_model = ChatSession(title=title)
    payload = session_model.model_dump()

    with neo4j_driver.session() as db_session:
        db_session.run(
            """
            MERGE (creator:Entity {id: 'CREATOR'})
            ON CREATE SET creator.name = coalesce(creator.name, 'Usuario')
            MERGE (session:ChatSession {id: $id})
            ON CREATE SET session.created_at = $created_at
            SET session.title = $title,
                session.updated_at = $updated_at
            MERGE (creator)-[:PARTICIPATES_IN]->(session)
            """,
            **payload,
        )

    return session_model


def get_all_sessions() -> List[ChatSession]:
    """Fetch all chat sessions ordered by most recent update."""
    with neo4j_driver.session() as db_session:
        result = db_session.run(
            "MATCH (s:ChatSession) RETURN s ORDER BY s.updated_at DESC"
        )
        sessions: List[ChatSession] = []
        for record in result:
            node = record["s"]
            sessions.append(ChatSession(**node))
        return sessions


def get_inbox_items() -> List[InboxItem]:
    """Fetch every :InboxItem node from Neo4j."""
    with neo4j_driver.session() as session:
        results = session.run("MATCH (i:InboxItem) RETURN i")
        return [InboxItem(**record["i"]) for record in results]


def get_inbox_item_by_id(item_id: str) -> Optional[InboxItem]:
    """Fetch a specific :InboxItem node by id."""
    with neo4j_driver.session() as session:
        result = session.run(
            "MATCH (i:InboxItem {id: $id}) RETURN i LIMIT 1",
            id=item_id,
        )
        record = result.single()
        if record:
            return InboxItem(**record["i"])
        return None


def add_chat_message(message: ChatMessage) -> ChatMessage:
    """Append a chat message into the ChromaDB collection linked to the session."""
    collection_name = f"chat_{message.session_id}"
    role_value = (message.role or "").lower() or "unknown"
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=default_embedding_function,
    )

    collection.add(
        documents=[message.content],
        metadatas=[{"role": role_value, "timestamp": message.id}],
        ids=[message.id],
    )

    try:
        with neo4j_driver.session() as session:
            session.run(
                """
                MERGE (chat_session:ChatSession {id: $session_id})
                ON CREATE SET chat_session.title = $session_id,
                              chat_session.created_at = $timestamp_iso,
                              chat_session.updated_at = $timestamp_iso
                SET chat_session.updated_at = $timestamp_iso
                WITH chat_session
                MERGE (creator:Entity {id: 'CREATOR'})
                ON CREATE SET creator.name = 'Usuario'
                MERGE (creator)-[:PARTICIPATES_IN]->(chat_session)
                MERGE (msg:ChatMessage {id: $id})
                SET msg.role = $role,
                    msg.content = $content,
                    msg.timestamp = datetime($timestamp_iso),
                    msg.timestamp_iso = $timestamp_iso,
                    msg.session_id = $session_id
                MERGE (chat_session)-[:HAS_MESSAGE]->(msg)
                """,
                id=message.id,
                session_id=message.session_id,
                role=role_value,
                content=message.content,
                timestamp_iso=timestamp_iso,
            )

            if role_value == "assistant":
                session.run(
                    """
                    MATCH (chat_session:ChatSession {id: $session_id})-[:HAS_MESSAGE]->(reply:ChatMessage {id: $id})
                    MATCH (chat_session)-[:HAS_MESSAGE]->(question:ChatMessage)
                    WHERE question.role = 'user'
                      AND question.timestamp IS NOT NULL
                      AND reply.timestamp IS NOT NULL
                      AND question.timestamp <= reply.timestamp
                    WITH reply, question
                    ORDER BY question.timestamp DESC
                    LIMIT 1
                    MERGE (reply)-[:RESPONSE_TO]->(question)
                    """,
                    session_id=message.session_id,
                    id=message.id,
                )
    except Exception as error:  # noqa: BLE001
        print(f"[Database] Aviso: nao foi possivel registrar mensagem no grafo. Detalhe: {error}")

    return message


def get_chat_messages(session_id: str) -> List[ChatMessage]:
    """Retrieve all messages for a session from ChromaDB."""
    collection_name = f"chat_{session_id}"
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=default_embedding_function,
        )
        results = collection.get(include=["metadatas", "documents"])

        messages: List[ChatMessage] = []
        for index in range(len(results["ids"])):
            messages.append(
                ChatMessage(
                    id=results["ids"][index],
                    session_id=session_id,
                    content=results["documents"][index],
                    role=results["metadatas"][index]["role"],
                )
            )

        messages.sort(key=lambda chat_msg: chat_msg.id)
        return messages
    except Exception as error:
        print(f"Warning: could not fetch chat {collection_name}. Error: {error}")
        return []


def create_log(log: SystemLog):
    with neo4j_driver.session() as session:
        session.run(
            "CREATE (l:SystemLog {id: $id, timestamp: $timestamp, type: $type, title: $title, "
            "description: $description, agent: $agent, project_id: $project_id})",
            **log.model_dump(),
        )
        if log.project_id:
            session.run(
                """
                MATCH (p:DevProject {id: $pid}), (l:SystemLog {id: $lid})
                MERGE (p)-[:TEM_LOG]->(l)
                """,
                pid=log.project_id,
                lid=log.id,
            )


def get_recent_logs(limit: int = 50) -> List[SystemLog]:
    with neo4j_driver.session() as session:
        result = session.run(
            "MATCH (l:SystemLog) RETURN l ORDER BY l.timestamp DESC LIMIT $limit",
            limit=limit,
        )
        return [SystemLog(**record["l"]) for record in result]


def save_knowledge_triples(triples: List[Dict[str, str]]):
    """
    Grava uma lista de fatos (triplas) na Memoria Sinaptica (Neo4j).
    Usa MERGE para evitar duplicatas e conectar conhecimentos existentes.
    """
    if not triples:
        return
    print(f"[Database] Salvando {len(triples)} novos fatos na Memoria Sinaptica...")
    with neo4j_driver.session() as session:
        for item in triples:
            source = (item.get("source") or "Desconhecido").replace("'", "").strip()
            target = (item.get("target") or "Desconhecido").replace("'", "").strip()
            rel = (
                (item.get("relationship") or "RELACIONADO_A")
                .upper()
                .replace(" ", "_")
                .strip()
            )
            if not source or not target or not rel:
                continue

            rel = "".join(char for char in rel if char.isalnum() or char == "_")
            if not rel:
                rel = "RELACIONADO_A"

            timestamp = datetime.now(timezone.utc).isoformat()
            try:
                session.run(
                    f"""
                    MERGE (source:Conceito {{name: $source_name}})
                      ON CREATE SET
                        source.id = randomUUID(),
                        source.status_memoria = $default_status,
                        source.confianca_intrinseca = $default_confidence,
                        source.forca_sinaptica = $default_strength,
                        source.ultima_ativacao = datetime($timestamp),
                        source.criado_em = datetime($timestamp)
                    SET
                        source.status_memoria = coalesce(source.status_memoria, $default_status),
                        source.confianca_intrinseca = coalesce(source.confianca_intrinseca, $default_confidence),
                        source.forca_sinaptica = coalesce(source.forca_sinaptica, $default_strength),
                        source.id = coalesce(source.id, randomUUID()),
                        source.ultima_ativacao = datetime($timestamp),
                        source.atualizado_em = datetime($timestamp)

                    MERGE (target:Conceito {{name: $target_name}})
                      ON CREATE SET
                        target.id = randomUUID(),
                        target.status_memoria = $default_status,
                        target.confianca_intrinseca = $default_confidence,
                        target.forca_sinaptica = $default_strength,
                        target.ultima_ativacao = datetime($timestamp),
                        target.criado_em = datetime($timestamp)
                    SET
                        target.status_memoria = coalesce(target.status_memoria, $default_status),
                        target.confianca_intrinseca = coalesce(target.confianca_intrinseca, $default_confidence),
                        target.forca_sinaptica = coalesce(target.forca_sinaptica, $default_strength),
                        target.id = coalesce(target.id, randomUUID()),
                        target.ultima_ativacao = datetime($timestamp),
                        target.atualizado_em = datetime($timestamp)

                    MERGE (source)-[rel:{rel}]->(target)
                      ON CREATE SET
                        rel.confianca_intrinseca = $default_confidence,
                        rel.relevancia_contextual = $default_rel_relevance,
                        rel.criado_em = datetime($timestamp)
                    SET
                        rel.confianca_intrinseca = coalesce(rel.confianca_intrinseca, $default_confidence),
                        rel.relevancia_contextual = coalesce(rel.relevancia_contextual, $default_rel_relevance),
                        rel.atualizado_em = datetime($timestamp)
                    """,
                    source_name=source,
                    target_name=target,
                    default_status=DEFAULT_MEMORY_STATUS,
                    default_confidence=DEFAULT_INTRINSIC_CONFIDENCE,
                    default_strength=DEFAULT_SYNAPTIC_STRENGTH,
                    default_rel_relevance=DEFAULT_REL_CONTEXTUAL_RELEVANCE,
                    timestamp=timestamp,
                )
            except Exception as error:
                print(f"[Database] Erro ao salvar tripla {source}-[:{rel}]->{target}: {error}")


def save_meta_knowledge(entries: List[Dict[str, str]]):
    """
    Persiste registros de meta-conhecimento, anotando dissonancias e resolucoes.
    Cada entrada recebe um id unico caso nao seja informado.
    """
    if not entries:
        return

    with neo4j_driver.session() as session:
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            node_id = entry.get("id") or str(uuid.uuid4())
            payload = {**entry, "id": node_id}
            payload.setdefault("registrado_em", datetime.now().isoformat())
            session.run(
                "MERGE (m:MetaConhecimento {id: $id}) "
                "SET m += $props",
                id=node_id,
                props=payload,
            )


def register_memory_activation(node_id: str, boost: float = 1.0, validated: bool = False):
    """
    Reforca um nodo de memoria existente, atualizando forca sinaptica e marcando validacoes.
    """
    if not node_id:
        return

    timestamp = datetime.now(timezone.utc).isoformat()
    with neo4j_driver.session() as session:
        session.run(
            """
            MATCH (n {id: $node_id})
            SET n.forca_sinaptica = coalesce(n.forca_sinaptica, $base_strength) + $boost,
                n.ultima_ativacao = datetime($timestamp),
                n.status_memoria = coalesce(n.status_memoria, $default_status),
                n.confianca_intrinseca = CASE
                    WHEN n.status_memoria = 'MCP'
                        THEN coalesce(n.confianca_intrinseca, $default_confidence)
                    ELSE coalesce(n.confianca_intrinseca, $default_confidence)
                END,
                n.validado_nqr = CASE
                    WHEN $validated THEN true
                    ELSE coalesce(n.validado_nqr, false)
                END,
                n.ultima_validacao_nqr = CASE
                    WHEN $validated THEN datetime($timestamp)
                    ELSE n.ultima_validacao_nqr
                END
            """,
            node_id=node_id,
            boost=boost,
            timestamp=timestamp,
            validated=validated,
            base_strength=DEFAULT_SYNAPTIC_STRENGTH,
            default_status=DEFAULT_MEMORY_STATUS,
            default_confidence=DEFAULT_INTRINSIC_CONFIDENCE,
        )


def _normalize_confidence(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)
    return max(0.0, min(number, 1.0))


def _get_attr(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    getter = getattr(obj, "get", None)
    if callable(getter):
        try:
            return getter(key, default)
        except TypeError:
            pass
    try:
        return obj[key]  # type: ignore[index]
    except Exception:
        try:
            obj_dict = dict(obj)  # type: ignore[arg-type]
        except Exception:
            return default
        return obj_dict.get(key, default)


def _relationship_weight(rel: Any) -> float:
    intrinsic = _normalize_confidence(_get_attr(rel, "confianca_intrinseca"), default=0.0)
    contextual = _normalize_confidence(_get_attr(rel, "relevancia_contextual"), default=0.0)
    if intrinsic <= 0.0 or contextual <= 0.0:
        return 10.0
    return 1.0 / (intrinsic * contextual)


def _format_path(node_list: Sequence[Any], rel_list: Sequence[Any]) -> str:
    segments: List[str] = []
    count = len(node_list)
    for index, node in enumerate(node_list):
        node_name = (
            _get_attr(node, "name")
            or _get_attr(node, "title")
            or _get_attr(node, "id")
            or f"Nodo{index}"
        )
        segments.append(str(node_name))
        if index < count - 1 and index < len(rel_list):
            rel = rel_list[index]
            rel_type = _get_attr(rel, "type")
            if rel_type is None:
                rel_type_attr = getattr(rel, "type", None)
                rel_type = rel_type_attr() if callable(rel_type_attr) else rel_type_attr
            rel_name = str(rel_type or "RELACAO")
            segments.append(f"-[{rel_name}]->")
    return " ".join(segments)


def _is_critical_context(context_of_use: str | None) -> bool:
    if not context_of_use:
        return False
    lowered = context_of_use.lower()
    critical_tokens = (
        "critico",
        "critica",
        "urgente",
        "auditoria",
        "seguranca",
        "compliance",
        "emergencia",
    )
    return any(token in lowered for token in critical_tokens)


class NexusGraph:
    MAX_PATH_LENGTH = 4
    MCP_PENALTY = 5.0

    @staticmethod
    def quantum_search(
        query: str,
        context_of_use: str | None = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Executa busca ponderada no grafo considerando confiancas intrinsecas.
        Retorna documentos estruturados para o pipeline RAG.
        """
        term = (query or "").strip().lower()
        critical = _is_critical_context(context_of_use)
        if not term:
            return []

        cypher = """
        MATCH (origin:Consciousness {id: 'SELF'})
        CALL {
            WITH origin
            MATCH path = (origin)-[rels*1..$max_depth]->(target)
            WHERE
                (
                    toLower(coalesce(target.name, '')) CONTAINS $term OR
                    toLower(coalesce(target.title, '')) CONTAINS $term OR
                    toLower(coalesce(target.description, '')) CONTAINS $term
                )
                AND ($critical = false OR ALL(node IN nodes(path) WHERE coalesce(node.status_memoria, '') <> 'MCP'))
            WITH DISTINCT path, rels, target,
                 reduce(total = 0.0, r IN rels | total + CASE
                     WHEN coalesce(r.confianca_intrinseca, 0.0) <= 0 OR coalesce(r.relevancia_contextual, 0.0) <= 0
                         THEN 10.0
                     ELSE 1.0 / (r.confianca_intrinseca * r.relevancia_contextual)
                 END
            ) AS path_weight
            RETURN target, rels, nodes(path) AS node_list, path_weight,
                   elementId(target) AS target_element_id,
                   [node IN nodes(path) | elementId(node)] AS node_element_ids
            ORDER BY path_weight ASC
            LIMIT $limit
        }
        RETURN target, rels, node_list, node_element_ids, path_weight, target_element_id
        """

        documents: List[Dict[str, Any]] = []
        with neo4j_driver.session() as session:
            records = session.run(
                cypher,
                term=term,
                limit=limit,
                max_depth=NexusGraph.MAX_PATH_LENGTH,
                critical=critical,
            )
            for record in records:
                target = record.get("target")
                rels = record.get("rels", [])
                node_list = record.get("node_list", [])
                node_element_ids = record.get("node_element_ids", [])
                path_weight = float(record.get("path_weight", 0.0))
                target_element_id = record.get("target_element_id")

                # Penaliza caminhos MCP quando nao critico
                if not critical:
                    if any(_get_attr(node, "status_memoria") == "MCP" for node in node_list):
                        path_weight += NexusGraph.MCP_PENALTY

                intrinsic_values: List[float] = []
                for rel in rels:
                    intrinsic_values.append(
                        _normalize_confidence(_get_attr(rel, "confianca_intrinseca"))
                    )
                target_conf = _normalize_confidence(_get_attr(target, "confianca_intrinseca"))
                if target_conf > 0:
                    intrinsic_values.append(target_conf)
                intrinsic_confidence = (
                    sum(intrinsic_values) / len(intrinsic_values) if intrinsic_values else 0.0
                )

                target_id = _get_attr(target, "id") or target_element_id

                document = {
                    "id": target_id,
                    "title": _get_attr(target, "name")
                    or _get_attr(target, "title")
                    or target_id
                    or "Conceito",
                    "content": _format_path(node_list, rels),
                    "url": _get_attr(target, "fonte_url") or _get_attr(target, "url") or "",
                    "confianca_intrinseca": intrinsic_confidence,
                    "status_memoria": _get_attr(target, "status_memoria"),
                    "path_weight": path_weight,
                    "context_nodes": [
                        {
                            "id": _get_attr(node, "id")
                            or (node_element_ids[index] if index < len(node_element_ids) else None),
                            "name": _get_attr(node, "name") or _get_attr(node, "title"),
                            "status_memoria": _get_attr(node, "status_memoria"),
                        }
                        for index, node in enumerate(node_list)
                    ],
                }
                documents.append(document)

        if not documents:
            # Fallback simples: retorna conceitos diretamente associados ao termo.
            fallback_cypher = """
            MATCH (concept:Conceito)
            WHERE toLower(coalesce(concept.name, '')) CONTAINS $term
                OR toLower(coalesce(concept.title, '')) CONTAINS $term
            RETURN concept, elementId(concept) AS concept_element_id
            LIMIT $limit
            """
            with neo4j_driver.session() as session:
                fallback_records = session.run(
                    fallback_cypher,
                    term=term,
                    limit=limit,
                )
                for record in fallback_records:
                    node = record.get("concept")
                    element_id = record.get("concept_element_id")
                    node_id = _get_attr(node, "id") or element_id
                    documents.append(
                        {
                            "id": node_id,
                            "title": _get_attr(node, "name") or _get_attr(node, "title") or node_id or "Conceito",
                            "content": _get_attr(node, "description") or _get_attr(node, "name") or "",
                            "url": _get_attr(node, "fonte_url") or _get_attr(node, "url") or "",
                            "confianca_intrinseca": _normalize_confidence(
                                _get_attr(node, "confianca_intrinseca"), default=0.0
                            ),
                            "status_memoria": _get_attr(node, "status_memoria"),
                            "path_weight": 0.0,
                            "context_nodes": [],
                        }
                    )

        documents.sort(key=lambda doc: doc.get("path_weight", 0.0))
        return documents[:limit]


def save_settings(settings: SystemSettings):
    with neo4j_driver.session() as session:
        session.run(
            "MERGE (c:SystemConfig) SET c.data = $data",
            data=settings.model_dump_json(),
        )


def get_settings() -> SystemSettings:
    with neo4j_driver.session() as session:
        result = session.run("MATCH (c:SystemConfig) RETURN c LIMIT 1")
        record = result.single()
        if record and record["c"].get("data"):
            config_data = json.loads(record["c"]["data"])
            return SystemSettings(**config_data)

    default_settings = SystemSettings()
    save_settings(default_settings)
    return default_settings
