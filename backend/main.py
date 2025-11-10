# ruff: noqa: E402
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Tuple

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

try:  # pragma: no cover
    from neo4j.time import Date as Neo4jDate
    from neo4j.time import DateTime as Neo4jDateTime
    from neo4j.time import Duration as Neo4jDuration
    from neo4j.time import Time as Neo4jTime
except ImportError:  # pragma: no cover
    Neo4jDate = Neo4jDateTime = Neo4jDuration = Neo4jTime = tuple()

load_dotenv()

import agente_central
import agente_codigo
import agente_executor
import agente_pesquisa
import agente_consolidacao
import agente_noticias
import ferramentas
import database
import genesis
from db_connect import chroma_client, close_neo4j_connection, neo4j_driver
from database import (
    add_chat_message,
    create_chat_session,
    create_inbox_item,
    get_all_sessions,
    get_chat_messages,
    get_inbox_item_by_id,
    get_inbox_items,
)
import agente_arquiteto
from agente_nqr import NexusQuantumReasoning
from models import (
    ChatInput,
    ChatMessage,
    ChatSession,
    DevProject,
    InboxItem,
    SystemLog,
    SystemSettings,
)

chat_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
nqr_chat = NexusQuantumReasoning()


class CodeGenerateRequest(BaseModel):
    prompt: str


class CodeRefactorRequest(BaseModel):
    code: str


class CodeResponse(BaseModel):
    code: str


class GraphNode(BaseModel):
    id: str
    label: str
    properties: dict


class GraphLink(BaseModel):
    source: str
    target: str
    type: str


class GraphData(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]


class PerplexicaResponse(BaseModel):
    role: str = "assistant"
    answer: str
    sources: List[Dict] = []
    session_id: str | None = None


class FileNode(BaseModel):
    name: str
    type: str
    path: str
    children: List["FileNode"] | None = None


class IdeaInput(BaseModel):
    text: str


def log_event(
    type: str,
    title: str,
    description: str,
    agent: str,
    project_id: str | None = None,
):
    """Função auxiliar para registrar eventos no sistema rapidamente."""
    new_log = SystemLog(
        timestamp=datetime.now().isoformat(),
        type=type,
        title=title,
        description=description,
        agent=agent,
        project_id=project_id,
    )
    database.create_log(new_log)
    print(f"[{agent}] LOG: {title}")


FileNode.model_rebuild()


def _serialize_neo4j_value(value: Any) -> Any:
    """
    Converte valores Neo4j (DateTime, Duration etc.) em tipos serializáveis.
    """
    if isinstance(value, (Neo4jDateTime, Neo4jDate, Neo4jTime, Neo4jDuration)):
        return value.isoformat()
    if isinstance(value, list):
        return [_serialize_neo4j_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_serialize_neo4j_value(item) for item in value)
    if isinstance(value, dict):
        return {key: _serialize_neo4j_value(val) for key, val in value.items()}
    return value


def get_directory_structure(root_path: str) -> List[FileNode]:
    tree: List[FileNode] = []
    try:
        for entry in os.scandir(root_path):
            if entry.is_dir():
                tree.append(
                    FileNode(
                        name=entry.name,
                        type="directory",
                        path=entry.path,
                        children=get_directory_structure(entry.path),
                    )
                )
            else:
                tree.append(
                    FileNode(
                        name=entry.name,
                        type="file",
                        path=entry.path,
                    )
                )
    except Exception as error:
        print(f"Erro ao ler diretório {root_path}: {error}")
    return tree


