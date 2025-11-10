# Nexus - Funcionalidades de "Ensino"

## 🧠 Visão Geral

O Nexus implementa duas funcionalidades cruciais que transformam o chat em uma ferramenta interativa de **ensino** e **refinamento**:

1. **Geração de Sinapses** - Solidifica conhecimento validado no Graph DB
2. **Ciclo de Refinamento de Resposta (CRR)** - Melhora respostas com feedback do usuário

---

## 📚 1. Geração de Sinapses

### Conceito
Permite ao usuário "ensinar" o Nexus marcando informações como válidas e importantes, consolidando-as na **Memória de Longo Prazo (Graph DB)**.

### Interface

**Localização:** Ao lado de cada resposta do assistente

**Botão:**
```
[🧠 Salvar na Memória]
```

**Estados:**
- **Idle**: Botão cinza com hover cyan
- **Saving**: "Salvando..." com ícone pulsante
- **Success**: Animação de confirmação com partículas

### Fluxo de Uso

1. **Usuário recebe resposta** do Nexus
2. **Usuário clica** "Salvar na Memória"
3. **Sistema processa** (1.5s)
   - Frontend mostra estado de loading
   - Backend chama IA3 (Validator) para validar
   - Cria nó no Graph DB
   - Estabelece conexões relevantes
4. **Confirmação visual** aparece
   - Ícone de cérebro animado
   - "Sinapse Criada!"
   - Partículas de celebração
   - Auto-dismiss após 2s

### Implementação Frontend

```typescript
const handleSaveToMemory = (messageId: number) => {
  setSavingToMemory(messageId);
  
  // API call
  await fetch('/api/memory/synapse', {
    method: 'POST',
    body: JSON.stringify({ 
      messageId, 
      content: message.content,
      context: {
        mode: currentMode,
        timestamp: new Date(),
        sources: message.sources
      }
    })
  });
  
  setSavingToMemory(null);
  setShowSynapseConfirmation(true);
};
```

### API Backend Esperada

**Endpoint:** `POST /api/memory/synapse`

**Request Body:**
```json
{
  "messageId": 123,
  "content": "Resposta do assistente...",
  "context": {
    "mode": "deep-research",
    "timestamp": "2024-01-28T14:32:45",
    "sources": [...]
  }
}
```

**Response:**
```json
{
  "success": true,
  "synapseId": "syn_abc123",
  "nodeId": "node_xyz789",
  "connections": 5,
  "relevance": 0.94
}
```

### Componente: SynapseConfirmation

**Arquivo:** `/components/SynapseConfirmation.tsx`

**Features:**
- Animação de escala e rotação do ícone
- Partículas Sparkles que sobem
- Auto-dismiss após 2s
- Centralizado na tela

---

## 🔄 2. Ciclo de Refinamento de Resposta (CRR)

### Conceito
Permite ao usuário fornecer **feedback contextual** para que o Nexus **regenere uma resposta melhorada (R2)**, aplicando o novo contexto através dos agentes cognitivos.

### Interface

**Localização:** Ao lado de cada resposta do assistente

**Botão:**
```
[🔄 Refinar Resposta]
```

**Dialog:** Modal full-screen overlay

### Fluxo de Uso

1. **Usuário clica** "Refinar Resposta"
2. **Dialog abre** mostrando:
   - Resposta original (R1) em box readonly
   - Textarea para feedback
   - Botão "Refinar Resposta"
3. **Usuário escreve feedback**
   - Ex: "Adicione mais exemplos práticos"
   - Ex: "Foque em aplicações empresariais"
   - Ex: "Simplifique a explicação"
4. **Usuário submete** (Ctrl+Enter ou botão)
5. **Sistema processa** (2.5s)
   - IA1 analisa contexto adicional
   - IA2 aplica nova lógica de raciocínio
   - IA3 valida resposta melhorada
6. **Nova mensagem aparece** (R2)
   - Badge "Resposta Refinada (R2)"
   - Conteúdo melhorado
   - Box mostrando feedback aplicado

### Implementação Frontend

