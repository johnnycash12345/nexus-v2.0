import { useState } from "react";
import { Plus, X, MessageSquare, Code, Brain, Inbox, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface QuickActionsMenuProps {
  onNavigate: (page: string) => void;
}

export function QuickActionsMenu({ onNavigate }: QuickActionsMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

  const actions = [
    {
      id: "chat",
      label: "Nova Conversa",
      icon: MessageSquare,
      color: "#20808D",
      description: "Iniciar chat pessoal",
    },
    {
      id: "code",
      label: "Novo Código",
      icon: Code,
      color: "#FFD75E",
      description: "Gerar código com IA",
    },
    {
      id: "universalInbox",
      label: "Caixa de Entrada",
      icon: Inbox,
      color: "#7B61FF",
      description: "Ver itens do Nexus",
    },
    {
      id: "memory",
      label: "Memória",
      icon: Brain,
      color: "#00C6FF",
      description: "Ver conhecimento",
    },
  ];

  const handleAction = (actionId: string) => {
    onNavigate(actionId);
    setIsOpen(false);
  };

  return (
    <div className="fixed bottom-8 right-8 z-40">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            className="absolute bottom-20 right-0 w-64 bg-[#2A2B2E] border border-[#3E3F45] rounded-xl shadow-2xl overflow-hidden"
          >
            <div className="p-3 border-b border-[#3E3F45]">
              <div className="text-xs text-[#8E8E93]" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                AÇÕES RÁPIDAS
              </div>
            </div>
            <div className="p-2">
              {actions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <motion.button
                    key={action.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ x: 4 }}
                    onClick={() => handleAction(action.id)}
                    className="w-full p-3 rounded-lg hover:bg-[#3E3F45] transition-all flex items-center gap-3 group"
                  >
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform"
                      style={{ backgroundColor: action.color + '20' }}
                    >
                      <Icon className="w-5 h-5" style={{ color: action.color }} strokeWidth={1.5} />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="text-sm text-[#ECECEC] mb-0.5" style={{ fontWeight: 500 }}>
                        {action.label}
                      </div>
                      <div className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
                        {action.description}
                      </div>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 rounded-full bg-gradient-to-br from-[#20808D] to-[#268a98] flex items-center justify-center shadow-2xl hover:shadow-[#20808D]/30 transition-all group relative overflow-hidden"
      >
        {/* Pulse effect */}
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.5, 0, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute inset-0 rounded-full bg-[#20808D]"
        />

        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <X className="w-6 h-6 text-white relative z-10" strokeWidth={2} />
            </motion.div>
          ) : (
            <motion.div
              key="open"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Sparkles className="w-6 h-6 text-white relative z-10" strokeWidth={2} />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </div>
  );
}