def get_proactive_message_by_rule(item_type: str, content: str) -> str:
    """Gera mensagens proativas com base em regras simples."""
    lower_type = item_type.lower()
    if "lembrete" in lower_type:
        return (
            f"Notei que '{content}' é um lembrete. Você gostaria que eu agendasse "
            "isso no seu Google Agenda?"
        )
    if "projeto" in lower_type:
        return (
            f"Isto parece ser um novo projeto: '{content}'. Confirma? Se sim, posso "
            "iniciar a Pesquisa Profunda e o planejamento do MVP."
        )
    return (
        f"Sua nota '{content}' (Tipo: {item_type}) foi salva. O que gostaria de fazer "
        "a seguir?"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if genesis.is_memory_empty():
        genesis.perform_genesis()
    else:
        print("--- Memoria detectada. Nexus operante. ---")
    try:
        yield
    finally:
        print("--- Fechando conexão com o Neo4j ---")
        close_neo4j_connection()


def background_learning_task(text_to_learn: str, source_topic: str):
    """
    Função que roda em segundo plano para extrair e salvar conhecimento
    sem bloquear a resposta principal para o usuário.
    """
    print(f"[Background] Iniciando aprendizado sobre: '{source_topic}'...")
    try:
        fatos = agente_consolidacao.extract_knowledge(text_to_learn)
        database.save_knowledge_triples(fatos)
        print(f"[Background] Aprendizado concluído para '{source_topic}'.")
    except Exception as error:
        print(f"[Background] ERRO durante o aprendizado: {error}")


def synthesize_tool_response(user_query: str, tool_name: str, tool_result: str) -> str:
    """
    Gera uma resposta amigável ao usuário com base no resultado de uma ferramenta.
    """
    system_prompt = (
        "Você é o sintetizador do Nexus. Com base no resultado retornado por uma "
        "ferramenta, elabore uma resposta clara para o usuário, explicando como a "
        "ferramenta foi utilizada."
    )
    user_prompt = (
        f"Pergunta original:\n{user_query}\n\n"
        f"Ferramenta utilizada: {tool_name}\n"
        f"Resultado bruto:\n{tool_result}"
    )
    try:
        response = chat_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as error:  # noqa: BLE001
        print(
            f"[Endpoint /api/chat/send] Falha ao sintetizar resposta de ferramenta: {error}"
        )
        return (
            "Executei a ferramenta solicitada, mas não consegui gerar uma resposta formatada. "
            f"Resultado bruto:\n{tool_result}"
        )


def check_service_health(service_name: str) -> Tuple[bool, str]:
    normalized = service_name.strip().lower()
    try:
        if normalized == "neo4j":
            with neo4j_driver.session() as session:
                session.run("RETURN 1 AS ok").single()
            return True, "OK"

        if normalized == "chromadb":
            chroma_client.list_collections()
            return True, "OK"

        if normalized == "deepseek":
            chat_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um verificador de status. Responda 'OK'.",
                    },
                    {"role": "user", "content": "Ping de saúde. Responda apenas OK."},
                ],
                max_tokens=5,
                temperature=0.0,
            )
            return True, "OK"

        return False, f"Serviço '{service_name}' desconhecido."
    except Exception as error:
        return False, str(error)


