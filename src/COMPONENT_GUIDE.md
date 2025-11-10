# Nexus Frontend v2 - Guia de Componentes

## 🎨 Componentes Criados

### Páginas Principais (Pages)

#### 1. **HomePage.tsx**
Interface de busca e chat principal.

**Props:**
```typescript
interface HomePageProps {
  onNavigate: (page: string) => void;
}
```

**Features:**
- 4 modos de operação com cards visuais
- Sugestões contextuais por modo
- Input avançado com anexos/microfone
- Estados: empty, chatting, processing

---

#### 2. **ChatPage.tsx**
Chat conversacional tradicional.

**Features:**
- Mensagens com avatares
- Ações por mensagem (Copy, Pin, Add to Memory, View Reasoning, Feedback)
- Indicador de digitação animado
- Scroll automático

---

#### 3. **CodePage.tsx**
Editor de código com IA.

**Features:**
- File navigator (sidebar esquerda)
- Editor central com syntax highlight
- Console com logs (sidebar direita)
- Botões: Run, Refactor, Generate, Deploy
- Logs contextuais dos agentes

---

#### 4. **ProjectsPage.tsx**
Gerenciamento de projetos.

**Features:**
- Dashboard com estatísticas
- Cards de projeto com progresso
- Filtros e busca
- 5 status diferentes com cores
- Botões: Relatório, Plano, Iniciar Pesquisa

---

#### 5. **TimelinePage.tsx**
Timeline de logs e decisões.

**Features:**
- Timeline visual vertical
- 6 tipos de log com cores
- Cards expansíveis com metadados
- Filtros por tipo
- Busca textual

---

#### 6. **MemoryPage.tsx**
Visualização do Graph DB.

**Features:**
- 2 modos: Graph View e List View
- 5 tipos de nó com cores
- Estatísticas globais
- Filtros e busca
- Interatividade (hover, click, expand)

---

#### 7. **CognitivePage.tsx**
Monitor de agentes.

**Features:**
- Cards dos 3 agentes (IA1, IA2, IA3)
- Métricas: queries, latency
- Logs em tempo real
- Estatísticas globais (queries/min, memory usage)

---

#### 8. **SettingsPage.tsx**
Configurações do sistema.

**Features:**
- Navegação lateral interna
- 4 seções: Sistema, Integrações, Aparência, Memória
- Toggles animados
- Sliders customizados
- Botão de salvar

---

### Componentes de UI

#### 9. **NexusSidebar.tsx**
Navegação principal.

**Props:**
```typescript
interface NexusSidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}
```

**Features:**
- Logo com hover effect
- Botão "New Session"
- 7 itens de navegação com ícones
- Tooltips ao hover
- Animação de tab ativa (layoutId)
- Settings no rodapé

---

#### 10. **NotificationSystem.tsx**
Sistema de notificações.

**Props:**
```typescript
interface NotificationSystemProps {
  notifications: Notification[];
  onDismiss: (id: number) => void;
}

interface Notification {
  id: number;
  type: "success" | "error" | "info" | "processing";
  title: string;
  message: string;
  duration?: number;
}
```

**Hook:**
```typescript
const { 
  notifications, 
  addNotification, 
  dismissNotification,
  updateNotification 
} = useNotifications();
```

**Uso:**
```typescript
addNotification("success", "Título", "Mensagem", 5000);
```

---

#### 11. **QuickActionsMenu.tsx**
Menu de ações rápidas flutuante.

**Props:**
```typescript
interface QuickActionsMenuProps {
  onNavigate: (page: string) => void;
}
```

**Features:**
- Botão flutuante com pulse effect
- Menu expansível com 4 ações
- Animações de abertura/fechamento
- Hover effects nos items

---

#### 12. **ProcessingIndicator.tsx**
Indicador de processamento.

**Props:**
```typescript
interface ProcessingIndicatorProps {
  message?: string;
  type?: "general" | "cognitive" | "code" | "research";
  inline?: boolean;
}
```

**Tipos:**
- **general**: Loader spinner
- **cognitive**: Brain icon + badges dos agentes
- **code**: Code icon
- **research**: Search icon

**Modos:**
- **inline**: Compacto, horizontal
- **full**: Centralizado, vertical com agentes

---

#### 13. **EmptyState.tsx**
Estado vazio reutilizável.

**Props:**
```typescript
interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

**Uso:**
```typescript
<EmptyState
  icon={FolderKanban}
  title="Nenhum projeto encontrado"
  description="Crie seu primeiro projeto"
  action={{
    label: "Criar Projeto",
    onClick: handleCreate
  }}
/>
```

---

## 🎨 Sistema de Design

### Cores

```typescript
// Background
const bgPrimary = "#202123";
const bgSecondary = "#2A2B2E";
const bgTertiary = "#3E3F45";

