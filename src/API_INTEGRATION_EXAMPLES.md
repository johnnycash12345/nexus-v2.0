# Nexus - Exemplos de Integração API

## 🔌 Endpoints Implementados no Frontend

### 1. Criar Sinapse (Salvar na Memória)

**Endpoint:** `POST /api/memory/synapse`

#### Request

```typescript
// Frontend implementation
const createSynapse = async (messageId: number, content: string) => {
  try {
    const response = await fetch('/api/memory/synapse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
      },
      body: JSON.stringify({
        messageId: messageId,
        content: content,
        metadata: {
          conversationId: getCurrentConversationId(),
          mode: getCurrentMode(),
          timestamp: new Date().toISOString(),
          sources: getMessageSources(messageId),
          userValidated: true
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error('Error creating synapse:', error);
    throw error;
  }
};
```

#### Request Body

```json
{
  "messageId": 12345,
  "content": "Machine Learning é um subcampo da IA que permite sistemas aprenderem com dados sem programação explícita. Exemplos: Netflix recomenda filmes, Gmail filtra spam, carros autônomos.",
  "metadata": {
    "conversationId": "conv_abc123",
    "mode": "deep-research",
    "timestamp": "2024-01-28T14:32:45.123Z",
    "sources": [
      {
        "title": "Wikipedia - Machine Learning",
        "url": "https://wikipedia.org/wiki/Machine_learning",
        "relevance": 0.95
      },
      {
        "title": "Stanford AI Course",
        "url": "https://cs229.stanford.edu",
        "relevance": 0.92
      }
    ],
    "userValidated": true
  }
}
```

#### Expected Response

```json
{
  "success": true,
  "synapseId": "syn_xyz789",
  "nodeId": "node_ml_001",
  "nodeType": "concept",
  "label": "Machine Learning",
  "relevance": 0.94,
  "connections": {
    "created": 5,
    "existing": 3,
    "total": 8
  },
  "connectedNodes": [
    {
      "nodeId": "node_ai_001",
      "label": "Artificial Intelligence",
      "connectionStrength": 0.95,
      "relationType": "parent"
    },
    {
      "nodeId": "node_dl_001",
      "label": "Deep Learning",
      "connectionStrength": 0.88,
      "relationType": "child"
    },
    {
      "nodeId": "node_stats_001",
      "label": "Statistics",
      "connectionStrength": 0.82,
      "relationType": "related"
    }
  ],
  "validatedBy": "IA3",
  "validationConfidence": 0.96,
  "timestamp": "2024-01-28T14:32:47.456Z"
}
```

#### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Content validation failed - confidence too low",
    "details": {
      "validationConfidence": 0.45,
      "minimumRequired": 0.70
    }
  }
}
```

---

### 2. Refinar Resposta (Ciclo de Refinamento)

**Endpoint:** `POST /api/chat/refine`

#### Request

```typescript
// Frontend implementation
const refineResponse = async (
  originalResponse: string,
  feedback: string,
  context: any
) => {
  try {
    const response = await fetch('/api/chat/refine', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
        'X-Conversation-Id': context.conversationId,
        'X-Mode': context.mode
      },
      body: JSON.stringify({
        originalResponse: originalResponse,
        feedback: feedback,
        context: {
          conversationId: context.conversationId,
          mode: context.mode,
          previousMessages: getRecentMessages(5),
          userPreferences: getUserPreferences()
        },
        refinementOptions: {
          preserveStructure: false,
          addExamples: true,
          targetAudience: "technical",
          maxLength: 2000
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error('Error refining response:', error);
    throw error;
  }
};
```

#### Request Body

```json
{
  "originalResponse": "Machine Learning é uma técnica de IA que usa algoritmos estatísticos para aprender padrões em dados.",
  "feedback": "Adicione 3 exemplos práticos do dia-a-dia e explique de forma mais simples",
  "context": {
    "conversationId": "conv_abc123",
    "mode": "personal",
    "previousMessages": [
      {
        "role": "user",
        "content": "O que é Machine Learning?"
      },
      {
        "role": "assistant",
        "content": "Machine Learning é..."
      }
    ],
    "userPreferences": {
      "language": "pt-BR",
      "technicalLevel": "beginner",
      "preferExamples": true
    }
  },
  "refinementOptions": {
    "preserveStructure": false,
    "addExamples": true,
    "targetAudience": "beginner",
    "maxLength": 2000
  }
}
```

#### Expected Response

```json
{
  "success": true,
  "refinedResponse": "Machine Learning (Aprendizado de Máquina) é como ensinar um computador a aprender com exemplos, igual uma criança aprende.\n\n**3 Exemplos do Dia-a-Dia:**\n\n1. **Netflix recomenda filmes**: O sistema aprende quais filmes você gosta baseado no que você já assistiu. Quanto mais você usa, melhores as recomendações!\n\n2. **Gmail filtra spam**: O email aprende a reconhecer spam vendo milhões de exemplos de emails bons e ruins. Por isso ele fica cada vez melhor.\n\n3. **Waze prevê trânsito**: O app aprende os padrões de trânsito vendo dados de milhões de motoristas, e consegue prever congestionamentos.\n\nEm resumo: é dar exemplos ao computador e deixar ele descobrir os padrões sozinho!",
  "improvements": [
    "Linguagem simplificada de técnica para acessível",
    "Adicionados 3 exemplos práticos populares (Netflix, Gmail, Waze)",
    "Estrutura reorganizada com marcadores e formatação",
    "Analogia com aprendizado infantil para facilitar compreensão",
    "Resumo final em uma frase"
  ],
  "agentsUsed": {
    "IA1": {
      "role": "Extractor",
      "action": "Analisou feedback do usuário e extraiu requisitos (exemplos práticos, simplificação)",
      "confidence": 0.97
    },
    "IA2": {
      "role": "Reasoner",
      "action": "Selecionou exemplos relevantes e criou analogia com aprendizado infantil",
      "confidence": 0.94
    },
    "IA3": {
      "role": "Validator",
      "action": "Validou precisão técnica e adequação ao nível iniciante",
      "confidence": 0.96
    }
  },
  "metrics": {
    "originalLength": 98,
    "refinedLength": 467,
    "readabilityScore": 85,
    "technicalAccuracy": 0.94,
    "examplesAdded": 3,
    "processingTime": 2347
  },
  "refinementLevel": 2,
  "timestamp": "2024-01-28T14:35:12.789Z"
}
```

#### Error Response

```json
{
  "success": false,
  "error": {
    "code": "REFINEMENT_FAILED",
    "message": "Unable to refine response with given feedback",
    "details": {
      "reason": "Feedback too vague",
      "suggestion": "Please provide more specific guidance, e.g., 'Add code examples' or 'Explain the concept of gradient descent'"
    }
  }
}
```

---

## 🔐 Autenticação

### Headers Necessários

```typescript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${userToken}`,
  'X-User-Id': userId,
  'X-Conversation-Id': conversationId,
  'X-Mode': currentMode,
  'X-Request-Id': generateRequestId(),
  'X-Client-Version': '2.0.0'
};
```

---

## 📊 Rate Limiting

### Limites Esperados

```json
{
  "synapse": {
    "requests_per_minute": 10,
    "requests_per_hour": 100,
    "requests_per_day": 500
  },
  "refinement": {
    "requests_per_minute": 5,
    "requests_per_hour": 50,
    "requests_per_day": 200
  }
}
```

### Rate Limit Headers (Response)

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1706450545
```

---

## 🔄 Retry Logic

### Implementação Recomendada

```typescript
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries = 3
): Promise<Response> {
  let lastError: Error;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      
      // Success
      if (response.ok) {
        return response;
      }
      
      // Rate limited - wait and retry
      if (response.status === 429) {
        const retryAfter = parseInt(
          response.headers.get('Retry-After') || '5'
        );
        await sleep(retryAfter * 1000);
        continue;
      }
      
      // Server error - retry
      if (response.status >= 500) {
        await sleep(Math.pow(2, i) * 1000); // Exponential backoff
        continue;
      }
      
      // Client error - don't retry
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      
    } catch (error) {
      lastError = error as Error;
      if (i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000);
      }
    }
  }
  
  throw lastError!;
}
```

---

## 📝 Logging

### Request Logging

```typescript
const logRequest = (endpoint: string, payload: any) => {
  console.log({
    timestamp: new Date().toISOString(),
    endpoint: endpoint,
    method: 'POST',
    userId: getCurrentUserId(),
    conversationId: getCurrentConversationId(),
    payloadSize: JSON.stringify(payload).length,
    requestId: generateRequestId()
  });
};
```

### Response Logging

```typescript
const logResponse = (endpoint: string, response: any, duration: number) => {
  console.log({
    timestamp: new Date().toISOString(),
    endpoint: endpoint,
    success: response.success,
    duration: duration,
    responseSize: JSON.stringify(response).length,
    agentsUsed: response.agentsUsed,
    confidence: response.validationConfidence || response.metrics?.technicalAccuracy
  });
};
```

---

## 🧪 Testing Examples

### Test: Create Synapse

```typescript
describe('Synapse Creation', () => {
  it('should create synapse successfully', async () => {
    const mockMessage = {
      id: 123,
      content: "Test knowledge",
      sources: [{ title: "Source 1", url: "http://test.com" }]
    };
    
    const result = await createSynapse(
      mockMessage.id,
      mockMessage.content
    );
    
    expect(result.success).toBe(true);
    expect(result.synapseId).toBeDefined();
    expect(result.nodeId).toBeDefined();
    expect(result.connections.total).toBeGreaterThan(0);
  });
  
  it('should handle validation failure', async () => {
    const lowQualityContent = "xyz";
    
    await expect(
      createSynapse(999, lowQualityContent)
    ).rejects.toThrow('VALIDATION_FAILED');
  });
});
```

### Test: Refine Response

```typescript
describe('Response Refinement', () => {
  it('should refine response with feedback', async () => {
    const original = "Technical explanation";
    const feedback = "Add practical examples";
    const context = {
      conversationId: "test_123",
      mode: "personal"
    };
    
    const result = await refineResponse(original, feedback, context);
    
    expect(result.success).toBe(true);
    expect(result.refinedResponse).toBeDefined();
    expect(result.improvements.length).toBeGreaterThan(0);
    expect(result.agentsUsed.IA1).toBeDefined();
    expect(result.metrics.examplesAdded).toBeGreaterThan(0);
  });
});
```

---

## 🎯 Integration Checklist

### Frontend
- [x] Implement createSynapse function
- [x] Implement refineResponse function
- [x] Handle loading states
- [x] Handle error states
- [x] Show success confirmations
- [x] Implement retry logic
- [x] Add request/response logging

### Backend (Required)
- [ ] Create `/api/memory/synapse` endpoint
- [ ] Create `/api/chat/refine` endpoint
- [ ] Implement IA3 validation
- [ ] Implement IA1, IA2, IA3 refinement
- [ ] Setup Graph DB integration
- [ ] Add rate limiting
- [ ] Setup monitoring/logging
- [ ] Add authentication middleware

---

## 🚀 Quick Start Integration

```typescript
// 1. Install dependencies (if needed)
npm install @types/node

// 2. Create API client
import { createSynapse, refineResponse } from './api/nexus';

// 3. Use in components
const handleSaveToMemory = async (messageId: number, content: string) => {
  try {
    setSaving(true);
    const result = await createSynapse(messageId, content);
    showSuccessNotification('Sinapse criada!');
    return result;
  } catch (error) {
    showErrorNotification('Erro ao criar sinapse');
  } finally {
    setSaving(false);
  }
};

const handleRefine = async (original: string, feedback: string) => {
  try {
    setRefining(true);
    const result = await refineResponse(original, feedback, context);
    addMessageToChat(result.refinedResponse);
    return result;
  } catch (error) {
    showErrorNotification('Erro ao refinar resposta');
  } finally {
    setRefining(false);
  }
};
```

---

**Última Atualização:** 2024-01-28
**Status:** ✅ Frontend Ready | ⏳ Backend Integration Pending