def retrieve_long_term_context(
    content: str,
    session_id: str | None,
    exclude_message_id: str | None = None,
) -> Tuple[str, List[Dict[str, str]], List[Dict[str, Any]]]:
    """
    Recupera contexto relevante a partir do Neo4j (memoria sinaptica) e ChromaDB.
    Retorna texto consolidado e uma lista de fontes.
    """
    print(f"[RAG] Recuperando contexto para: '{content}' (sessao: {session_id})")

    context_lines: List[str] = []
    sources: List[Dict[str, str]] = []
    context_facts: List[Dict[str, Any]] = []
    lowered = content.lower()

    # Consulta grafos (Neo4j)
    if lowered:
        try:
            with neo4j_driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WHERE toLower(coalesce(n.name, n.title, n.description, '')) CONTAINS $term
                    OPTIONAL MATCH (n)-[r]->(m)
                    WITH n, collect({rel: type(r), target: coalesce(m.name, m.title, m.id, '')}) AS rels
                    RETURN n, rels
                    LIMIT 5
                    """,
                    term=lowered,
                )
                for record in result:
                    node = record["n"]
                    rels = record["rels"] or []
                    node_name = (
                        node.get("name")
                        or node.get("title")
                        or node.get("id")
                        or "NoName"
                    )
                    description = node.get("description")
                    line_parts = [f"Neo4j Node: {node_name}"]
                    if description:
                        line_parts.append(f"Descricao: {description}")
                    if rels:
                        rel_text = "; ".join(
                            f"{item.get('rel')} -> {item.get('target')}"
                            for item in rels
                            if item.get("rel")
                        )
                        if rel_text:
                            line_parts.append(f"Relacoes: {rel_text}")
                    combined_text = " | ".join(line_parts)
                    context_lines.append(combined_text)
                    intrinsic = float(node.get("confianca_intrinseca", 0.0) or 0.0)
                    context_facts.append(
                        {
                            "content": combined_text,
                            "title": node_name,
                            "confianca_intrinseca": intrinsic,
                            "url": node.get("fonte_url") or "",
                            "status_memoria": node.get("status_memoria"),
                        }
                    )
                    sources.append(
                        {
                            "title": f"Neo4j:{node_name}",
                            "url": "",
                        }
                    )
        except Exception as error:  # noqa: BLE001
            print(f"[RAG] ERRO ao consultar Neo4j: {error}")

    # Consulta memoria de curto prazo (ChromaDB)
    if session_id:
        collection_name = f"chat_{session_id}"
        try:
            collection = chroma_client.get_or_create_collection(
                name=collection_name,
                embedding_function=database.default_embedding_function,
            )
            query_result = collection.query(
                query_texts=[content],
                n_results=3,
                include=["metadatas", "documents", "distances"],
            )
            documents = query_result.get("documents", [[]])[0]
            metadatas = query_result.get("metadatas", [[]])[0]
            ids = query_result.get("ids", [[]])[0]
            distances = query_result.get("distances", [[]])[0]
            for index, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
                doc_id = ids[index - 1] if index - 1 < len(ids) else f"doc_{index}"
                if exclude_message_id and doc_id == exclude_message_id:
                    continue
                context_lines.append(f"ChatMem[{doc_id}]: {doc}")
                role = meta.get("role") if isinstance(meta, dict) else ""
                distance = distances[index - 1] if index - 1 < len(distances) else None
                sources.append(
                    {
                        "title": f"ChatMem:{role or 'mensagem'}",
                        "url": "",
                        "distance": distance,
                    }
                )
                context_facts.append(
                    {
                        "content": doc,
                        "title": f"ChatMem:{role or 'mensagem'}",
                        "confianca_intrinseca": 0.0,
                        "url": "",
                        "status_memoria": "MCP",
                    }
                )
        except Exception as error:  # noqa: BLE001
            print(f"[RAG] ERRO ao consultar ChromaDB ({collection_name}): {error}")

    if not context_lines:
        context_lines.append("Nenhum contexto de longo prazo relevante encontrado.")

    return "\n".join(context_lines), sources, context_facts


def generate_chat_response(
    content: str,
    history: List[ChatMessage],
    session_id: str | None,
    current_message_id: str | None = None,
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Gera resposta conversacional utilizando o LLM DeepSeek com memoria curta e contexto recuperado.
    """
    print("[Agente de Chat] Gerando resposta com contexto...")

    long_term_context, sources, context_facts = retrieve_long_term_context(
        content,
        session_id,
        exclude_message_id=current_message_id,
    )

    recent_history = history[-10:] if history else []
    if recent_history:
        history_text = "\n".join(
            f"{message.role.upper()}: {message.content}" for message in recent_history
        )
    else:
        history_text = "Nenhum historico recente."

    system_prompt = (
        "Voce e o Nexus, o assistente cognitivo e companheiro pessoal de Paulo. "
        "Seja amigavel, empatico e responda de forma util, mantendo o contexto. "
        "Use o CONTEXTO DE LONGO PRAZO e o Historico Recente para formular sua resposta. "
        "DIRETRIZ DE MEMORIA: Se o usuario fornecer informacoes sobre si mesmo na MENSAGEM ATUAL, "
        "trate isso como CONHECIMENTO NOVO, mesmo que apareca no contexto recuperado devido a indexacao rapida. "
        "Nunca diga 'Eu ja sabia disso' quando a informacao veio na mensagem atual. Agradeca e confirme o aprendizado."
    )
    full_prompt = (
        f"CONTEXTO DE LONGO PRAZO:\n{long_term_context}\n\n"
        f"HISTORICO RECENTE:\n{history_text}\n\n"
        f"NOVA MENSAGEM: {content}"
    )

    try:
        response = chat_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt},
            ],
            temperature=0.7,
        )
        answer = response.choices[0].message.content
        answer = nqr_chat.self_correct_rag(answer, context_facts)
        return answer, sources
    except Exception as error:  # noqa: BLE001
        print(f"[Agente de Chat] ERRO: {error}")
        return (
            "Desculpe, estou tendo um problema de conexao com o meu LLM. Tente novamente.",
            [],
        )


