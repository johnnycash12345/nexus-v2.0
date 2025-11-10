import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Copy, ThumbsUp, ThumbsDown, Paperclip, Pin, Sparkles, ChevronDown, RefreshCw, Brain } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { RefinementDialog } from "./RefinementDialog";
import { SynapseConfirmation } from "./SynapseConfirmation";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  isRefined?: boolean;
  originalContent?: string;
  refinementFeedback?: string;
}

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "assistant",
      content: "Olá! Sou o Nexus, seu assistente cognitivo de IA. Como posso ajudá-lo hoje?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Refinement states
  const [refinementDialogOpen, setRefinementDialogOpen] = useState(false);
  const [selectedMessageForRefinement, setSelectedMessageForRefinement] = useState<Message | null>(null);
  const [isRefining, setIsRefining] = useState(false);
  
  // Synapse states
  const [showSynapseConfirmation, setShowSynapseConfirmation] = useState(false);
  const [savingToMemory, setSavingToMemory] = useState<number | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      const aiMessage: Message = {
        id: messages.length + 2,
        role: "assistant",
        content: `Entendi sua pergunta: "${input}". Estou processando através dos agentes cognitivos IA1 (Extractor), IA2 (Reasoner) e IA3 (Validator) para fornecer a melhor resposta possível. Este é um exemplo de resposta do sistema Nexus que demonstra o poder do processamento cognitivo autônomo.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  };

  // Handle synapse creation (save to memory)
  const handleSaveToMemory = (messageId: number) => {
    setSavingToMemory(messageId);
    
    // Simulate API call to backend
    setTimeout(() => {
      setSavingToMemory(null);
      setShowSynapseConfirmation(true);
      
      // TODO: Actual API call
      // await fetch('/api/memory/synapse', {
      //   method: 'POST',
      //   body: JSON.stringify({ messageId, content: message.content })
      // });
    }, 1500);
  };

  // Handle refinement request
  const handleOpenRefinement = (message: Message) => {
    setSelectedMessageForRefinement(message);
    setRefinementDialogOpen(true);
  };

  // Handle refinement submission
  const handleRefineResponse = (feedback: string) => {
    if (!selectedMessageForRefinement) return;
    
    setIsRefining(true);
    
    // Simulate API call to backend for refinement
    setTimeout(() => {
      const refinedMessage: Message = {
        id: messages.length + 1,
        role: "assistant",
        content: `[Resposta Refinada - R2]\n\nBaseado no seu feedback: "${feedback}"\n\n${selectedMessageForRefinement.content}\n\n[Melhorias aplicadas pelos agentes cognitivos]\n• IA1 (Extractor) analisou o contexto adicional\n• IA2 (Reasoner) aplicou nova lógica de raciocínio\n• IA3 (Validator) validou a resposta melhorada\n\nEsta resposta incorpora seu feedback e oferece uma explicação mais alinhada às suas necessidades.`,
        timestamp: new Date(),
        isRefined: true,
        originalContent: selectedMessageForRefinement.content,
        refinementFeedback: feedback,
      };
      
      setMessages((prev) => [...prev, refinedMessage]);
      setIsRefining(false);
      setRefinementDialogOpen(false);
      setSelectedMessageForRefinement(null);
      
      // TODO: Actual API call
      // await fetch('/api/chat/refine', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     originalResponse: selectedMessageForRefinement.content,
      //     feedback: feedback
      //   })
      // });
    }, 2500);
  };

  return (
    <div className="h-screen flex flex-col bg-[#202123]">
      {/* Refinement Dialog */}
      <RefinementDialog
        isOpen={refinementDialogOpen}
        onClose={() => {
          setRefinementDialogOpen(false);
          setSelectedMessageForRefinement(null);
        }}
        originalResponse={selectedMessageForRefinement?.content || ""}
        onRefine={handleRefineResponse}
        isRefining={isRefining}
      />

      {/* Synapse Confirmation */}
      <SynapseConfirmation
        show={showSynapseConfirmation}
        onComplete={() => setShowSynapseConfirmation(false)}
      />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 py-12 space-y-8">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="group"
              >
                <div className="flex gap-4">
                  {/* Avatar */}
                  <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 bg-gradient-to-br from-[#20808D] to-[#268a98]">
                    {message.role === "assistant" ? (
                      <Bot className="w-4 h-4 text-white" strokeWidth={1.5} />
                    ) : (
                      <User className="w-4 h-4 text-white" strokeWidth={1.5} />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 pt-0.5">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm text-[#ECECEC]" style={{ fontWeight: 500 }}>
                        {message.role === "assistant" ? "Nexus" : "Você"}
                      </span>
                      <span className="text-xs text-[#8E8E93]">{formatTime(message.timestamp)}</span>
                    </div>
                    
                    {/* Refined Badge */}
                    {message.isRefined && (
                      <div className="mb-2 inline-flex items-center gap-2 px-3 py-1.5 bg-[#7B61FF]/10 border border-[#7B61FF]/30 rounded-lg">
                        <RefreshCw className="w-3.5 h-3.5 text-[#7B61FF]" />
                        <span className="text-xs text-[#7B61FF]" style={{ fontWeight: 500 }}>
                          Resposta Refinada (R2)
                        </span>
                      </div>
                    )}
                    
                    <p className="text-[#ECECEC] leading-relaxed mb-3 whitespace-pre-line" style={{ fontWeight: 400 }}>
                      {message.content}
                    </p>

                    {/* Refinement Info */}
                    {message.isRefined && message.refinementFeedback && (
                      <div className="mt-3 p-3 bg-[#202123] border border-[#3E3F45] rounded-lg">
                        <div className="text-xs text-[#8E8E93] mb-1" style={{ fontWeight: 500 }}>
                          Feedback aplicado:
                        </div>
                        <p className="text-xs text-[#ECECEC]" style={{ fontWeight: 400 }}>
                          "{message.refinementFeedback}"
                        </p>
                      </div>
                    )}

                    {/* Actions */}
                    {message.role === "assistant" && (
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => navigator.clipboard.writeText(message.content)}
                          className="w-7 h-7 flex items-center justify-center hover:bg-[#2A2B2E] rounded-md transition-colors group/btn"
                          title="Copiar"
                        >
                          <Copy className="w-3.5 h-3.5 text-[#8E8E93] group-hover/btn:text-[#20808D]" />
                        </button>
                        <button 
                          className="w-7 h-7 flex items-center justify-center hover:bg-[#2A2B2E] rounded-md transition-colors group/btn"
                          title="Fixar"
                        >
                          <Pin className="w-3.5 h-3.5 text-[#8E8E93] group-hover/btn:text-[#FFD75E]" />
                        </button>
                        
                        {/* Save to Memory (Synapse) Button */}
                        <button 
                          onClick={() => handleSaveToMemory(message.id)}
                          disabled={savingToMemory === message.id}
                          className="px-3 py-1.5 flex items-center gap-1.5 hover:bg-[#20808D]/10 border border-transparent hover:border-[#20808D]/30 rounded-md transition-all group/btn disabled:opacity-50"
                          title="Salvar na Memória Sináptica"
                        >
                          {savingToMemory === message.id ? (
                            <>
                              <Brain className="w-3.5 h-3.5 text-[#20808D] animate-pulse" />
                              <span className="text-xs text-[#20808D]" style={{ fontWeight: 500 }}>
                                Salvando...
                              </span>
                            </>
                          ) : (
                            <>
                              <Brain className="w-3.5 h-3.5 text-[#8E8E93] group-hover/btn:text-[#20808D]" />
                              <span className="text-xs text-[#8E8E93] group-hover/btn:text-[#20808D]" style={{ fontWeight: 500 }}>
                                Salvar na Memória
                              </span>
                            </>
                          )}
                        </button>

                        {/* Refine Button */}
                        <button 
                          onClick={() => handleOpenRefinement(message)}
                          className="px-3 py-1.5 flex items-center gap-1.5 hover:bg-[#7B61FF]/10 border border-transparent hover:border-[#7B61FF]/30 rounded-md transition-all group/btn"
                          title="Refinar Resposta"
                        >
                          <RefreshCw className="w-3.5 h-3.5 text-[#8E8E93] group-hover/btn:text-[#7B61FF]" />
                          <span className="text-xs text-[#8E8E93] group-hover/btn:text-[#7B61FF]" style={{ fontWeight: 500 }}>
                            Refinar
                          </span>
                        </button>

                        <div className="w-px h-4 bg-[#3E3F45] mx-1" />
                        
                        <button 
                          className="w-7 h-7 flex items-center justify-center hover:bg-[#2A2B2E] rounded-md transition-colors group/btn"
                          title="Ver Raciocínio"
                        >
                          <ChevronDown className="w-3.5 h-3.5 text-[#8E8E93] group-hover/btn:text-[#ECECEC]" />
                        </button>
                        <button 
                          className="w-7 h-7 flex items-center justify-center hover:bg-[#2A2B2E] rounded-md transition-colors group/btn"
                          title="Útil"
                        >
                          <ThumbsUp className="w-3.5 h-3.5 text-[#8E8E93] group-hover/btn:text-[#00C896]" />
                        </button>
                        <button 
                          className="w-7 h-7 flex items-center justify-center hover:bg-[#2A2B2E] rounded-md transition-colors group/btn"
                          title="Não útil"
                        >
                          <ThumbsDown className="w-3.5 h-3.5 text-[#8E8E93] group-hover/btn:text-[#FF6B6B]" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-4"
            >
              <div className="w-7 h-7 rounded-full flex items-center justify-center bg-gradient-to-br from-[#20808D] to-[#268a98]">
                <Bot className="w-4 h-4 text-white" strokeWidth={1.5} />
              </div>
              <div className="flex-1 pt-0.5">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm text-[#ECECEC]" style={{ fontWeight: 500 }}>Nexus</span>
                </div>
                <div className="flex gap-1.5">
                  <motion.div
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                    className="w-1.5 h-1.5 bg-[#8E8E93] rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                    className="w-1.5 h-1.5 bg-[#8E8E93] rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                    className="w-1.5 h-1.5 bg-[#8E8E93] rounded-full"
                  />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-[#3E3F45]">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              placeholder="Enviar mensagem..."
              className="w-full px-5 py-3 bg-[#2A2B2E] border-0 rounded-full text-[#ECECEC] placeholder-[#8E8E93] focus:outline-none focus:ring-1 focus:ring-[#20808D] transition-all text-sm"
              style={{ fontWeight: 400 }}
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
              <button className="w-8 h-8 flex items-center justify-center hover:bg-white/5 rounded-full transition-colors">
                <Paperclip className="w-4 h-4 text-[#8E8E93]" />
              </button>
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="w-8 h-8 bg-[#20808D] rounded-full flex items-center justify-center hover:bg-[#268a98] transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Send className="w-3.5 h-3.5 text-white" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
