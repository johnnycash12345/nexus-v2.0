# Nexus Frontend v2 🚀

Sistema cognitivo de IA autônomo com interface desktop completa e altamente funcional.

## ✨ Funcionalidades Principais

### 🏠 Home (Search & Chat)
- 4 modos de operação: Chat Pessoal, Pesquisa Profunda, Desenvolvimento, Especialista
- Sugestões contextuais dinâmicas
- Interface estilo Perplexity com sources, answer e related
- **🧠 Salvar na Memória** - Solidifica conhecimento no Graph DB
- **🔄 Refinar Resposta** - Melhora respostas com feedback do usuário (R1 → R2)
- Confirmação visual animada ao criar sinapses

### 💬 Personal Chat
- Chat conversacional tradicional
- **🧠 Salvar na Memória** - Cria sinapse no Graph DB com conhecimento validado
- **🔄 Refinar Resposta** - Ciclo de Refinamento (R1 → feedback → R2)
- Fixar mensagens importantes
- Ver cadeia de raciocínio (ReAct) dos agentes
- Feedback com thumbs up/down
- Badge visual para respostas refinadas

### 💻 Development
- Editor de código com navegação de arquivos
- **Gerar** - IA cria código baseado em contexto
- **Refatorar** - Agente de Código analisa e melhora (SOLID, padrões)
- **Executar** - Rodar código com feedback
- **Deploy** - Pipeline automático (CAE)
- Console com logs contextuais dos agentes

### 📁 Projects & Ideas
- Gerenciamento completo de projetos
- 5 status: Capturada, Em Pesquisa, Em Andamento, Concluída, Pausada
- Relatórios de viabilidade e planos de ação
- Barras de progresso animadas
- Filtros e busca avançada

### ⏱️ Timeline & Logs
- Histórico completo de decisões e atividades
- 6 tipos de log: Decisão, Erro, Marco, Código, Pesquisa, Validação
- Timeline visual com dots coloridos
- Metadados expansíveis (confidence, sources, etc.)
- Filtros por tipo e busca textual

### 🧠 Synaptic Memory
- Visualização do Graph DB (conhecimento validado)
- **Graph View** - Grafo interativo com nós e conexões
- **List View** - Cards detalhados com informações completas
- 5 tipos de nó: Conceito, Entidade, Código, Decisão, Padrão
- Relevância e contagem de conexões
- Sugestão de novas conexões

### 📊 Cognitive Monitor
- Status em tempo real dos 3 agentes
- **IA1 - Extractor**: Data extraction and processing
- **IA2 - Reasoner**: Logical reasoning and inference
- **IA3 - Validator**: Quality assurance and validation
- Métricas: queries, latency, memory usage
- Logs em tempo real por agente

### ⚙️ Settings
- Sistema: Streaming, Auto-save, Notificações
- Parâmetros de IA: Temperature, Max Tokens
- Integrações e aparência
- Controle de memória

## 🎨 Design

- **Dark theme** minimalista inspirado no Perplexity
- **Cores**: Cyan (#20808D), Purple (#7B61FF), Gold (#FFD75E)
- **Animações** suaves com Framer Motion
- **Tipografia** clean com system fonts
- **Responsivo** para desktop (min 1280px)

## 🔔 Sistema de Notificações

- Notificações flutuantes no canto superior direito
- 4 tipos: Success, Error, Info, Processing
- Auto-dismiss com timer visual
- Notificações de demo ao iniciar

## ⚡ Quick Actions Menu

- Botão flutuante no canto inferior direito
- Ações rápidas:
  - Nova Conversa
  - Novo Código
  - Nova Ideia
  - Ver Memória
- Animações de abertura/fechamento

## 🗂️ Estrutura de Navegação

**Sidebar (16px):**
1. 🔍 Search & Chat
2. 💬 Personal Chat
3. 💻 Development
4. 📁 Projects & Ideas
5. ⏱️ Timeline & Logs
6. 🧠 Synaptic Memory
7. 📊 Cognitive Monitor
8. ⚙️ Settings

## 🚀 Como Usar

1. **Iniciar Conversa**: Clique em "Search & Chat" ou no botão "+"
2. **Selecionar Modo**: Escolha entre Chat Pessoal, Pesquisa Profunda, Desenvolvimento ou Especialista
3. **Interagir**: Digite sua pergunta/comando
4. **Ensinar o Nexus**:
   - 🧠 **Salvar na Memória**: Clique para consolidar conhecimento no Graph DB
   - 🔄 **Refinar Resposta**: Forneça feedback para melhorar a resposta (R1 → R2)
5. **Ver Projetos**: Acesse "Projects & Ideas" para gerenciar ideias
6. **Monitorar**: Use "Timeline" e "Cognitive Monitor" para acompanhar atividades

## 📚 Recursos Avançados

### Memória Sináptica
- Conhecimento validado e consolidado
- Conexões entre conceitos
- Relevância calculada
- Filtros e busca

### Agentes Cognitivos
- **IA1**: Extração de dados
- **IA2**: Raciocínio lógico
- **IA3**: Validação de qualidade
- Trabalham em sinergia

### Desenvolvimento com IA
- Geração contextual de código
- Refatoração automática
- Deploy pipeline
- Logs detalhados

## 🎯 Fluxos Principais

### 1. Pesquisa Profunda com Refinamento
1. Selecione modo **Pesquisa Profunda**
2. Digite pergunta complexa
3. Agentes processam (IA1, IA2, IA3)
4. Receba resposta (R1) com sources
5. **Opcional**: Clique "Refinar" → forneça feedback → receba R2 melhorada
6. Clique "Salvar na Memória" → Sinapse criada! 🧠

### 2. Desenvolvimento
Development → Selecione arquivo → Gerar/Refatorar → Executar → Deploy

### 3. Ensino Iterativo
1. Faça pergunta
2. Receba R1
3. **Refinar** com feedback: "Adicione exemplos práticos"
4. Receba R2 melhorada
5. **Refinar novamente** se necessário: "Simplifique"
6. Receba R3
7. **Salvar na Memória** quando satisfeito ✓

## 🔗 Integração Backend (Próximos Passos)

O frontend está pronto para integração com:
- API REST para todas as operações
- WebSocket para real-time updates
- Autenticação JWT
- Graph Database (Neo4j/similar)
- Vector Database para embeddings

## 📝 Documentação Completa

Ver `NEXUS_DOCUMENTATION.md` para documentação técnica detalhada.

---

**Status**: ✅ Protótipo de alta fidelidade completo e pronto para testes de usuário!