# Le a variavel de ambiente ALLOWED_ORIGINS com urls separados por virgula.
origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
# Divide a string em uma lista, removendo espacos extras e ignorando entradas vazias.
allowed_origins = [
    origin.strip() for origin in origins_str.split(",") if origin.strip()
]
if not allowed_origins:
    allowed_origins = ["http://localhost:5173"]

ngrok_origin = os.getenv("NGROK_URL", "").strip()
if ngrok_origin and ngrok_origin not in allowed_origins:
    allowed_origins.append(ngrok_origin)

app = FastAPI(
    title="Nexus Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Nexus Backend (Fase V1.0) Online"}


@app.get("/api/capabilities")
async def get_capabilities():
    """
    Retorna um manifesto de funcionalidades, agentes e ferramentas do Nexus.
    """
    tool_descriptions = ferramentas.get_tool_descriptions()

    capabilities = {
        "system_name": "Nexus v2.0 (Lumen Core)",
        "description": "Uma IA cognitiva multiagente.",
        "agents": [
            {
                "name": "Agente Central",
                "description": "Gerencia o roteamento de intenções e a conversa.",
                "endpoint": "/api/chat/send",
                "modes": ["Chat Pessoal", "Lembrete", "Nota Simples"],
            },
            {
                "name": "Agente de Pesquisa",
                "description": "Executa pesquisas profundas e RAG.",
                "endpoint": "/api/chat/send",
                "modes": ["Pesquisa Profunda"],
            },
            {
                "name": "Agente Arquiteto",
                "description": "Gerencia a 'Fábrica de MVPs' e o Incubador de Ideias.",
                "endpoint": "/api/projects/from_idea",
                "modes": ["Projeto", "Ideia", "Arquitetura"],
            },
            {
                "name": "Agente de Código",
                "description": "Gera e refatora código.",
                "endpoint": "/api/code/generate",
                "modes": ["Código"],
            },
        ],
        "tools": tool_descriptions,
        "status_endpoint": "/api/status",
    }
    return capabilities


@app.post("/api/projects/new", response_model=DevProject)
def create_new_project(name: str, description: str) -> DevProject:
    workspace_path = f"D:\\NexusProjects\\{name.replace(' ', '_')}"
    try:
        os.makedirs(workspace_path, exist_ok=True)
        with open(
            os.path.join(workspace_path, "main.py"),
            "w",
            encoding="utf-8",
        ) as file_handle:
            file_handle.write(
                "# Projeto Nexus: "
                + name
                + "\n\ndef main():\n    print('Ola, Nexus!')\n\nif __name__ == '__main__':\n    main()\n"
            )
    except Exception as error:
        print(f"Erro ao criar pasta do projeto: {error}")

    new_project = DevProject(
        name=name,
        description=description,
        status="Capturada",
        progress=0,
        tech_stack=[],
        workspace_path=workspace_path,
        created_at=datetime.now().isoformat(),
        main_session_id=None,
    )
    with neo4j_driver.session() as session:
        session.run(
            "CREATE (p:DevProject {id: $id, name: $name, description: $description, status: $status, "
            "progress: $progress, workspace_path: $workspace_path, created_at: $created_at, "
            "main_session_id: $main_session_id, tech_stack: $tech_stack})",
            **new_project.model_dump(exclude_none=True),
        )
    return new_project


@app.get("/api/projects", response_model=List[DevProject])
def get_all_projects() -> List[DevProject]:
    with neo4j_driver.session() as session:
        result = session.run("MATCH (p:DevProject) RETURN p")
        return [DevProject(**record["p"]) for record in result]


