# Nexus Frontend v2 - Documentação Completa

## 🚀 Visão Geral

O Nexus é um sistema cognitivo de IA autônomo com interface desktop completa e altamente funcional. Este documento descreve todas as funcionalidades implementadas no frontend.

## 📐 Arquitetura de Navegação

### Sidebar Principal (16px width)
- **Logo Nexus** - Retorna à home
- **Nova Sessão (+)** - Inicia nova conversa
- **Search & Chat** - Interface de busca estilo Perplexity
- **Personal Chat** - Chat conversacional tradicional
- **Development** - Editor de código com IA
- **Projects & Ideas** - Gerenciamento de projetos
- **Timeline & Logs** - Histórico de decisões
- **Synaptic Memory** - Visualização do Graph DB
- **Cognitive Monitor** - Status dos agentes
- **Settings** - Configurações do sistema

---

## 🎯 Funcionalidades por Página

### 1. **Home (Search & Chat)**
Interface principal inspirada no Perplexity com recursos avançados.

**Modos de Operação:**
- **Chat Pessoal** - Conversas rápidas e diretas
- **Pesquisa Profunda** - Análise detalhada com relatórios
- **Desenvolvimento** - Geração e refatoração de código
- **Especialista** - Uso de memória sináptica para domínios específicos

**Recursos:**
- Input avançado com anexos, imagens e áudio (microfone)
- Sugestões contextuais baseadas no modo selecionado
- Sources, Answer e Related organizados
- Botões de ação: "Adicionar à Memória", "Ver Raciocínio", "Fixar"
- Indicador visual do modo ativo

**Estados:**
- Empty state com logo, modos e sugestões
- Chat state com mensagens e histórico
- Processing state com animação de agentes

---

### 2. **Personal Chat**
Chat conversacional tradicional com recursos de memória.

**Recursos:**
- Mensagens com avatares de usuário e assistente
- Timestamp em cada mensagem
- Ações por mensagem:
  - **Copy** - Copiar conteúdo
  - **Pin** - Fixar mensagem importante
  - **Sparkles** - Adicionar à memória sináptica
  - **ChevronDown** - Ver cadeia de raciocínio (ReAct)
  - **ThumbsUp/Down** - Feedback de qualidade
- Indicador de digitação do assistente
- Input com anexos

**Integração com Memória:**
- Botão de aprovação de conhecimento
- Confirmação visual ao adicionar à memória
- Link direto para Graph View

---

### 3. **Development (Code Page)**
Editor de código completo com IA e deploy.

**Painel Esquerdo - Navegação de Arquivos:**
- Árvore de arquivos e pastas
- Ícones diferenciados (folder/file)
- Seleção de arquivo ativa
- Upload de arquivos

**Painel Central - Editor:**
- Syntax highlighting (simulado)
- Linha e coluna atuais
- Indicador de linguagem
- Status bar com Python version, encoding

**Painel Direito - Console:**
- Logs em tempo real
- Categorias: info, success, error
- **Logs Contextuais** separados mostrando atividade dos agentes

**Controles Principais:**
- **Manual/Autônomo** - Alternar modo de controle
- **Executar** - Rodar código
- **Refatorar** - Agente de Código analisa e melhora
- **Gerar** - IA gera código baseado em contexto
- **Deploy** - Iniciar processo de deploy (CAE)

**Feedback de Processos:**
- Loading states para cada ação
- Mensagens de progresso no console
- Notificações de conclusão

---

### 4. **Projects & Ideas**
Gerenciamento completo de projetos e relatórios de viabilidade.

**Dashboard de Estatísticas:**
- Total de projetos
- Capturadas, Em Pesquisa, Em Andamento, Concluídas
- Gráficos visuais de progresso

**Filtros e Busca:**
- Busca por título/descrição
- Filtro por status
- Ordenação

**Cards de Projeto:**
- Status visual com cores
- Barra de progresso animada
- Tags de tecnologia
- Botões de ação:
  - **Relatório** - Ver relatório de viabilidade
  - **Plano** - Ver plano de ação
  - **Iniciar Pesquisa** - Para ideias capturadas
- Datas de criação e última atualização

**Estados de Projeto:**
- **Capturada** (cinza) - Ideia inicial
- **Em Pesquisa** (roxo) - Análise de viabilidade em andamento
- **Em Andamento** (cyan) - Desenvolvimento ativo
- **Concluída** (verde) - Projeto finalizado
- **Pausada** (amarelo) - Temporariamente parada

---

### 5. **Timeline & Logs**
Histórico completo com nodos de log.

**Tipos de Log:**
- **Decisão** (cyan) - Decisões importantes tomadas
- **Erro** (vermelho) - Erros e falhas
- **Marco** (verde) - Marcos importantes
- **Código** (amarelo) - Atividades de código
- **Pesquisa** (roxo) - Pesquisas realizadas
- **Validação** (azul) - Conhecimento validado

**Interface Timeline:**
- Linha do tempo vertical
- Dots coloridos por tipo
- Cards expansíveis
- Filtros por tipo de log
- Busca textual

