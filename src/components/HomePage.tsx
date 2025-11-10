import { useState } from "react";
import { Send, Mic, Sparkles, Image as ImageIcon, Paperclip, MessageSquare, Search, Code, Brain, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { RefinementDialog } from "./RefinementDialog";
import { SynapseConfirmation } from "./SynapseConfirmation";

interface HomePageProps {
  onNavigate: (page: string) => void;
}

type OperationMode = "personal" | "deep-research" | "development" | "expert";

export function HomePage({ onNavigate }: HomePageProps) {
  const [input, setInput] = useState("");
  const [selectedMode, setSelectedMode] = useState<OperationMode>("personal");
  const [messages, setMessages] = useState<any[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  
  // Refinement states
  const [refinementDialogOpen, setRefinementDialogOpen] = useState(false);
  const [selectedMessageForRefinement, setSelectedMessageForRefinement] = useState<any>(null);
  const [isRefining, setIsRefining] = useState(false);
  
  // Synapse states
  const [showSynapseConfirmation, setShowSynapseConfirmation] = useState(false);
  const [savingToMemory, setSavingToMemory] = useState<number | null>(null);

  const operationModes = [
    { 
      id: "personal" as OperationMode, 
      label: "Chat Pessoal", 
      icon: MessageSquare,
      description: "Conversas rápidas e respostas diretas",
      color: "#20808D"
    },
    { 
      id: "deep-research" as OperationMode, 
      label: "Pesquisa Profunda", 
      icon: Search,
      description: "Análise detalhada e relatórios completos",
      color: "#7B61FF"
    },
    { 
      id: "development" as OperationMode, 
      label: "Desenvolvimento", 
      icon: Code,
      description: "Geração e refatoração de código",
      color: "#FFD75E"
    },
    { 
      id: "expert" as OperationMode, 
      label: "Especialista", 
      icon: Brain,
      description: "Domínios específicos usando memória sináptica",
      color: "#00C6FF"
    },
  ];

  const getSuggestionsForMode = (mode: OperationMode) => {
    const suggestions = {
      personal: [
        { text: "Como funciona o sistema cognitivo do Nexus?", icon: "🧠" },
        { text: "Explique o conceito de memória sináptica", icon: "💡" },
        { text: "Quais são as capacidades dos agentes IA?", icon: "🤖" },
        { text: "Como iniciar um novo projeto?", icon: "🚀" },
      ],
      "deep-research": [
        { text: "Análise de viabilidade: sistema de recomendação ML", icon: "📊" },
        { text: "Pesquisar tendências em computação quântica", icon: "⚛️" },
        { text: "Comparar arquiteturas de microserviços", icon: "🏗️" },
        { text: "Gerar relatório sobre blockchain empresarial", icon: "📑" },
      ],
      development: [
        { text: "Criar API REST com autenticação JWT", icon: "💻" },
        { text: "Refatorar código para padrões SOLID", icon: "🔧" },
        { text: "Implementar sistema de cache Redis", icon: "⚡" },
        { text: "Otimizar queries de banco de dados", icon: "🎯" },
      ],
      expert: [
        { text: "Consultar conhecimento sobre arquitetura de sistemas", icon: "🏛️" },
        { text: "Aplicar padrões de design aprendidos", icon: "📐" },
        { text: "Usar memória sobre melhores práticas de segurança", icon: "🔐" },
        { text: "Revisar decisões anteriores do projeto X", icon: "📋" },
      ],
    };
    return suggestions[mode];
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userQuery = input.trim();
    const currentMode = selectedMode;
    const modeDetails = operationModes.find((mode) => mode.id === currentMode);
    const modeLabel = modeDetails?.label ?? currentMode;

    setMessages((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        type: "query",
        text: userQuery,
        mode: currentMode,
      },
    ]);

    setInput("");
    setIsThinking(true);

    try {
      const response = await fetch("/api/chat/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: userQuery,
          mode: modeLabel,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      const normalizedSources =
        Array.isArray(data?.sources) && data.sources.length > 0
          ? data.sources
          : null;

      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          type: "answer",
          query: userQuery,
          mode: currentMode,
          answer:
            data?.answer ??
            data?.content ??
            "Recebi sua mensagem, mas nao veio conteudo na resposta.",
          sources: normalizedSources,
          classification: data?.type ?? null,
          itemId: data?.item_id ?? null,
        },
      ]);
    } catch (error) {
      console.error("Erro ao enviar mensagem para o backend:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          type: "answer",
          query: userQuery,
          mode: currentMode,
          answer:
            "Desculpe, nao consegui contatar o backend agora. Tente novamente em instantes.",
          isError: true,
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  };
  // Handle synapse creation (save to memory)
  const handleSaveToMemory = (messageId: number) => {
    setSavingToMemory(messageId);
    
    setTimeout(() => {
      setSavingToMemory(null);
      setShowSynapseConfirmation(true);
    }, 1500);
  };

  // Handle refinement request
  const handleOpenRefinement = (message: any) => {
    setSelectedMessageForRefinement(message);
    setRefinementDialogOpen(true);
  };

  // Handle refinement submission
  const handleRefineResponse = (feedback: string) => {
    if (!selectedMessageForRefinement) return;
    
    setIsRefining(true);
    
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        type: "answer",
        query: selectedMessageForRefinement.query,
        mode: selectedMessageForRefinement.mode,
        sources: selectedMessageForRefinement.sources,
        answer: `[Resposta Refinada - R2]\n\nBaseado no seu feedback: "${feedback}"\n\n${selectedMessageForRefinement.answer}\n\n[Melhorias aplicadas pelos agentes cognitivos]\n• IA1 (Extractor) analisou o contexto adicional fornecido\n• IA2 (Reasoner) aplicou nova lógica de raciocínio considerando o feedback\n• IA3 (Validator) validou a resposta melhorada com 98% de confiança\n\nEsta resposta incorpora seu feedback e oferece uma explicação mais alinhada às suas necessidades específicas.`,
        related: selectedMessageForRefinement.related,
        canPin: true,
        isRefined: true,
        refinementFeedback: feedback,
        originalAnswer: selectedMessageForRefinement.answer,
      }]);
      
      setIsRefining(false);
      setRefinementDialogOpen(false);
      setSelectedMessageForRefinement(null);
    }, 2500);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Refinement Dialog */}
      <RefinementDialog
        isOpen={refinementDialogOpen}
        onClose={() => {
          setRefinementDialogOpen(false);
          setSelectedMessageForRefinement(null);
        }}
        originalResponse={selectedMessageForRefinement?.answer || ""}
        onRefine={handleRefineResponse}
        isRefining={isRefining}
      />

      {/* Synapse Confirmation */}
      <SynapseConfirmation
        show={showSynapseConfirmation}
        onComplete={() => setShowSynapseConfirmation(false)}
      />

      {messages.length === 0 ? (
        // Empty state
        <div className="flex-1 flex items-center justify-center px-6">
          <div className="max-w-4xl w-full">
            <div className="text-center mb-12">
              <motion.h1 
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-6xl mb-4 tracking-tight bg-gradient-to-r from-[#20808D] to-[#7B61FF] bg-clip-text text-transparent"
                style={{ fontWeight: 500 }}
              >
                nexus
              </motion.h1>
              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="text-[#8E8E93] text-base"
                style={{ fontWeight: 400 }}
              >
                Sistema cognitivo de IA autônomo
              </motion.p>
            </div>

            {/* Input */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-8"
            >
              <div className="relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSend()}
                  placeholder="Pergunte qualquer coisa ao Nexus..."
                  className="w-full px-6 py-5 bg-[#2A2B2E] border border-[#3E3F45] rounded-2xl text-[#ECECEC] placeholder-[#8E8E93] focus:outline-none focus:ring-2 focus:ring-[#20808D] focus:border-transparent transition-all text-base shadow-lg"
                  style={{ fontWeight: 400 }}
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                  <button className="w-10 h-10 flex items-center justify-center hover:bg-white/5 rounded-lg transition-colors">
                    <Paperclip className="w-4 h-4 text-[#8E8E93]" />
                  </button>
                  <button className="w-10 h-10 flex items-center justify-center hover:bg-white/5 rounded-lg transition-colors">
                    <ImageIcon className="w-4 h-4 text-[#8E8E93]" />
                  </button>
                  <button className="w-10 h-10 flex items-center justify-center hover:bg-white/5 rounded-lg transition-colors">
                    <Mic className="w-4 h-4 text-[#8E8E93]" />
                  </button>
                  <button
                    onClick={handleSend}
                    disabled={!input.trim()}
                    className="w-10 h-10 bg-gradient-to-r from-[#20808D] to-[#268a98] rounded-lg flex items-center justify-center hover:shadow-lg hover:shadow-[#20808D]/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <Send className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Operation Modes */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="text-xs text-[#8E8E93] mb-3 px-1" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                MODOS DE OPERAÇÃO
              </div>
              <div className="grid grid-cols-4 gap-3 mb-12">
                {operationModes.map((mode) => {
                  const Icon = mode.icon;
                  const isSelected = selectedMode === mode.id;
                  
                  return (
                    <motion.button
                      key={mode.id}
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setSelectedMode(mode.id)}
                      className={`p-4 rounded-xl border transition-all ${
                        isSelected
                          ? "bg-[#2A2B2E] border-[#20808D] shadow-lg shadow-[#20808D]/10"
                          : "bg-[#2A2B2E] border-[#3E3F45] hover:border-[#4E4F55]"
                      }`}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <div 
                          className="w-8 h-8 rounded-lg flex items-center justify-center"
                          style={{ backgroundColor: mode.color + '20' }}
                        >
                          <Icon className="w-4 h-4" style={{ color: mode.color }} strokeWidth={1.5} />
                        </div>
                        <span className="text-sm text-[#ECECEC]" style={{ fontWeight: 500 }}>
                          {mode.label}
                        </span>
                      </div>
                      <p className="text-xs text-[#8E8E93] text-left" style={{ fontWeight: 400 }}>
                        {mode.description}
                      </p>
                    </motion.button>
                  );
                })}
              </div>
            </motion.div>

            {/* Contextual Suggestions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="text-xs text-[#8E8E93] mb-3 px-1" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                SUGESTÕES PARA {operationModes.find(m => m.id === selectedMode)?.label.toUpperCase()}
              </div>
              <div className="grid grid-cols-2 gap-3">
                {getSuggestionsForMode(selectedMode).map((suggestion, idx) => (
                  <motion.button
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + idx * 0.05 }}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => setInput(suggestion.text)}
                    className="p-4 bg-[#2A2B2E] border border-[#3E3F45] hover:border-[#4E4F55] rounded-xl text-left transition-all flex items-start gap-3 group"
                  >
                    <span className="text-xl">{suggestion.icon}</span>
                    <span className="flex-1 text-sm text-[#ECECEC] group-hover:text-[#20808D] transition-colors" style={{ fontWeight: 400 }}>
                      {suggestion.text}
                    </span>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      ) : (
        // Messages view
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-6 py-8">
            {/* Mode indicator */}
            <div className="mb-6 flex items-center gap-2 px-4 py-2 bg-[#2A2B2E] border border-[#3E3F45] rounded-lg w-fit">
              {(() => {
                const mode = operationModes.find(m => m.id === selectedMode);
                const Icon = mode?.icon;
                return (
                  <>
                    {Icon && <Icon className="w-4 h-4" style={{ color: mode.color }} strokeWidth={1.5} />}
                    <span className="text-sm text-[#ECECEC]" style={{ fontWeight: 400 }}>
                      Modo: {mode?.label}
                    </span>
                  </>
                );
              })()}
            </div>

            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-12"
                >
                  {message.type === "answer" && (
                    <div>
                      <h2 className="mb-8 text-[#ECECEC] text-2xl" style={{ fontWeight: 400 }}>
                        {message.query}
                      </h2>

                      {/* Sources */}
                      {message.sources && (
                        <div className="mb-8">
                          <div className="text-[#8E8E93] text-xs mb-3" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>SOURCES</div>
                          <div className="flex gap-2">
                            {message.sources.map((source: any, idx: number) => (
                              <div
                                key={idx}
                                className="px-4 py-2 bg-[#2A2B2E] border border-[#3E3F45] rounded-lg flex items-center gap-2 text-sm hover:border-[#4E4F55] transition-colors cursor-pointer"
                              >
                                <div className="w-6 h-6 bg-[#20808D]/20 rounded flex items-center justify-center text-[#20808D] text-xs" style={{ fontWeight: 600 }}>
                                  {source.favicon}
                                </div>
                                <span className="text-[#ECECEC]" style={{ fontWeight: 400 }}>{source.title}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Answer */}
                      <div className="mb-6">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="text-[#8E8E93] text-xs" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                            ANSWER
                          </div>
                          {message.isRefined && (
                            <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-[#7B61FF]/10 border border-[#7B61FF]/30 rounded">
                              <RefreshCw className="w-3 h-3 text-[#7B61FF]" />
                              <span className="text-xs text-[#7B61FF]" style={{ fontWeight: 500 }}>R2</span>
                            </div>
                          )}
                        </div>
                        <p className="text-[#ECECEC] leading-relaxed whitespace-pre-line" style={{ fontWeight: 400 }}>
                          {message.answer}
                        </p>
                        
                        {/* Refinement Info */}
                        {message.isRefined && message.refinementFeedback && (
                          <div className="mt-4 p-3 bg-[#202123] border border-[#3E3F45] rounded-lg">
                            <div className="text-xs text-[#8E8E93] mb-1" style={{ fontWeight: 500 }}>
                              Feedback aplicado:
                            </div>
                            <p className="text-xs text-[#ECECEC]" style={{ fontWeight: 400 }}>
                              "{message.refinementFeedback}"
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 mb-8 pb-8 border-b border-[#3E3F45] flex-wrap">
                        <button 
                          onClick={() => handleSaveToMemory(message.id)}
                          disabled={savingToMemory === message.id}
                          className="px-4 py-2 bg-[#2A2B2E] hover:bg-[#20808D]/10 border border-[#3E3F45] hover:border-[#20808D]/30 rounded-lg text-sm text-[#ECECEC] hover:text-[#20808D] transition-all flex items-center gap-2 disabled:opacity-50"
                        >
                          <Brain className={`w-4 h-4 ${savingToMemory === message.id ? 'animate-pulse' : ''}`} />
                          {savingToMemory === message.id ? 'Salvando...' : 'Salvar na Memória'}
                        </button>
                        
                        <button 
                          onClick={() => handleOpenRefinement(message)}
                          className="px-4 py-2 bg-[#2A2B2E] hover:bg-[#7B61FF]/10 border border-[#3E3F45] hover:border-[#7B61FF]/30 rounded-lg text-sm text-[#ECECEC] hover:text-[#7B61FF] transition-all flex items-center gap-2"
                        >
                          <RefreshCw className="w-4 h-4" />
                          Refinar Resposta
                        </button>
                        
                        <button className="px-4 py-2 bg-[#2A2B2E] hover:bg-[#3A3B3E] border border-[#3E3F45] rounded-lg text-sm text-[#ECECEC] transition-all">
                          Ver Raciocínio
                        </button>
                        <button className="px-4 py-2 bg-[#2A2B2E] hover:bg-[#3A3B3E] border border-[#3E3F45] rounded-lg text-sm text-[#ECECEC] transition-all">
                          📌 Fixar
                        </button>
                      </div>

                      {/* Related */}
                      {message.related && (
                        <div>
                          <div className="text-[#8E8E93] text-xs mb-3" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>RELATED</div>
                          <div className="space-y-2">
                            {message.related.map((item: string, idx: number) => (
                              <button
                                key={idx}
                                className="w-full px-4 py-3 bg-[#2A2B2E] hover:bg-[#3A3B3E] border border-[#3E3F45] hover:border-[#4E4F55] rounded-lg text-left text-[#ECECEC] transition-all text-sm"
                                style={{ fontWeight: 400 }}
                              >
                                {item}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {isThinking && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-3 text-[#8E8E93] text-sm"
              >
                <div className="flex gap-1.5">
                  <motion.div
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                    className="w-2 h-2 bg-[#20808D] rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                    className="w-2 h-2 bg-[#7B61FF] rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                    className="w-2 h-2 bg-[#FFD75E] rounded-full"
                  />
                </div>
                <span>Agentes cognitivos processando...</span>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* Bottom Input (when chatting) */}
      {messages.length > 0 && (
        <div className="border-t border-[#3E3F45] bg-[#202123]">
          <div className="max-w-4xl mx-auto px-6 py-4">
            <div className="relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Fazer pergunta de acompanhamento..."
                className="w-full px-6 py-4 bg-[#2A2B2E] border border-[#3E3F45] rounded-2xl text-[#ECECEC] placeholder-[#8E8E93] focus:outline-none focus:ring-2 focus:ring-[#20808D] focus:border-transparent transition-all text-sm"
                style={{ fontWeight: 400 }}
              />
              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
                <button className="w-9 h-9 flex items-center justify-center hover:bg-white/5 rounded-lg transition-colors">
                  <Paperclip className="w-4 h-4 text-[#8E8E93]" />
                </button>
                <button
                  onClick={handleSend}
                  disabled={!input.trim()}
                  className="w-9 h-9 bg-gradient-to-r from-[#20808D] to-[#268a98] rounded-lg flex items-center justify-center hover:shadow-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Send className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