@app.post("/api/projects/from_idea", response_model=DevProject)
def create_project_from_idea(input_data: IdeaInput) -> DevProject:
    structure = agente_arquiteto.structure_idea(input_data.text)

    workspace_root = os.getenv("NEXUS_PROJECTS_ROOT", "/app/NexusProjects")
    workspace_path = os.path.join(workspace_root, structure.name.replace(" ", "_"))
    os.makedirs(workspace_path, exist_ok=True)

    plan_path = os.path.join(workspace_path, "PLAN.md")
    with open(plan_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(
            f"# {structure.name}\n\n## Resumo do MVP\n{structure.mvp_summary}\n\n"
            "## Stack\n" + "\n".join(f"- {tech}" for tech in structure.tech_stack)
        )

    chat_session = create_chat_session(f"Chat: {structure.name}")

    new_project = DevProject(
        name=structure.name,
        description=structure.description,
        status="Em Pesquisa",
        progress=5,
        tech_stack=structure.tech_stack,
        workspace_path=workspace_path,
        created_at=datetime.now().isoformat(),
        main_session_id=chat_session.id,
    )

    with neo4j_driver.session() as session:
        session.run(
            "CREATE (p:DevProject {id: $id, name: $name, description: $description, status: $status, "
            "progress: $progress, workspace_path: $workspace_path, created_at: $created_at, "
            "main_session_id: $main_session_id, tech_stack: $tech_stack})",
            **new_project.model_dump(exclude_none=True),
        )
        session.run(
            """
            MATCH (p:DevProject {id: $pid}), (s:ChatSession {id: $sid})
            MERGE (p)-[:TEM_CHAT_DEDICADO]->(s)
            """,
            pid=new_project.id,
            sid=chat_session.id,
        )

    log_event(
        type="milestone",
        title="Novo Projeto Iniciado",
        description=(
            f"Projeto '{new_project.name}' foi criado a partir de uma ideia. MVP definido."
        ),
        agent="Agente Arquiteto",
        project_id=new_project.id,
    )

    return new_project


@app.get("/api/projects/{project_id}/files", response_model=List[FileNode])
def get_project_files(project_id: str) -> List[FileNode]:
    workspace_path = None
    with neo4j_driver.session() as session:
        result = session.run(
            "MATCH (p:DevProject {id: $id}) RETURN p.workspace_path as path",
            id=project_id,
        )
        record = result.single()
        if record:
            workspace_path = record["path"]

    if not workspace_path or not os.path.exists(workspace_path):
        raise HTTPException(status_code=404, detail="Projeto ou pasta não encontrada")

    return get_directory_structure(workspace_path)


@app.get("/api/timeline/logs", response_model=List[SystemLog])
def get_timeline_logs() -> List[SystemLog]:
    return database.get_recent_logs()


@app.get("/api/settings", response_model=SystemSettings)
def get_system_settings() -> SystemSettings:
    return database.get_settings()


@app.post("/api/settings")
def update_system_settings(settings: SystemSettings):
    try:
        database.save_settings(settings)
        return {"status": "success", "message": "Configurações salvas"}
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Erro ao salvar configurações: {error}"
        )


@app.get("/api/chat/sessions", response_model=List[ChatSession])
def get_sessions() -> List[ChatSession]:
    return get_all_sessions()


@app.get("/api/chat/{session_id}/messages", response_model=List[ChatMessage])
def get_messages(session_id: str) -> List[ChatMessage]:
    return get_chat_messages(session_id)