```typescript
const handleRefineResponse = async (feedback: string) => {
  setIsRefining(true);
  
  // API call
  const response = await fetch('/api/chat/refine', {
    method: 'POST',
    body: JSON.stringify({
      originalResponse: selectedMessage.content,
      feedback: feedback,
      context: {
        conversationId: currentConversationId,
        mode: currentMode
      }
    })
  });
  
  const refinedData = await response.json();
  
  // Add refined message
  setMessages(prev => [...prev, {
    id: generateId(),
    role: "assistant",
    content: refinedData.refinedResponse,
    isRefined: true,
    refinementFeedback: feedback,
    originalContent: selectedMessage.content,
    timestamp: new Date()
  }]);
  
  setIsRefining(false);
  setRefinementDialogOpen(false);
};
```

### API Backend Esperada

**Endpoint:** `POST /api/chat/refine`

**Request Body:**
```json
{
  "originalResponse": "Resposta original...",
  "feedback": "Adicione mais exemplos práticos",
  "context": {
    "conversationId": "conv_123",
    "mode": "deep-research"
  }
}
```

**Response:**
```json
{
  "success": true,
  "refinedResponse": "Resposta melhorada...",
  "improvements": [
    "Adicionados 3 exemplos práticos",
    "Focado em casos de uso empresarial",
    "Estrutura simplificada"
  ],
  "confidence": 0.96,
  "agentsUsed": ["IA1", "IA2", "IA3"]
}
```

### Componente: RefinementDialog

**Arquivo:** `/components/RefinementDialog.tsx`

**Props:**
```typescript
interface RefinementDialogProps {
  isOpen: boolean;
  onClose: () => void;
  originalResponse: string;
  onRefine: (feedback: string) => void;
  isRefining: boolean;
}
```

**Features:**
- Modal com backdrop blur
- Box com resposta original (readonly)
- Textarea expansível para feedback
- Suporte para Ctrl+Enter
- Info box explicativa
- Loading state no botão
- Animações de entrada/saída

---

## 🎨 Design System

### Cores Específicas

```css
/* Synapse (Memory) */
--synapse-primary: #20808D;
--synapse-bg: rgba(32, 128, 141, 0.1);
--synapse-border: rgba(32, 128, 141, 0.3);

/* Refinement */
--refinement-primary: #7B61FF;
--refinement-bg: rgba(123, 97, 255, 0.1);
--refinement-border: rgba(123, 97, 255, 0.3);
```

### Badges

**Resposta Refinada:**
```tsx
<div className="inline-flex items-center gap-1.5 px-2 py-1 bg-[#7B61FF]/10 border border-[#7B61FF]/30 rounded">
  <RefreshCw className="w-3 h-3 text-[#7B61FF]" />
  <span className="text-xs text-[#7B61FF]">R2</span>
</div>
```

---

## 📊 Estados e Feedback

### Estados do Botão "Salvar na Memória"

1. **Idle**
   - Texto: "Salvar na Memória"
   - Ícone: Brain (cinza)
   - Hover: cyan

2. **Saving**
   - Texto: "Salvando..."
   - Ícone: Brain pulsante
   - Desabilitado

3. **Success**
   - Confirmation overlay
   - Auto-dismiss

### Estados do Botão "Refinar"

1. **Idle**
   - Texto: "Refinar Resposta"
   - Ícone: RefreshCw (cinza)
   - Hover: roxo

2. **Dialog Open**
   - Modal ativo
   - Backdrop blur

3. **Refining**
   - Botão: "Refinando..."
   - Ícone: RefreshCw spinning
   - Desabilitado

4. **Complete**
   - Nova mensagem R2 aparece
   - Dialog fecha

---

## 🔧 Integração com Backend

### Endpoints Necessários

1. **POST /api/memory/synapse**
   - Cria sinapse no Graph DB
   - Valida conhecimento (IA3)
   - Retorna nodeId e conexões

2. **POST /api/chat/refine**
   - Recebe feedback
   - Processa com IA1, IA2, IA3
   - Retorna resposta melhorada

### Headers Recomendados

