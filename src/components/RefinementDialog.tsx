import { useState } from "react";
import { X, RefreshCw, Send } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface RefinementDialogProps {
  isOpen: boolean;
  onClose: () => void;
  originalResponse: string;
  onRefine: (feedback: string) => void;
  isRefining: boolean;
}

export function RefinementDialog({
  isOpen,
  onClose,
  originalResponse,
  onRefine,
  isRefining
}: RefinementDialogProps) {
  const [feedback, setFeedback] = useState("");

  const handleSubmit = () => {
    if (!feedback.trim()) return;
    onRefine(feedback);
    setFeedback("");
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Dialog */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-6">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-[#2A2B2E] border border-[#3E3F45] rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
            >
              {/* Header */}
              <div className="px-6 py-4 border-b border-[#3E3F45] flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#7B61FF]/20 flex items-center justify-center">
                    <RefreshCw className="w-5 h-5 text-[#7B61FF]" strokeWidth={1.5} />
                  </div>
                  <div>
                    <h2 className="text-lg text-[#ECECEC]" style={{ fontWeight: 500 }}>
                      Ciclo de Refinamento de Resposta
                    </h2>
                    <p className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
                      Forneça feedback para melhorar a resposta
                    </p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="w-8 h-8 flex items-center justify-center hover:bg-[#3E3F45] rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-[#8E8E93]" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 overflow-y-auto max-h-[calc(80vh-200px)]">
                {/* Original Response */}
                <div className="mb-6">
                  <div className="text-xs text-[#8E8E93] mb-2" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                    RESPOSTA ORIGINAL (R1)
                  </div>
                  <div className="p-4 bg-[#202123] border border-[#3E3F45] rounded-lg">
                    <p className="text-sm text-[#ECECEC] leading-relaxed" style={{ fontWeight: 400 }}>
                      {originalResponse}
                    </p>
                  </div>
                </div>

                {/* Feedback Input */}
                <div>
                  <div className="text-xs text-[#8E8E93] mb-2" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                    SEU FEEDBACK / CONTEXTO ADICIONAL
                  </div>
                  <textarea
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === "Enter" && e.ctrlKey) {
                        handleSubmit();
                      }
                    }}
                    placeholder="Ex: 'Adicione mais exemplos práticos' ou 'Foque em aplicações empresariais' ou 'Simplifique a explicação'..."
                    className="w-full h-32 px-4 py-3 bg-[#202123] border border-[#3E3F45] rounded-lg text-[#ECECEC] placeholder-[#8E8E93] focus:outline-none focus:ring-2 focus:ring-[#7B61FF] focus:border-transparent resize-none text-sm"
                    style={{ fontWeight: 400 }}
                    disabled={isRefining}
                  />
                  <p className="text-xs text-[#8E8E93] mt-2" style={{ fontWeight: 400 }}>
                    Pressione Ctrl+Enter para enviar
                  </p>
                </div>

                {/* Info Box */}
                <div className="mt-4 p-3 bg-[#7B61FF]/10 border border-[#7B61FF]/30 rounded-lg">
                  <p className="text-xs text-[#7B61FF]" style={{ fontWeight: 400 }}>
                    💡 O Nexus usará seu feedback para gerar uma resposta melhorada (R2), 
                    aplicando os agentes cognitivos IA1, IA2 e IA3 com o novo contexto.
                  </p>
                </div>
              </div>

              {/* Footer */}
              <div className="px-6 py-4 border-t border-[#3E3F45] flex items-center justify-between">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-sm text-[#8E8E93] hover:text-[#ECECEC] transition-colors"
                  style={{ fontWeight: 400 }}
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!feedback.trim() || isRefining}
                  className="px-5 py-2.5 bg-gradient-to-r from-[#7B61FF] to-[#8B71FF] text-white rounded-lg hover:shadow-lg hover:shadow-[#7B61FF]/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
                  style={{ fontWeight: 500 }}
                >
                  {isRefining ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Refinando...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Refinar Resposta
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