# Endpoint legacy renamed to support session handling.
@app.post("/api/chat/send", response_model=PerplexicaResponse)
def post_chat(
    input_data: ChatInput,
    background_tasks: BackgroundTasks,
) -> PerplexicaResponse:
    """Roteia o fluxo do chat utilizando o modo sugerido e o classificador central."""
    content = input_data.content
    suggested_mode = input_data.mode or "Chat Pessoal"
    session_id = input_data.session_id

    if not session_id:
        title = f"{content[:30]}..."
        new_session = create_chat_session(title=title)
        session_id = new_session.id

    user_message = ChatMessage(session_id=session_id, role="user", content=content)
    add_chat_message(user_message)
    if len(user_message.content) > 50:
        background_tasks.add_task(
            background_learning_task,
            user_message.content,
            "Chat Pessoal",
        )

    print(
        f"[Endpoint /api/chat/send] Recebido: '{content}' "
        f"(Modo Sugerido: {suggested_mode}, Sessao: {session_id})"
    )

    conversation_history = get_chat_messages(session_id)
    if not conversation_history or conversation_history[-1].content != content:
        conversation_history.append(user_message)

    history_for_classifier = [
        {"role": message.role, "content": message.content}
        for message in conversation_history[-10:]
    ]

    final_mode = suggested_mode
    intent_payload: Dict[str, Any] | None = None
    if suggested_mode in ("Modo: Chat Pessoal", "Chat Pessoal"):
        classification_result = agente_central.classify_intent(
            content,
            history_for_classifier,
        )
        if isinstance(classification_result, tuple):
            final_mode, intent_payload = classification_result
        else:
            final_mode = classification_result
    print(f"[Roteador Principal] Modo Final Decidido: {final_mode}")

    assistant_answer: str
    sources: List[Dict] = []

    if final_mode == "Pesquisa Profunda":
        print("[Endpoint /api/chat/send] Roteando para Agente de Pesquisa...")
        search_result = agente_pesquisa.search(content)
        assistant_answer = search_result["answer"]
        sources = search_result.get("sources", [])
        background_tasks.add_task(
            background_learning_task, search_result["answer"], content
        )
    elif final_mode == "Noticias":
        print("[Endpoint /api/chat/send] Roteando para Agente de Noticias...")
        news_result = agente_noticias.search_news(content)
        return PerplexicaResponse(
            answer=news_result["answer"],
            sources=news_result["sources"],
            session_id=session_id,
        )
    elif final_mode == "Chat Pessoal":
        print(
            "[Endpoint /api/chat/send] MODO: Conversa Pessoal. Chamando Agente de Chat (LLM)."
        )

        assist_content, assist_sources = generate_chat_response(
            content,
            conversation_history,
            session_id,
            current_message_id=user_message.id,
        )
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=assist_content,
        )
        add_chat_message(assistant_message)

        return PerplexicaResponse(
            answer=assist_content,
            sources=assist_sources,
            session_id=session_id,
        )
    elif final_mode == "Executar Ferramenta":
        print(
            "[Endpoint /api/chat/send] OFBD ativo. Executando ferramenta sugerida pelo DeepSeek."
        )
        tool_plan = intent_payload or {}
        tool_name = tool_plan.get("tool_name")
        arguments = tool_plan.get("arguments") or {}

        if not tool_name:
            raise HTTPException(
                status_code=400,
                detail="Plano de ferramenta inválido: nome não fornecido.",
            )

        try:
            tool_result = agente_executor.execute_dynamic_tool(tool_name, arguments)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))
        except RuntimeError as error:
            raise HTTPException(status_code=500, detail=str(error))
        assistant_answer = synthesize_tool_response(content, tool_name, tool_result)
        sources = []
    elif final_mode == "Ideia":
        print(
            "[Endpoint /api/chat/send] Roteando para Incubador de Ideias (Agente Arquiteto)..."
        )
        try:
            agente_arquiteto.process_new_idea(content)
            assistant_answer = (
                "Incrível! Capturei sua ideia, gerei objetivos iniciais e criei um lembrete proativo "
                "para o próximo passo. Você pode acompanhar na Caixa de Entrada."
            )
        except Exception as error:
            print(f"[Endpoint /api/chat/send] Erro ao incubar ideia: {error}")
            raise HTTPException(
                status_code=500,
                detail="Não consegui processar a ideia agora. Tente novamente em instantes.",
            )
    elif final_mode in ["Lembrete", "Projeto", "Nota Simples", "Lista"]:
        print("[Endpoint /api/chat/send] Roteando para Caixa de Entrada (Neo4j)...")
        try:
            new_item = InboxItem(
                content=content,
                type=final_mode,
                created_at=datetime.now().isoformat(),
            )
            create_inbox_item(new_item)
            assistant_answer = f"Entendido. Classifiquei como '{final_mode}' e salvei na sua Caixa de Entrada."
        except Exception as error:
            print(f"[Endpoint /api/chat/send] Erro ao salvar no Neo4j: {error}")
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar na Caixa de Entrada.",
            )
    else:
        assistant_answer = (
            "Ola! (Modo Conversa ainda em implementacao. "
            f"Mas entendi que voce disse: '{content}')"
        )

    assistant_message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=assistant_answer,
    )
    add_chat_message(assistant_message)

    return PerplexicaResponse(
        answer=assistant_answer,
        sources=sources,
        session_id=session_id,
    )


@app.get("/status")
def get_system_status():
    monitored = ["Neo4j", "ChromaDB", "DeepSeek"]
    services_status: Dict[str, Dict[str, Any]] = {}
    failed_services: Dict[str, str] = {}

    for service in monitored:
        healthy, detail = check_service_health(service)
        services_status[service] = {"healthy": healthy, "detail": detail}
        if not healthy:
            failed_services[service] = detail

    diagnostic_message = (
        agente_central.generate_diagnostic_message(failed_services)
        if failed_services
        else "Todos os serviços operacionais."
    )

    return {
        "services": services_status,
        "diagnostic": diagnostic_message,
    }


