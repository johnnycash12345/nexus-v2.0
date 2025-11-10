import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Bot, Loader2, Send, User } from "lucide-react";
import { motion } from "motion/react";

interface ProactiveChatMessage {
  id: string;
  role: "assistant" | "user";
  content: string;
}

interface ProactiveChatPageProps {
  itemId: string;
  onNavigate: (page: string) => void;
}

export function ProactiveChatPage({ itemId, onNavigate }: ProactiveChatPageProps) {
  const [messages, setMessages] = useState<ProactiveChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchMessages = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/inbox/chat/${itemId}`, {
          method: "GET",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Não foi possível carregar o histórico deste item.");
        }

        const data: ProactiveChatMessage[] = await response.json();
        setMessages(data);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }

        setError(err instanceof Error ? err.message : "Erro inesperado ao carregar o chat.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchMessages();

    return () => controller.abort();
  }, [itemId]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendResponse = async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput) return;

    setError(null);
    setIsSending(true);

    try {
      const response = await fetch(`/api/inbox/chat/${itemId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: trimmedInput }),
      });

      if (!response.ok) {
        throw new Error("Não foi possível enviar sua resposta agora.");
      }

      const updatedMessages: ProactiveChatMessage[] = await response.json();
      setMessages(updatedMessages);
      setInputValue("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro inesperado ao enviar a resposta.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#202123]">
      <div className="border-b border-[#3E3F45] bg-[#2A2B2E]">
        <div className="flex items-center justify-between px-8 py-6">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => onNavigate("universalInbox")}
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-[#3E3F45] text-[#8E8E93] transition-colors hover:border-[#20808D] hover:text-[#ECECEC]"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl text-[#ECECEC]" style={{ fontWeight: 500 }}>
                Chat Dedicado Proativo
              </h1>
              <p className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
                Item vinculado: <span className="text-[#ECECEC]">{itemId}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="px-8 py-8">
        {error && (
          <div className="mb-6 rounded-lg border border-[#3E3F45] bg-[#2A2B2E] px-5 py-4 text-sm text-[#FFD75E]">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex h-[65vh] items-center justify-center text-[#8E8E93]">
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Carregando histórico proativo...
          </div>
        ) : (
          <div className="flex h-[65vh] flex-col overflow-hidden rounded-2xl border border-[#3E3F45] bg-[#1E1F22]">
            <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
              {messages.map((message) => {
                const isAssistant = message.role === "assistant";
                return (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex items-start gap-3 ${isAssistant ? "justify-start" : "justify-end"}`}
                  >
                    {isAssistant && (
                      <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-lg bg-[#20808D]/20">
                        <Bot className="h-4 w-4 text-[#20808D]" />
                      </div>
                    )}
                    <div
                      className={`max-w-lg rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                        isAssistant
                          ? "bg-[#2A2B2E] text-[#ECECEC] border border-[#3E3F45]"
                          : "bg-[#20808D] text-white"
                      }`}
                    >
                      {message.content}
                    </div>
                    {!isAssistant && (
                      <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-lg bg-[#20808D]/20">
                        <User className="h-4 w-4 text-[#ECECEC]" />
                      </div>
                    )}
                  </motion.div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            <div className="border-t border-[#3E3F45] bg-[#222327] px-6 py-4">
              <div className="flex items-end gap-3">
                <textarea
                  value={inputValue}
                  onChange={(event) => setInputValue(event.target.value)}
                  placeholder="Responda à mensagem proativa do Nexus..."
                  className="min-h-[52px] flex-1 resize-none rounded-xl border border-[#3E3F45] bg-[#1B1C1F] px-4 py-3 text-sm text-[#ECECEC] placeholder:text-[#5A5B60] focus:border-[#20808D] focus:outline-none focus:ring-2 focus:ring-[#20808D]/40"
                  rows={2}
                />
                <button
                  type="button"
                  onClick={handleSendResponse}
                  disabled={isSending || !inputValue.trim()}
                  className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#20808D] text-white transition-all hover:bg-[#268a98] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSending ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