**Informações por Log:**
- Timestamp e tempo relativo
- Agente responsável
- Projeto relacionado
- Metadados (quando selecionado):
  - Confidence levels
  - Número de fontes
  - Métricas específicas

---

### 6. **Synaptic Memory (Graph View)**
Visualização e gerenciamento da memória de longo prazo.

**Estatísticas Globais:**
- Total de nós
- Total de conexões
- Relevância média
- Nó mais conectado

**Tipos de Nó:**
- **Conceito** (cyan) - Conceitos abstratos
- **Entidade** (roxo) - Entidades concretas
- **Código** (amarelo) - Snippets de código
- **Decisão** (verde) - Decisões importantes
- **Padrão** (azul) - Padrões de design

**Modos de Visualização:**
- **Graph View** - Visualização de grafo interativa
  - Nós posicionados dinamicamente
  - Linhas de conexão com força
  - Badges de contagem de conexões
  - Hover para destaque
  - Click para selecionar
- **List View** - Cards detalhados
  - Grid 2 colunas
  - Informações completas
  - Conexões relacionadas expansíveis
  - Relevância percentual

**Filtros:**
- Por tipo de nó
- Busca textual
- Ordenação por relevância/conexões

**Interações:**
- Adicionar novo nó
- Ver detalhes completos
- Editar informações
- Sugerir novas conexões

---

### 7. **Cognitive Monitor**
Monitoramento em tempo real dos agentes cognitivos.

**Agentes:**
- **IA1 - Extractor** (cyan)
  - Data extraction and processing
  - Queries, Latency
- **IA2 - Reasoner** (roxo)
  - Logical reasoning and inference
  - Queries, Latency
- **IA3 - Validator** (amarelo)
  - Quality assurance and validation
  - Queries, Latency

**Métricas Globais:**
- Queries por minuto
- Memory usage
- Uptime
- Status de cada agente

**Logs em Tempo Real:**
- Atividade de cada agente
- Mensagens com timestamp
- Categorização por tipo

---

### 8. **Settings**
Configurações do sistema.

**Seções:**
- **Sistema**
  - Toggles: Streaming, Auto-save, Notificações
  - Sliders: Temperature, Max Tokens
- **Integrações**
  - Gerenciar APIs externas
- **Aparência**
  - Dark mode toggle
  - Customizações visuais
- **Memória**
  - Uso de memória
  - Limpeza de dados

**Controles:**
- Toggles animados
- Sliders com feedback visual
- Botão de salvar alterações

---

## 🎨 Design System

### Cores Principais
```css
--nexus-bg: #202123        /* Background principal */
--nexus-panel: #2A2B2E     /* Painéis e cards */
--nexus-border: #3E3F45    /* Bordas */
--nexus-text-primary: #ECECEC   /* Texto principal */
--nexus-text-secondary: #8E8E93 /* Texto secundário */
```

### Cores de Destaque
```css
--nexus-blue: #20808D      /* Ações principais */
--nexus-violet: #7B61FF    /* Secundário */
--nexus-gold: #FFD75E      /* Terciário */
--success: #00C896         /* Sucesso */
--error: #FF6B6B           /* Erro */
```

### Tipografia
- **Headings**: -apple-system, BlinkMacSystemFont, "Segoe UI"
- **Body**: System fonts
- **Code**: "SF Mono", "Monaco", monospace
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold)

### Componentes Base
- **Border Radius**: 8px (normal), 12px (xl), 9999px (pill)
- **Shadows**: Sutis com blur de 10-20px
- **Transitions**: 200ms para hover states
- **Animations**: Motion/Framer Motion para todas animações

---

## 🔔 Sistema de Notificações

**Componente NotificationSystem:**
- Posicionado top-right
- Animações de entrada/saída
- Auto-dismiss com timer visual
- Tipos: success, error, info, processing

**Uso:**
```typescript
addNotification("success", "Título", "Mensagem", 5000);
```

**Estados de Processing:**
- Loader animado
- Sem auto-dismiss
- Atualização dinâmica via updateNotification

---

## 📊 Indicadores de Estado

**ProcessingIndicator Component:**
- Tipos: general, cognitive, code, research
- Modo inline ou full
- Animações de pulso para agentes cognitivos
- Dots coloridos animados

**Estados Globais:**
- Loading
- Processing (com agente específico)
- Success
- Error
- Empty state

---

## 🎯 Fluxos de Interação

### Fluxo 1: Pesquisa Profunda
1. Usuário seleciona modo "Pesquisa Profunda"
2. Digite pergunta complexa
3. Sistema mostra "Agentes cognitivos processando..."
4. IA1 extrai informações de fontes
5. IA2 processa e raciocina
6. IA3 valida resultados
7. Exibe: Sources → Answer → Related
8. Botões: Adicionar à Memória, Ver Raciocínio

### Fluxo 2: Desenvolvimento de Código
1. Navegar para Development
2. Selecionar arquivo na sidebar
3. Escrever ou gerar código
4. Clicar "Refatorar"
5. Agente de Código analisa
6. Mostra sugestões no console
7. Aplica melhorias
8. Clicar "Deploy"
9. CAE executa pipeline
10. Notificação de sucesso

