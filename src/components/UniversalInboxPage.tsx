import { useEffect, useState } from "react";
import {
  FolderKanban,
  AlarmClock,
  GraduationCap,
  ListChecks,
  StickyNote,
  Inbox,
  LucideIcon,
  Loader2,
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

type InboxItemType = "Projeto" | "Lembrete" | "Tópico de Estudo" | "Lista" | "Nota Simples";

interface InboxItem {
  id: string;
  content: string;
  type: InboxItemType;
}

interface UniversalInboxPageProps {
  onNavigate: (page: string) => void;
}

const typeConfig: Record<InboxItemType, { icon: LucideIcon; color: string }> = {
  Projeto: { icon: FolderKanban, color: "#20808D" },
  Lembrete: { icon: AlarmClock, color: "#FFD75E" },
  "Tópico de Estudo": { icon: GraduationCap, color: "#7B61FF" },
  Lista: { icon: ListChecks, color: "#268a98" },
  "Nota Simples": { icon: StickyNote, color: "#8E8E93" },
};

export function UniversalInboxPage({ onNavigate }: UniversalInboxPageProps) {
  const [items, setItems] = useState<InboxItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchItems = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/inbox/items", {
          method: "GET",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Falha ao carregar a caixa de entrada.");
        }

        const data: InboxItem[] = await response.json();
        setItems(data);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }

        setError(err instanceof Error ? err.message : "Erro inesperado ao buscar itens.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchItems();

    return () => {
      controller.abort();
    };
  }, []);

  const handleCardClick = (itemId: string) => {
    onNavigate(`proactiveChat:${itemId}`);
  };

  return (
    <div className="min-h-screen bg-[#202123]">
      <div className="border-b border-[#3E3F45] bg-[#2A2B2E]">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl text-[#ECECEC]" style={{ fontWeight: 500 }}>
                Caixa de Entrada Universal
              </h1>
              <p className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
                Todos os itens capturados pelo Nexus aparecem aqui em tempo real.
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
          <div className="flex items-center justify-center py-12 text-[#8E8E93]">
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Carregando itens da caixa de entrada...
          </div>
        ) : (
          <AnimatePresence>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {items.map((item) => {
                const config = typeConfig[item.type] ?? { icon: Inbox, color: "#4E4F55" };
                const Icon = config.icon;

                return (
                  <motion.button
                    key={item.id}
                    layout
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -6 }}
                    transition={{ duration: 0.2 }}
                    onClick={() => handleCardClick(item.id)}
                    className="w-full rounded-xl border border-[#3E3F45] bg-[#2A2B2E] p-5 text-left transition-all hover:-translate-y-1 hover:border-[#4E4F55] hover:bg-[#2F3033] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#20808D]"
                  >
                    <div className="mb-3 flex items-center gap-3">
                      <div
                        className="flex h-10 w-10 items-center justify-center rounded-lg"
                        style={{ backgroundColor: `${config.color}20` }}
                      >
                        <Icon className="h-5 w-5" style={{ color: config.color }} strokeWidth={1.6} />
                      </div>
                      <span className="text-sm text-[#8E8E93]" style={{ fontWeight: 500 }}>
                        {item.type}
                      </span>
                    </div>
                    <p className="text-[#ECECEC]" style={{ fontWeight: 400 }}>
                      {item.content}
                    </p>
                  </motion.button>
                );
              })}

              {!items.length && !error && (
                <div className="col-span-full rounded-xl border border-dashed border-[#3E3F45] bg-[#25262A] p-10 text-center text-sm text-[#8E8E93]">
                  Nenhum item foi capturado até o momento.
                </div>
              )}
            </div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
