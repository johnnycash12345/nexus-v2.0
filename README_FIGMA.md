# Nexus v2.0 — Blueprint para o Time de Figma

Este documento descreve, em linguagem orientada para designers, tudo o que o frontend precisa entregar para operar com o backend do Nexus v2.0. Use-o como referência única ao desenhar fluxos, componentes e handoff para o time de desenvolvimento.

---

## 1. Objetivo e Persona

| Item | Detalhe |
| --- | --- |
| **Produto** | Cockpit cognitivo tipo Perplexity que orquestra agentes, ferramentas externas e memória híbrida. |
| **Usuário-alvo** | Pesquisadores e builders técnicos que alternam entre pesquisa, planejamento, execução de ideias e chat pessoal. |
| **Tom visual** | “Mission Control” — clean, alto contraste, foco em legibilidade e telemetria em tempo real. Priorizar modo escuro. |

---

## 2. Layout Global

1. **Sidebar persistente (240 px)**  
   - Logo + status breve (online/offline).  
   - Navegação em blocos: Cockpit, Pesquisa, Chat, Projetos, Inbox, Código, Monitoramento.  
   - CTA inferior (“Nova Ideia” → abre modal para `process_new_idea`).

2. **Header contextual (64 px)**  
   - Breadcrumb da área ativa.  
   - Botão “Executar Ferramenta” (abre drawer com ferramentas registradas).  
   - Avatar do usuário + menu rápido (Configurações, Status, Logs).

3. **Área de Trabalho**  
   - Painel mestre com cartões ou chats (depende da rota).  
   - Painel lateral secundário (opcional) para contextos: fontes, memória, timeline.

4. **Feedback**  
   - Toast stack (cantos superiores) para confirmações/erros.  
   - Barra de progresso fina no topo para chamadas de API longas.

---

## 3. Mapa de Experiências

| Seção | Descrição visual | API principal |
| --- | --- | --- |
| **Cockpit / Pesquisa Profunda** | Feed com resultados RAG, cards de ferramenta e citações. Composer flutuante com prompt + anexos de contexto. | `POST /api/chat/send` |
| **Chat Pessoal** | Conversa “bolha” com avatar do Nexus, timeline de fontes, chips com ações rápidas. | `POST /api/chat/send` (modo chat) |
| **Projetos & Arquitetura** | Grade de projetos + sidebar com `process_new_idea`. Cada projeto abre aba com arquivos (árvore) e timeline. | `POST /api/projects/new`, `GET /api/projects` |
| **Inbox / Lembretes** | Lista tipo kanban/lista, filtros por tipo (`Lembrete`, `Projeto`, `Ideia`). Item abre chat proativo. | `GET /api/inbox/items`, `GET/POST /api/inbox/chat/{id}` |
| **Código Assistido** | Editor dual-pane, botões “Gerar”/“Refatorar” com outputs plain text. | `POST /api/code/generate`, `POST /api/code/refactor` |
| **Monitoramento** | Cartões com status de Neo4j, Chroma, DeepSeek + logs recentes. Link para `/status`. | `GET /status` |
| **Memória Gráfica** | Visualização force-directed ou lista, com filtros e detalhes ao clicar em nós. | `GET /api/memory/graph` |

---

## 4. Componentes-Chave

| Componente | Requisitos |
| --- | --- |
| **Composer Híbrido** | Campo multiline + tag de modo (Pesquisa, Chat, Ideia). Ações: anexar link, inserir ficheiro, escolher ferramenta. Mostrar contagem de tokens e estado (“Simulando comando”, “Orquestrando ferramenta”). |
| **Cartão de Resultado** | Inclui badge da fonte (Tavily, NASA, etc.), título, snippet, botões “Salvar no Inbox” / “Executar Ferramenta Relacionada”. |
| **Console de Ferramentas (OFBD)** | Drawer com lista formatada via `get_tool_descriptions()`. Cada item mostra descrição e parâmetros. Deve permitir edição manual antes de enviar. |
| **Timeline / Logs** | Estilo lista vertical com ícones por agente (`Agente Executor`, `NQR`, `Guardião`). Mostrar timestamp ISO curto. |
| **Toasts & Inline Alerts** | Severidades: info, success, warning, danger. Usar cores consistentes (ex.: Azul 400, Verde 400, Amarelo 400, Vermelho 400). |
| **Grafos & Métricas** | Cards com badges de status (OK/Degradado/Offline). Exibir mensagem de diagnóstico vinda de `generate_diagnostic_message`. |

---

## 5. Estados e Fluxos Necessários

1. **Envio de prompt**  
   - `Idle → Simulando (spinner) → Resposta`  
   - Mostrar chips “Ferramenta Sugerida” quando `final_mode == "Executar Ferramenta"`.