### Fluxo 3: Consolidação de Conhecimento
1. No chat, receber resposta útil
2. Clicar em "Sparkles" (Adicionar à Memória)
3. Sistema valida informação (IA3)
4. Cria nó no Graph DB
5. Sugere conexões com conhecimento existente
6. Confirma adição
7. Disponível na Synaptic Memory

---

## 🚀 Próximos Passos (Integração Backend)

### APIs Necessárias
1. `/api/chat` - Chat endpoints
2. `/api/code/generate` - Geração de código
3. `/api/code/refactor` - Refatoração
4. `/api/projects` - CRUD de projetos
5. `/api/timeline` - Logs e nodos
6. `/api/memory` - Graph DB operations
7. `/api/cognitive/status` - Status dos agentes

### WebSocket Endpoints
- `/ws/chat` - Chat em tempo real
- `/ws/cognitive` - Updates de agentes
- `/ws/notifications` - Notificações push

### Autenticação
- JWT tokens
- Session management
- Role-based access

---

## 📱 Responsividade

Embora focado em desktop, o design considera:
- Min-width: 1280px (ideal: 1920px)
- Sidebars colapsáveis
- Grids adaptáveis
- Scroll containers otimizados

---

## ✨ Animações e Transições

**Motion/Framer Motion:**
- Page transitions (fade)
- Card hover effects (translateY)
- List item stagger animations
- Loading spinners
- Progress bars
- Notification slides

**Princípios:**
- Durações: 200-300ms para UI, 1-2s para feedback
- Easing: easeInOut para suavidade
- Não bloquear interação

---

---

## 🧠 Funcionalidades de "Ensino" (NEW!)

### 1. Geração de Sinapses - Salvar na Memória

**Conceito:** Permite ao usuário "ensinar" o Nexus marcando informações como válidas e consolidando-as no Graph DB.

**Localização:** Botão ao lado de cada resposta do assistente

**Estados:**
- Idle: "🧠 Salvar na Memória" (cinza, hover cyan)
- Saving: "Salvando..." com ícone pulsante
- Success: Confirmação animada com partículas (2s auto-dismiss)

**Fluxo:**
1. Usuário recebe resposta útil
2. Clica "Salvar na Memória"
3. Sistema valida com IA3 (1.5s)
4. Cria nó no Graph DB com conexões
5. Mostra confirmação "Sinapse Criada!" 🎉

**API Call:**
```typescript
POST /api/memory/synapse
{
  messageId, content, metadata: { mode, sources, timestamp }
}
```

### 2. Ciclo de Refinamento de Resposta (CRR)

**Conceito:** Permite ao usuário fornecer feedback contextual para regenerar uma resposta melhorada (R2).

**Localização:** Botão "🔄 Refinar Resposta" ao lado de cada resposta

**Dialog:** Modal com:
- Box mostrando resposta original (R1)
- Textarea para feedback do usuário
- Info box explicativa
- Botão "Refinar Resposta"

**Fluxo:**
1. Usuário clica "Refinar Resposta"
2. Dialog abre mostrando R1
3. Usuário escreve feedback (ex: "Adicione exemplos práticos")
4. Sistema processa com IA1, IA2, IA3 (2.5s)
5. Nova mensagem R2 aparece no chat
6. Badge "Resposta Refinada (R2)" visível
7. Box mostra feedback aplicado

**API Call:**
```typescript
POST /api/chat/refine
{
  originalResponse, feedback, context: { conversationId, mode }
}
```

**Recursos:**
- Refinamento iterativo ilimitado (R1 → R2 → R3 → R4...)
- Badge visual "R2" em respostas refinadas
- Exibe feedback aplicado em box
- Ctrl+Enter para submeter

**Componentes Novos:**
- `RefinementDialog.tsx` - Modal de refinamento
- `SynapseConfirmation.tsx` - Confirmação animada

**Ver detalhes completos em:**
- [TEACHING_FEATURES.md](TEACHING_FEATURES.md) - Specs detalhadas
- [API_INTEGRATION_EXAMPLES.md](API_INTEGRATION_EXAMPLES.md) - Exemplos de API
- [QUICK_START.md](QUICK_START.md) - Guia do usuário

---

## 🎓 Conclusão

O Nexus Frontend v2 é uma interface desktop completa e profissional que integra:
- ✅ 9 páginas funcionais
- ✅ 4 modos de operação
- ✅ Sistema de notificações
- ✅ Indicadores de processamento
- ✅ **🧠 Geração de Sinapses (NEW!)**
- ✅ **🔄 Ciclo de Refinamento de Resposta (NEW!)**
- ✅ Integração completa com conceito de memória sináptica
- ✅ Timeline de decisões
- ✅ Editor de código com IA
- ✅ Gerenciamento de projetos
- ✅ Visualização de grafo de conhecimento
- ✅ Monitor de agentes cognitivos

Pronto para integração com backend e testes de usuário! 🚀