// Text
const textPrimary = "#ECECEC";
const textSecondary = "#8E8E93";

// Accent Colors
const nexusBlue = "#20808D";
const nexusViolet = "#7B61FF";
const nexusGold = "#FFD75E";
const successGreen = "#00C896";
const errorRed = "#FF6B6B";
const infoBlue = "#00C6FF";
```

### Tipografia

```typescript
// Font Weights
fontWeight: 400 // Regular - body text
fontWeight: 500 // Medium - headings, labels
fontWeight: 600 // Semibold - emphasis

// Font Sizes (via Tailwind)
text-xs: 12px
text-sm: 14px
text-base: 16px
text-lg: 18px
text-xl: 20px
text-2xl: 24px
```

### Espaçamento

```typescript
// Gap
gap-1: 4px
gap-2: 8px
gap-3: 12px
gap-4: 16px
gap-6: 24px

// Padding
p-2: 8px
p-4: 16px
p-6: 24px
p-8: 32px
```

### Border Radius

```typescript
rounded-md: 6px
rounded-lg: 8px
rounded-xl: 12px
rounded-2xl: 16px
rounded-full: 9999px
```

### Sombras

```typescript
// Subtle
shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05)

// Regular
shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1)

// Emphasis
shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.25)

// Colored (com cor específica)
shadow-[#20808D]/20: com opacity 20%
```

---

## 🎭 Padrões de Animação

### Transições de Página

```typescript
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  transition={{ duration: 0.2 }}
>
```

### Cards Hover

```typescript
<motion.div
  whileHover={{ y: -4 }}
  whileTap={{ scale: 0.98 }}
>
```

### List Items Stagger

```typescript
{items.map((item, idx) => (
  <motion.div
    key={item.id}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: idx * 0.05 }}
  >
))}
```

### Loading Dots

```typescript
<motion.div
  animate={{ opacity: [0.3, 1, 0.3] }}
  transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
  className="w-2 h-2 bg-[#20808D] rounded-full"
/>
```

### Progress Bar

```typescript
<motion.div
  initial={{ width: 0 }}
  animate={{ width: `${progress}%` }}
  transition={{ duration: 1, ease: "easeOut" }}
  className="h-full rounded-full bg-[#20808D]"
/>
```

---

## 🔧 Hooks Customizados

### useNotifications

```typescript
const {
  notifications,
  addNotification,
  dismissNotification,
  updateNotification
} = useNotifications();

// Adicionar notificação
const id = addNotification("success", "Título", "Mensagem", 5000);

// Atualizar notificação (útil para processing → success)
updateNotification(id, { 
  type: "success", 
  title: "Concluído!" 
});

// Remover notificação
dismissNotification(id);
```

---

## 📱 Responsividade

### Breakpoints

```typescript
// Desktop (foco principal)
min-width: 1280px (ideal)
min-width: 1920px (ótimo)

// Tablet (secundário)
min-width: 768px

// Mobile (terciário)
min-width: 640px
```

### Grid Adaptável

```typescript
// Desktop
grid-cols-2 // 2 colunas
grid-cols-3 // 3 colunas

// Tablet
md:grid-cols-2

// Mobile
grid-cols-1
```

---

## 🎯 Melhores Práticas

### 1. Sempre usar motion/react para animações
```typescript
import { motion, AnimatePresence } from "motion/react";
```

### 2. Usar fontWeight via style, não Tailwind
```typescript
// ✅ Correto
<span style={{ fontWeight: 400 }}>Text</span>

// ❌ Evitar
<span className="font-normal">Text</span>
```

### 3. Cores via CSS variables quando possível
```typescript
// ✅ Correto
style={{ backgroundColor: nodeTypeConfig[node.type].color + '20' }}

// ✅ Também correto
className="bg-[#20808D]"
```

### 4. Sempre fornecer key em listas
```typescript
{items.map((item) => (
  <div key={item.id}>
))}
```

### 5. Usar AnimatePresence para elementos condicionais
```typescript
<AnimatePresence>
  {isVisible && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
  )}
</AnimatePresence>
```

---

## 🚀 Performance

### Otimizações Implementadas

1. **Lazy Loading**: Componentes carregam sob demanda
2. **Memoization**: useCallback/useMemo onde necessário
3. **Virtual Scrolling**: Para listas longas (timeline, logs)
4. **Debounce**: Em inputs de busca
5. **Throttle**: Em scroll handlers

---

## 📚 Referências

- **Framer Motion**: https://www.framer.com/motion/
- **Lucide Icons**: https://lucide.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **React**: https://react.dev/

---

**Última Atualização**: 2024-01-28