@app.get("/api/memory/graph", response_model=GraphData)
def get_memory_graph() -> GraphData:
    """
    Retorna todos os nós e relacionamentos do Neo4j para visualização.
    """
    nodes: List[GraphNode] = []
    links: List[GraphLink] = []

    with neo4j_driver.session() as session:
        result_nodes = session.run(
            "MATCH (n) RETURN elementId(n) as id, labels(n) as labels, properties(n) as props"
        )
        for record in result_nodes:
            labels = record["labels"]
            label = labels[0] if labels else "Unknown"
            nodes.append(
                GraphNode(
                    id=record["id"],
                    label=label,
                    properties=_serialize_neo4j_value(dict(record["props"])),
                )
            )

        result_links = session.run(
            "MATCH (a)-[r]->(b) RETURN elementId(a) as source, elementId(b) as target, type(r) as type"
        )
        for record in result_links:
            links.append(
                GraphLink(
                    source=record["source"],
                    target=record["target"],
                    type=record["type"],
                )
            )

    return GraphData(nodes=nodes, links=links)


@app.get("/api/inbox/items", response_model=List[InboxItem])
def list_inbox_items():
    return get_inbox_items()


@app.get("/api/inbox/chat/{item_id}", response_model=List[ChatMessage])
def get_proactive_chat(item_id: str):
    messages = get_chat_messages(item_id)

    if not messages:
        item = get_inbox_item_by_id(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item não encontrado")

        proactive_content = get_proactive_message_by_rule(
            item.type,
            item.content,
        )
        first_message = ChatMessage(
            session_id=item_id,
            role="assistant",
            content=proactive_content,
        )
        add_chat_message(first_message)
        return [first_message]

    return messages


@app.post("/api/inbox/chat/{item_id}", response_model=List[ChatMessage])
def post_proactive_chat_response(
    item_id: str, input_data: ChatInput
) -> List[ChatMessage]:
    """
    Recebe a RESPOSTA do usuario no Chat Dedicado,
    processa a intencao, chama o Agente Executor e
    retorna o novo historico de chat.
    """
    user_content = input_data.content
    print(f"[Endpoint /api/inbox/chat/{item_id}] Recebida resposta: {user_content}")

    user_message = ChatMessage(
        session_id=item_id,
        role="user",
        content=user_content,
    )
    add_chat_message(user_message)

    positive_responses = ["sim", "ok", "confirma", "pode", "gostaria", "faca"]

    if any(res in user_content.lower() for res in positive_responses):
        print(
            f"[Endpoint /api/inbox/chat/{item_id}] Intencao positiva detectada. Acionando Agente Executor..."
        )

        item = get_inbox_item_by_id(item_id)

        if item:
            status_report = agente_executor.execute_task(item.type, item.content)
            executor_message = ChatMessage(
                session_id=item_id,
                role="assistant",
                content=status_report,
            )
            add_chat_message(executor_message)
        else:
            error_msg = ChatMessage(
                session_id=item_id,
                role="assistant",
                content="Desculpe, nao consegui encontrar o item original para executar a tarefa.",
            )
            add_chat_message(error_msg)
    else:
        fallback_msg = ChatMessage(
            session_id=item_id,
            role="assistant",
            content="Entendido. Deixarei como esta por enquanto.",
        )
        add_chat_message(fallback_msg)

    return get_chat_messages(item_id)


@app.post("/api/code/generate", response_model=CodeResponse)
def generate_code_endpoint(request: CodeGenerateRequest):
    """
    Endpoint para o botao "Gerar" do frontend.
    Chama o Agente de Codigo para gerar novo codigo.
    """
    print(f"[Endpoint /api/code/generate] Recebido prompt: {request.prompt}")
    new_code = agente_codigo.generate_code(request.prompt)
    return CodeResponse(code=new_code)


@app.post("/api/code/refactor", response_model=CodeResponse)
def refactor_code_endpoint(request: CodeRefactorRequest):
    """
    Endpoint para o botao "Refatorar" do frontend.
    Chama o Agente de Codigo para refatorar o codigo existente.
    """
    print(
        f"[Endpoint /api/code/refactor] Recebido {len(request.code)} caracteres para refatorar."
    )
    refactored_code = agente_codigo.refactor_code(request.code)
    return CodeResponse(code=refactored_code)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