2. **Execução de Ferramentas**  
   - Drawer com parâmetros pré-preenchidos (payload do OFBD).  
   - Estado “Em execução” + log textual (exibir JSON retornado).  
   - Resposta final sintetizada (usar componente de blocos markdown).

3. **Incubação de Ideias**  
   - Modal “Registrar Ideia”. Campos: Título, Descrição, Impacto.  
   - Mostrar preview de entidades `objective`, `next_action`, `resources_needed`.  
   - Após confirmação, banner “Lembrete Proativo criado”.

4. **Status / Falha de serviços**  
   - Card vermelho quando `check_service_health` falhar; mostrar `diagnostic`.  
   - CTA “Tentar novamente” → dispara nova chamada `GET /status`.

---

## 6. Contractos de API Relevantes

| Endpoint | Método | Payload principal | Observações de UI |
| --- | --- | --- | --- |
| `/api/chat/send` | POST | `{ "content": str, "session_id": str }` | Resposta `PerplexicaResponse`: `answer`, `sources`, `session_id`. Renderizar `sources` como lista clicável. |
| `/api/inbox/items` | GET | – | Retorna lista de `InboxItem {id, content, type}`. Mostrar filtros por `type`. |
| `/api/inbox/chat/{id}` | GET/POST | `ChatInput { content }` | Usar para conversas proativas (Executar Tarefa). Mostrar marcador “Agente Executor”. |
| `/api/projects/new` | POST | `{ "title": str, "description": str }` | Após criação, atualizar grade de projetos. |
| `/api/projects/{id}/files` | GET | – | Resulta em árvore de `FileNode`. Usar componente colapsável. |
| `/api/code/generate` / `refactor` | POST | `CodeGenerateRequest { prompt }` ou `CodeRefactorRequest { code }` | Exibir output em bloco `pre`, com botão "Copiar". |
| `/api/memory/graph` | GET | – | Consumir para renderizar grafo (use fallback “lista” se WebGL não estiver disponível). |
| `/status` | GET | – | Retorna `{ services: {Neo4j: {healthy, detail}, ...}, diagnostic }`. Mostrar cards e mensagem do diagnostic. |

### Componentes ↔ Endpoint ↔ Payload

| Componente | Endpoint | Payload (request) | Expectativa de UI |
| --- | --- | --- | --- |
| Composer Pesquisa/Chat | `POST /api/chat/send` | `{"session_id":"uuid","content":"texto"}` | Mostrar estado “Simulando/Executando ferramenta” e renderizar `PerplexicaResponse`. |
| Drawer OFBD (Executar Ferramenta) | (payload interno) | `{"tool_name":"news_search","arguments":{"query":"IA","max_results":3}}` | Preencher campos da ferramenta com os argumentos validados e exibir resultado sintetizado. |
| Modal Nova Ideia | `POST /api/projects/from_idea` | `{"text":"Minha ideia..."}` | Após resposta `DevProject`, exibir preview das entidades `objective`, `next_action`, `resources_needed`. |
| Monitor de Status | `GET /status` | – | Cards coloridos por serviço + mensagem do campo `diagnostic`. |
| Inbox Proativo | `GET/POST /api/inbox/chat/{id}` | `{"content":"sim"} (POST)` | Interface de chat com badges do Agente Executor; confirmar execução quando resposta sinalizar sucesso. |

--- 

## 7. Guia Visual

- **Tipografia**: Preferir Inter ou Space Grotesk. Títulos 20 px/semibold, corpo 14 px/regular.  
- **Paleta**:  
  - Fundo primário `#050B15`  
  - Cartões `#101726`  
  - Acento primário `#52E1F4` (links, ícones ativos)  
  - Acento secundário `#A855F7` (estados inteligentes)  
  - Erro `#F87171`, Sucesso `#4ADE80`, Aviso `#FACC15`
- **Ícones**: usar coleção linear (Lucide) e manter consistência 20 px.
- **Auto Layout**: obrigatório em todos os frames; gutters 24 px horizontais / 16 px verticais.
- **Modo Responsivo**: criar variantes desktop (1440 px) e laptop (1280 px); mobile não prioritário.

---

## 8. Checklist de Entrega

1. Componentes tokenizados (cores, spacings, tipografia em Styles).  
2. Design Tokens exportáveis (JSON ou plugin Figma Tokens).  
3. Flows etiquetados com IDs iguais aos endpoints (ex.: “/api/chat/send”).  
4. Anotações de estados vazios, erros, loading e sucesso.  
5. Hand-off com descrições (`alt + enter`) citando campos JSON que devem preencher cada componente.  
6. Prototipagem interativa:  
   - Envio de prompt  
   - Execução de ferramenta sugerida  
   - Criação de ideia + lembrete  
   - Consulta de status

Com este blueprint, o time de Figma consegue alinhar pixel-perfeito com o backend do Nexus garantindo que cada componente saiba qual dado consumir e como reagir aos estados dos agentes.