```typescript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${userToken}`,
  'X-Conversation-Id': conversationId,
  'X-Mode': currentMode
};
```

### Error Handling

```typescript
try {
  const response = await fetch('/api/memory/synapse', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error('Failed to create synapse');
  }
  
  const result = await response.json();
  // Success handling
  
} catch (error) {
  // Show error notification
  addNotification('error', 'Erro', 'Não foi possível salvar na memória');
  setSavingToMemory(null);
}
```

---

## 📱 Responsividade

### Dialog em Mobile

- Max-width: 95vw
- Max-height: 90vh
- Padding reduzido
- Textarea com min-height menor

### Botões em Mobile

- Stack vertical se necessário
- Touch-friendly (min 44px height)

---

## ♿ Acessibilidade

### Keyboard Navigation

- **Esc**: Fecha dialog
- **Ctrl+Enter**: Submete refinamento
- **Tab**: Navega entre elementos

### ARIA Labels

```tsx
<button
  aria-label="Salvar resposta na memória sináptica"
  aria-busy={savingToMemory === message.id}
>
```

### Screen Reader

```tsx
<div role="status" aria-live="polite">
  {savingToMemory && "Salvando conhecimento na memória..."}
</div>
```

---

## 🎯 Casos de Uso

### Caso 1: Pesquisa Acadêmica

1. Usuário pergunta: "Explique computação quântica"
2. Nexus responde (R1)
3. Usuário: **Salvar na Memória** ✓
4. Sistema cria nó "Computação Quântica" no Graph DB
5. Conecta com nós relacionados (Física, Algoritmos, etc.)

### Caso 2: Refinamento Prático

1. Usuário pergunta: "Como implementar autenticação JWT?"
2. Nexus responde (R1) - explicação teórica
3. Usuário: **Refinar** → "Adicione código prático em Node.js"
4. Nexus gera R2 com exemplos de código
5. Usuário satisfeito: **Salvar na Memória** ✓

### Caso 3: Iteração Múltipla

1. R1 → muito técnica
2. Refinar → "simplifique"
3. R2 → melhor mas falta exemplos
4. Refinar novamente → "adicione exemplos"
5. R3 → perfeita!
6. **Salvar na Memória** ✓

---

## 📈 Métricas Sugeridas

### Analytics

- Taxa de uso "Salvar na Memória"
- Taxa de uso "Refinar"
- Número médio de refinamentos por conversa
- Tempo médio para refinamento
- Taxa de satisfação pós-refinamento

### Logs

```typescript
{
  event: "synapse_created",
  messageId: 123,
  userId: "user_xyz",
  timestamp: "2024-01-28T14:32:45",
  mode: "deep-research"
}

{
  event: "response_refined",
  originalMessageId: 124,
  refinedMessageId: 125,
  feedback: "Adicione exemplos",
  userId: "user_xyz",
  timestamp: "2024-01-28T14:35:12"
}
```

---

## ✅ Checklist de Implementação

### Frontend
- [x] Componente RefinementDialog
- [x] Componente SynapseConfirmation
- [x] Botão "Salvar na Memória" em ChatPage
- [x] Botão "Refinar" em ChatPage
- [x] Botão "Salvar na Memória" em HomePage
- [x] Botão "Refinar" em HomePage
- [x] Estados de loading
- [x] Animações e transições
- [x] Badges R2
- [x] Feedback visual

### Backend (Pendente)
- [ ] Endpoint /api/memory/synapse
- [ ] Endpoint /api/chat/refine
- [ ] Integração com Graph DB
- [ ] Validação com IA3
- [ ] Processamento com IA1, IA2, IA3
- [ ] Logs e analytics

---

## 🚀 Próximos Passos

1. **Implementar endpoints backend**
2. **Testar integração com Graph DB**
3. **Validar fluxo completo**
4. **Adicionar analytics**
5. **Testes de usuário**
6. **Refinamento de UX baseado em feedback**

---

**Última Atualização:** 2024-01-28
**Versão:** 2.0
**Status:** ✅ Frontend Completo | ⏳ Backend Pendente
