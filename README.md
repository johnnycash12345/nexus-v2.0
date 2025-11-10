# nexus-v2.0

## Nexus v1.0 - Multi-Agent Research Orchestrator

> Plataforma cognitiva que orquestra LLMs, ferramentas externas e memorias hibridas para executar pesquisas, gerar codigo e consolidar conhecimento.

## Tabela de conteudo
- [Visao geral](#visao-geral)
- [Destaques do sistema](#destaques-do-sistema)
- [Arquitetura completa](#arquitetura-completa)
- [Componentes do backend](#componentes-do-backend)
- [Modelo de dados e contratos](#modelo-de-dados-e-contratos)
- [Frontend](#frontend)
- [Configuracao e execucao](#configuracao-e-execucao)
- [Observabilidade e seguranca](#observabilidade-e-seguranca)
- [Extensibilidade](#extensibilidade)
- [Operacao e troubleshooting](#operacao-e-troubleshooting)
- [Roadmap de evolucao](#roadmap-de-evolucao)
- [Recursos adicionais](#recursos-adicionais)

## Visao geral

O Nexus v1.0 foi projetado como um cockpit de pesquisa inspirado em assistentes tipo Perplexity. O fluxo central integra:
- Classificacao dinamica de intencao com DeepSeek/OpenAI/Ollama.
- Planejamento de busca, orquestracao de ferramentas e sintese final (RAG completo).
- Consolidacao de conhecimento em grafo sem forcar o usuario a repetir interacoes.
- Frente unica para conversa, pesquisa, desenvolvimento guiado e acompanhamento de projetos.

## Destaques do sistema
- **Multi-provedor LLM:** DeepSeek (principal), OpenAI, Perplexity API, Ollama offline e fallback heuristico.
- **Orquestracao multiagente:** cada etapa possui um agente dedicado, com logs e monitoramento.
- **Memorias complementares:** Neo4j (long-term grafo e timeline) + ChromaDB (memoria de curto prazo por sessao).
- **Controle de uso de APIs:** `usage_tracker.py` bloqueia sobrecarga conforme limites definidos em `api_limits.py`.
- **Interface completa:** React + Vite com Radix UI, CMDK, embla-carousel e sistema de notificacoes.
- **Genesis Protocol:** quando o grafo esta vazio, seeds de consciencia sao implantadas automaticamente.
- **Executor com guardiao:** tarefas confirmadas passam por `agente_executor` e podem ser avaliadas pelo `agente_guardiao` antes de aplicacao de diffs.

## Arquitetura completa

```
User
  |
  v
Frontend (Vite/React SPA)
  |
  v
Backend FastAPI (`backend/main.py`)
    |-- Agente Central      (classifica intencao / escolhe provedor)
    |-- Agente Pesquisa     (planejamento + RAG)
    |-- Agente Noticias     (briefings recentes)
    |-- Agente Executor     (tarefas Inbox/Projetos)
    |-- Agente Codigo       (generate/refactor)
    |-- Agente Arquiteto    (planner de MVPs)
    |-- Agente Consolidacao (triples de conhecimento)
    |-- Agente Guardiao     (checagem de seguranca)
    |
    +--> Ferramentas externas (Tavily, NASA APOD, DuckDuckGo News, ...)
    |
    +--> Memorias
          |-- ChromaDB HTTP (historico de chat por sessao)
          |-- Neo4j (grafo, projetos, logs, settings, Genesis)
```

Armazenamento adicional:
- `executor_log.txt` guarda execucoes do agente executor.
- `daily_usage.json` armazena contadores diarios de uso de APIs.
- Workspaces de projetos sao criados em `D:\NexusProjects\<nome>` por default.

### Pipeline principal (Pesquisa Profunda)
1. `POST /api/chat/send` recebe `ChatInput`.
2. `agente_central.classify_intent` escolhe modo, provedor e modelo.
3. `agente_pesquisa.plan_research` usa DeepSeek para definir ferramenta e query otimizadas.
4. `ferramentas.py` executa a API (Tavily, NASA, DDG etc.).
5. `_normalize_tool_output` formata contexto e fontes.
6. DeepSeek sintetiza resposta final com citacoes.
7. `background_learning_task` extrai triplas com `agente_consolidacao` e salva via `database.save_knowledge_triples`.
8. Historico e memo RAG ficam disponiveis para refinamentos posteriores.

### Demais fluxos
- **Chat Pessoal:** `generate_chat_response` coleta historico recente do ChromaDB, consulta Neo4j/Chroma via `retrieve_long_term_context` e chama DeepSeek para resposta contextual.
- **Noticias:** `agente_noticias.search_news` gera briefing em PT-BR traduzindo urgente.
- **Lembretes/Projetos/Notas:** criam `InboxItem` no Neo4j e ficam prontos para follow-up com o Executor.
- **Projetos estruturados:** `agente_arquiteto.structure_idea` gera `PLAN.md`, workspace local e chat dedicado.
- **Codigo:** `agente_codigo` gera/refatora com DeepSeek Coder e opcionalmente passa pelo Guardiao.

## Componentes do backend

| Arquivo | Descricao |
| --- | --- |
| `main.py` | FastAPI app, endpoints REST, lifespan (Genesis), background tasks, orquestracao geral. |
| `models.py` | Tipos Pydantic (ChatMessage, InboxItem, DevProject, SystemSettings etc.). |
| `agente_central.py` | Router de intencao com heuristica offline, DeepSeek e OpenAI; escolhe provedor LLM. |
| `agente_pesquisa.py` | Pipeline RAG completo (planejamento, execucao de ferramentas, normalizacao, sintese). |
| `agente_noticias.py` | Busca e resumo de noticias (DuckDuckGo + DeepSeek). |
| `agente_consolidacao.py` | Extrai triplas (source, relationship, target) de qualquer texto. |
| `agente_executor.py` | Registra tarefas confirmadas, persiste log e responde ao usuario. |
| `agente_codigo.py` | Gera/refatora codigo com DeepSeek Coder. |
| `agente_arquiteto.py` | Converte ideias em estrutura de projeto (name, description, tech_stack, tarefas, MVP). |
| `agente_guardiao.py` | Valida diffs de codigo buscando riscos (exfiltracao, destrucao, backdoor). |
| `main.py` (`generate_chat_response`) | Agente de conversa pessoal que combina memoria curta com RAG em Neo4j/Chroma (DeepSeek). |
| `database.py` | Persistencia em Neo4j e ChromaDB, logs, configuracoes, timeline, knowledge triples. |
| `db_connect.py` | Inicializa conexoes (retry com ChromaDB), expone `neo4j_driver` e `chroma_client`. |
| `ferramentas.py` | Registro dinamico de ferramentas, wrappers com limitador de uso. |
| `usage_tracker.py` | Controle diario de chamadas com `daily_usage.json`. |
| `api_limits.py` | Limites pre-configurados para APIs comuns. |
| `genesis.py` | Protocolo inicial para semear nos SELF/CREATOR/INITIAL_CURIOSITY. |
| `teste_aprendizado.py` | Script manual para validar pipeline de aprendizagem (consolidacao + Neo4j). |

### Dependencias Python (`backend/requirements.txt`)
- FastAPI, Uvicorn, Pydantic, CORS
- `neo4j`, `chromadb-client`, `sentence-transformers`, `onnxruntime`
- `openai` (cliente universal utilizado para DeepSeek e outros provedores compat)
- `tavily-python`, `requests`, `python-dotenv`

### Configuracoes dinamicas (`SystemSettings`)
`database.get_settings()` carrega/gera `SystemSettings` contendo:
- Modo (turbo, balanced, economic, offline).
- Provedores (OpenAI, Google, DeepSeek, Perplexity) com flags `enabled`, `api_key`, `model_name`.
- Modelo Ollama para modo offline.
- `fallback_enabled` para decidir quando usar heuristicas locais.

Atualize via `POST /api/settings` com payload completo do objeto `SystemSettings` (Pydantic cuida de defaults).

### Lifespan e background
- `lifespan` chama `genesis.perform_genesis()` se o grafo estiver vazio.
- `background_learning_task` roda assincronamente para nao bloquear resposta ao usuario.
- Logs de cada agente sao emitidos no console e podem ser capturados por agregadores externos.

## Modelo de dados e contratos

### Modelos Pydantic principais

| Modelo | Campos relevantes |
| --- | --- |
| `ChatInput` | `content`, `mode`, `session_id` (opcional). |
| `ChatMessage` | `id` (UUID), `session_id`, `role`, `content`. |
| `PerplexicaResponse` | `role` (assistant), `answer`, `sources[]`, `session_id`. |
| `InboxItem` | `id`, `content`, `type`, `created_at`. |
| `DevProject` | `id`, `name`, `description`, `status`, `progress`, `tech_stack[]`, `workspace_path`, `main_session_id`. |
| `SystemLog` | `timestamp`, `type`, `title`, `description`, `agent`, `project_id`. |
| `SystemSettings` | `general` (idioma, tema, autosave) + `ai` (modo, provedores). |

### Contratos HTTP (exemplos)

`POST /api/chat/send`
```json
{
  "content": "Qual a diferenca entre fusao e fissao nuclear?",
  "mode": "Chat Pessoal",
  "session_id": null
}
```

Resposta (modo Pesquisa Profunda):
```json
{
  "role": "assistant",
  "answer": "Fusao combina nucleos leves liberando energia...",
  "sources": [
    {"title": "IAEA - Nuclear Fusion Basics", "url": "https://www.iaea.org/..."},
    {"title": "MIT News - Nuclear Fission Explained", "url": "https://news.mit.edu/..."}
  ],
  "session_id": "1b7d3a43-..."
}
```

`POST /api/projects/from_idea`
```json
{
  "text": "Quero construir um painel que monitora satelites de clima e gera alertas."
}
```

Resposta:
```json
{
  "id": "c5f1...",
  "name": "Climate Sentinel",
  "description": "Painel web para monitorar satelites meteorologicos",
  "status": "Em Pesquisa",
  "progress": 5,
  "tech_stack": ["React", "FastAPI", "Neo4j"],
  "workspace_path": "D:\\NexusProjects\\Climate_Sentinel",
  "main_session_id": "98df..."
}
```

### Estrutura de persistencia

```
Neo4j
  :InboxItem {id, content, type, created_at}
  :ChatSession {id, title, created_at, updated_at}
  :SystemLog {id, type, title, agent, description}
  :DevProject {id, status, progress, tech_stack[]}
  :Conceito / :Entity / :Impulse (genesis e know-how)

ChromaDB
  Colecao chat_<session_id>
    ids -> UUID da mensagem
    documents -> conteudo da mensagem
    metadatas -> {role, timestamp}
```

`usage_tracker.py` guarda contagens no arquivo `backend/daily_usage.json`, reiniciado diariamente.

## Frontend

Repositorio monorepo: frontend na raiz (`src/`) e backend em `backend/`.

- **Tecnologias:** React 18, Vite 6, Radix UI, CMDK, Embla Carousel, Lucide Icons, Tailwind-merge, Sonner notifications.
- **Guides:** Documentacao completa em `src/NEXUS_DOCUMENTATION.md`, quick start em `src/QUICK_START.md`, exemplos de integracao em `src/API_INTEGRATION_EXAMPLES.md`.
- **Modulos principais:**
  - Search & Chat (perguntas orquestradas com fontes).
  - Personal Chat (conversa livre + memorizacao).
  - Development (editor com gerar/refatorar/executar/deploy).
  - Projects & Ideas (pipeline Kanban).
  - Timeline & Logs (linha do tempo colorida).
  - Synaptic Memory (grafo interativo + list view).
  - Cognitive Monitor (status dos 3 agentes principais).
- UI responsiva para desktop (>= 1280px), tema dark com ciano, roxo e dourado.

## Configuracao e execucao

### Requisitos
- Python 3.11+
- Node.js >= 18
- Docker (opcional mas recomendado para Neo4j/ChromaDB)
- Acesso a APIs externas utilizadas

### Variaveis de ambiente (`backend/.env`)

| Variavel | Obrigatoria | Descricao |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | Sim | Usada por todos os agentes que conversam com DeepSeek. |
| `OPENAI_API_KEY` | Nao | Usada se `SystemSettings.ai.openai.enabled` for true. |
| `TAVILY_API_KEY` | Nao | Ativa ferramenta Tavily (pesquisa web). |
| `NASA_API_KEY` | Nao | Ativa APOD na ferramenta NASA. |
| `NEO4J_URI` | Sim | Default `bolt://localhost:7687`. |
| `NEO4J_USER` | Sim | Default `neo4j`. |
| `NEO4J_PASSWORD` | Sim | Default `nexuspassword123`. Troque em producao. |
| `CHROMA_HOST` | Sim | Default `localhost`. |
| `CHROMA_PORT` | Sim | Default `8005` (exposto por docker-compose). |

### Levantando ambiente completo

```
# 1. Clonar repositorio
git clone https://github.com/<org>/nexus-v1.git
cd nexus-v1.0

# 2. Subir bancos (opcional mas recomendado)
cd backend
docker-compose up -d

# 3. Backend Python
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 4. Frontend
cd ..
npm install
npm run dev
```

URL padrao: `http://localhost:5173` (frontend) comunicando com `http://localhost:8000`.

### Scripts uteis
- `backend/teste_aprendizado.py`: smoke test do pipeline de aprendizado (necessita Neo4j ativo).
- `docker-compose.yml`: levanta Neo4j 5 Community e ChromaDB HTTP.
- Ajuste `NEO4J_AUTH` no compose para ambiente seguro.

## Observabilidade e seguranca

- **Logs estruturados:** cada agente imprime prefixos `[Agente X]` facilitando ingestao por sistemas externos.
- **SystemLog** (`database.create_log`): grava eventos com timestamp ISO; accessivel via `/api/timeline/logs`.
- **Agente Guardiao:** valida diffs antes de aplicar (ideal integrar ao pipeline de CI se for executar codigo).
- **Controle de chaves:** `register_tool` ignora ferramentas sem chave, evitando erros ruidosos.
- **Fallback offline:** modo OFFLINE usa heuristica local evitando chamadas externas (util para ambientes restritos).
- **Genesis**: roda apenas uma vez; para reiniciar seeds limpe o banco Neo4j.

## Extensibilidade

### Adicionando novas ferramentas de pesquisa
```python
def _tool_biorxiv(query: str) -> str:
    data = consulta_api(query)
    return json.dumps(data["results"])

register_tool(
    "biorxiv_search",
    "Artigos recentes do BioRxiv.",
    _tool_biorxiv,
    required_env_var="BIORXIV_API_KEY",
    limit_key="biorxiv"
)
```

### Criando novos agentes
- Crie `backend/agente_<nome>.py` com funcoes claras.
- Importe no `main.py` ou modulos relevantes.
- Se produzir side effects, registre logs via `log_event`.

### Aprimorando o RAG
- Ajuste `retrieve_long_term_context` para filtrar tipos especificos de nos ou colecoes (ex.: Conceito, Projeto).
- Inclua metadados adicionais (url, timestamp) nas fontes retornadas para exibicao no frontend.
- Aumente `n_results` e use filtros semanticos em ChromaDB conforme necessidade.

### Ajustando fluxo de intencao
- Atualize `agente_central.get_best_model_for_task` para suportar novos providers.
- Inclua novas categorias na lista `valid_intents`.
- Trate o novo modo no endpoint `/api/chat/send`.

### Enriquecendo memoria
- Use `agente_consolidacao.extract_knowledge(texto)` para alimentar grafo com novos documentos.
- Considere criar endpoints dedicados para uploads (PDF, Markdown) e reusar o extrator.

## Operacao e troubleshooting

- **ChromaDB indisponivel:** `db_connect` tenta reconectar 5 vezes. Ajuste `max_retries`/`retry_delay` se necessario.
- **Limite atingido:** confira `backend/daily_usage.json`. Para reset manual apague o arquivo (sem estar rodando).
- **Intencao incorreta:** revise `SystemSettings.ai.mode` e habilite/desabilite provedores conforme necessidade.
- **Erro ao salvar na inbox:** cheque conexao Neo4j (`neo4j status`, credenciais). Logs apontam `Erro ao salvar no Neo4j`.
- **Guardiao rejeitando diffs:** analise justificativa retornada (ex: "REJEITADO: comando rm recursivo"). Ajuste prompt se for falso positivo.
- **Genesis repetido:** limpe banco se desejar reiniciar (`docker compose down -v`) antes de ligar novamente.
- **Desempenho:** monitore latencia de Tavily e DeepSeek; configure caches externos se necessario.

## Roadmap de evolucao
- WebSocket streaming de respostas e status dos agentes.
- Autenticacao (JWT) e RBAC para multi-usuarios.
- Pipelines assinc para consolidacao em lote.
- Integracao com vetorial local (FAISS) para documentos privados.
- Painel de administracao para limites e chaves.
- Testes automatizados (Pytest) cobrindo agentes e endpoints principais.
- Empacotamento docker completo (backend + frontend + bancos) com docker-compose extendido.

## Recursos adicionais
- `src/NEXUS_DOCUMENTATION.md`: guia completo da UI e fluxos.
- `src/API_INTEGRATION_EXAMPLES.md`: como consumir o backend a partir de outros clientes.
- `backend/executor_log.txt`: historico de tarefas processadas pelo executor (gera manualmente em runtime).
- `backend/daily_usage.json`: contadores dos limites de API (regenerado diariamente).
- `backend/README.md` (caso criado futuramente) pode detalhar scripts especificos.

## Fluxos operacionais comuns

### Pesquisa aprofundada com registro de conhecimento
1. Usuaria acessa Search & Chat e digita pergunta aberta (ex.: "Como funciona agricultura vertical?").
2. `agente_central` identifica como "Pesquisa Profunda" (modo balanced por padrao).
3. `agente_pesquisa` usa Tavily (ou fallback) para coletar fontes, normaliza e aciona DeepSeek.
4. Resposta R1 aparece com citacoes; usuario pode:
   - clicar em "Refinar Resposta" para enviar feedback e gerar R2,
   - clicar em "Salvar na Memoria" para persistir triplas no Neo4j.
5. Background task registra fatos importantes e linka com conceitos existentes.

### Transformando nota em projeto
1. Usuario envia "Quero avaliar viabilidade de app para monitorar florestas".
2. Intent classificada como "Projeto"; `InboxItem` criado em Neo4j.
3. Ao aceitar via Inbox Chat, `agente_arquiteto` transforma ideia em `DevProject`.
4. `PLAN.md` e workspace sao gerados; timeline recebe log do marco.

### Geracao/refatoracao de codigo
1. No modo Development, usuario seleciona arquivo ou cola trecho.
2. Ao clicar em "Gerar", `POST /api/code/generate` chama DeepSeek Coder.
3. Resultado pode ser enviado ao Guardiao antes de aplicar diff local.
4. Logs do console exibem a operacao e o arquivo `executor_log.txt` registra acao concluida.

### Conversa pessoal com memoria curta + RAG
1. Usuario escolhe modo Chat Pessoal e envia mensagem informal.
2. Backend monta `conversation_history` com as ultimas interacoes salvas no ChromaDB.
3. `retrieve_long_term_context` consulta Neo4j (conceitos, relacoes) e ChromaDB (mensagens semelhantes) para montar contexto.
4. `generate_chat_response` combina contexto longo + historico recente e envia prompt ao DeepSeek.
5. Resposta (com fontes) e persistida como mensagem da assistente, mantendo memoria curta atualizada.

## Configurando ambientes

### Perfis sugeridos
| Ambiente | Objetivo | Configuracoes tipicas |
| --- | --- | --- |
| Desenvolvimento | Iterar rapido com acesso completo aos logs | `SystemSettings.ai.mode = balanced`, chaves DeepSeek/Tavily reais, docker-compose local |
| QA/Staging | Validar integracoes com dados ficticios | Limitar `usage_tracker` para 5 chamadas/dia, base Neo4j limpa, seeds customizadas |
| Producao | Operacao real com usuarios | Autenticacao ativada (futuro), logs enviados a observabilidade externa, controle de permissoes no Neo4j |

### Deploy backend
- Empacotar com `uvicorn main:app --workers 4` atras de reverse proxy (NGINX/Traefik).
- Configurar health-check `/` em load balancer.
- Sincronizar `.env` via secrets manager.
- Backup recorrente dos volumes `neo4j_data` e `chroma_data`.

### Deploy frontend
- `npm run build` gera pacote em `dist/`.
- Servir via Vite preview, NGINX static ou CDN.
- Configurar variavel `VITE_API_BASE_URL` (se adotado) para apontar ao backend.

## Ajustando comportamento das IAs

### Selecionando provedores
- `SystemSettings.ai.mode` define estrategia geral:
  - `turbo`: prioriza modelos com maior capacidade (OpenAI+, Perplexity).
  - `balanced`: usa DeepSeek quando ativo, alterna com OpenAI para casos complexos.
  - `economic`: mantem DeepSeek ou Ollama para reduzir custo.
  - `offline`: bloqueia chamadas externas, ativa heuristica e Ollama local.
- `fallback_enabled` garante retorno heuristico se a internet cair.

### Parametros especificos
- `agente_pesquisa.plan_research`: `temperature=0.2`, `response_format=json` para obter tool/query.
- `agente_consolidacao.extract_knowledge`: `temperature=0.1` para maior determinismo.
- Ajuste `temperature` e `max_tokens` conforme necessidade adicionando kwargs nos `chat.completions`.

### Integrando Ollama
- Certifique-se que `OLLAMA_HOST` esteja acessivel.
- Atualize `settings.ai.ollama_model` (ex.: `"llama3.1:8b"`).
- Expanda `agente_central` para usar `client.chat.completions` do Ollama via biblioteca local (TODO).

## Customizacao de ferramentas

### Estrategia de registro
1. Criar funcao que encapsule a chamada externa e retorne string ou JSON.
2. Opcional: envolver em wrapper com `limit_key` para contabilizar uso.
3. Chamar `register_tool("nome", "descricao", func, required_env_var="API_KEY", limit_key="servico")`.

### Ferramentas existentes
| Nome | Descricao | Formato de retorno |
| --- | --- | --- |
| `tavily_search` | Busca ampla multi-fonte | JSON com `[{"title","url","content"}]` |
| `nasa_search` | NASA Astronomy Picture of the Day | Texto com resumo + link |
| `news_search` | DuckDuckGo News | JSON com arrays de noticias |

### Boas praticas
- Tratar erros retornando string `ERRO <nome>: mensagem`.
- Utilizar timeout baixo (`requests.get(..., timeout=10)`).
- Garantir que campos `title`/`url` existam para alimentar citacoes.

## Testes e garantia de qualidade

### Automacao sugerida
- **Pytest** para unidades dos agentes: testar `plan_research`, `_normalize_tool_output`, `usage_tracker`.
- **Testes de integracao**: subir Neo4j/Chroma em modo teste (pode usar fixtures) verificando endpoints com `httpx.AsyncClient`.
- **Contract tests**: validar schema de `PerplexicaResponse` e `DevProject`.
- **Lint**: adicionar `ruff`/`flake8` para padrao em Python e `eslint` para frontend (nao incluso por padrao).

### Testes manuais
- `python backend/teste_aprendizado.py` (requer `.env` e bancos).
- Collections Postman / Bruno:
  - `POST /api/chat/send` com modos diferentes.
  - `POST /api/projects/from_idea`.
  - `POST /api/code/generate`.
- Validar UI:
  - Salvar na memoria gera nova conexao em Synaptic Memory.
  - Timeline atualiza quando projeto, log ou pesquisa e concluida.

### Dados de teste
- Ajustar `usage_tracker` para limites baixos durante QA.
- Utilizar chaves de sandbox para APIs externas quando disponiveis.

## Monitoramento, logs e auditoria

- **Logs padrao**: console; cada agente prefixa mensagens (facilita filtragem).
- **executor_log.txt**: rastreia tarefas executadas (para auditoria ou debugging).
- **SystemLog via Neo4j**: exposto em `/api/timeline/logs`, pode ser exportado para SIEM.
- **Metrica manual**: contagem de `daily_usage.json` exibe uso acumulado.
- **Alertas**: configure watchers externos para detectar:
  - Erros de conexao com ChromaDB/Neo4j.
  - Limites de API atingidos.
  - Falha do Genesis (requer intervencao manual).

## Backup e manutencao
- **Neo4j**: snapshots diarias via `neo4j-admin dump` ou backup de volume Docker.
- **ChromaDB**: copiar volume `chroma_data` (consistente via downtime ou lock).
- **Arquivos locais**: `executor_log.txt` e workspaces podem ser arquivados conforme politica interna.
- **Rotacao de chaves**: atualizar `.env`, reiniciar backend, invalidar chaves antigas.
- **Atualizacao de dependencias**:
  - Backend: `pip install -U -r requirements.txt`.
  - Frontend: `npm update` (verificar breaking changes do Vite/Radix).

## Integracao com outros sistemas
- **Webhooks**: adicionar endpoint FastAPI que receba eventos externos e injete mensagens na inbox.
- **Calendario**: `agente_executor` pode ser expandido para chamar Google Calendar ou Outlook API.
- **Slack/Teams**: criar adaptador que escreva retorno do Nexus em canais e receba feedback.
- **Data Lakes**: exportar `SystemLog` e triplas do Neo4j para pipelines analiticos (Spark, dbt).

## FAQ

**O que acontece sem chaves externas?**  
`ferramentas.register_tool` ignora ferramentas sem credenciais. O Nexus funciona com heuristica offline + Ollama (se configurado), mas sem pesquisa externa.

**Como reexecutar o Genesis?**  
Pare o backend, limpe o banco Neo4j (ex.: `docker compose down -v`) e suba novamente. Ao detectar grafo vazio o Genesis roda automaticamente.

**Posso usar outro vector DB?**  
Sim. Substitua inicializacao em `db_connect.py` por cliente FAISS, Weaviate ou Qdrant e ajuste chamadas em `database` (metodos `add_chat_message` e `get_chat_messages`).

**Existe suporte a streaming?**  
Nao. O roadmap inclui WebSocket streaming; atualmente as respostas sao retornadas apos conclusao do pipeline.

**Como ajustar a linguagem das respostas?**  
`SystemSettings.general.language` define idioma preferido. Os prompts sistemicos instruem DeepSeek a responder em pt-BR; personalize mensagens de sistema para outro idioma.

## Glossario rapido
- **RAG (Retrieval Augmented Generation):** modelo combina consulta a fontes externas + LLM.
- **Memoria sinaptica:** representacao grafica de conhecimento persistido (Neo4j).
- **Genesis Protocol:** seeds iniciais do grafo (SELF, CREATOR, INITIAL_CURIOSITY).
- **InboxItem:** item pendente (lembrete, projeto, nota) aguardando acao.
- **PerplexicaResponse:** formato padrao de resposta do chat (compatibilidade com integra????es anteriores).
- **Tripla:** fato no formato `source` - `[relationship]` -> `target`.

## Estrutura do frontend (resumo)

```
src/
  main.tsx             # bootstrap React
  App.tsx              # layout base e rotas de modo
  index.css            # estilos globais
  components/
    chat/              # componentes do Search & Chat
    development/       # editores, paines de execucao
    projects/          # tabelas e cards de projetos
    timeline/          # timeline com logs
    memory/            # grafo e list view
    monitor/           # dashboards dos agentes
  styles/              # tokens de tema e utilitarios
  guidelines/          # docs de design interno
  NEXUS_DOCUMENTATION.md
  QUICK_START.md
  API_INTEGRATION_EXAMPLES.md
```

## Script e comandos uteis

| Acao | Comando |
| --- | --- |
| Rodar backend em modo dev | `cd backend && uvicorn main:app --reload` |
| Rodar backend em workers | `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4` |
| Rodar frontend | `npm run dev` |
| Build frontend | `npm run build` |
| Executar testes unitarios (sugestao) | `pytest backend/tests` (criar pasta `tests/`) |
| Reset contadores de API | Apagar `backend/daily_usage.json` (com backend parado) |
| Exportar logs do Neo4j | `cypher-shell "MATCH (l:SystemLog) RETURN l"` |

## Conhecidos limitacoes
- Sem autenticacao nativa; qualquer usuario com acesso ao backend pode consumir APIs.
- Sem fila distribuida; background tasks rodam inline no processo FastAPI (usar Celery/RQ se carga alta).
- Ferramentas externas dependem de estabilidade das APIs (trate `ERRO` nas respostas).
- Genesis sem versionamento; recomecar do zero elimina memoria adquirida.

---

Com este README uma IA ou desenvolvedor consegue reconstruir o sistema, entender cada agente e seus contratos, estender capacidades e operar o Nexus v1.0 em ambiente local ou hospedado.
