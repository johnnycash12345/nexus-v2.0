import { motion } from "motion/react";
import { Loader, Brain, Code, Search } from "lucide-react";

interface ProcessingIndicatorProps {
  message?: string;
  type?: "general" | "cognitive" | "code" | "research";
  inline?: boolean;
}

export function ProcessingIndicator({ 
  message = "Processando...", 
  type = "general",
  inline = false 
}: ProcessingIndicatorProps) {
  const getIcon = () => {
    switch (type) {
      case "cognitive":
        return <Brain className="w-5 h-5 text-[#20808D]" strokeWidth={1.5} />;
      case "code":
        return <Code className="w-5 h-5 text-[#FFD75E]" strokeWidth={1.5} />;
      case "research":
        return <Search className="w-5 h-5 text-[#7B61FF]" strokeWidth={1.5} />;
      default:
        return <Loader className="w-5 h-5 text-[#20808D] animate-spin" strokeWidth={1.5} />;
    }
  };

  const getAgentIndicators = () => {
    if (type !== "cognitive") return null;
    
    return (
      <div className="flex gap-2 mt-3">
        <motion.div
          animate={{ 
            opacity: [0.3, 1, 0.3],
            scale: [0.95, 1.05, 0.95]
          }}
          transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
          className="px-3 py-1.5 bg-[#20808D]/20 border border-[#20808D]/30 rounded-lg text-xs text-[#20808D]"
          style={{ fontWeight: 400 }}
        >
          IA1 - Extractor
        </motion.div>
        <motion.div
          animate={{ 
            opacity: [0.3, 1, 0.3],
            scale: [0.95, 1.05, 0.95]
          }}
          transition={{ duration: 1.5, repeat: Infinity, delay: 0.3 }}
          className="px-3 py-1.5 bg-[#7B61FF]/20 border border-[#7B61FF]/30 rounded-lg text-xs text-[#7B61FF]"
          style={{ fontWeight: 400 }}
        >
          IA2 - Reasoner
        </motion.div>
        <motion.div
          animate={{ 
            opacity: [0.3, 1, 0.3],
            scale: [0.95, 1.05, 0.95]
          }}
          transition={{ duration: 1.5, repeat: Infinity, delay: 0.6 }}
          className="px-3 py-1.5 bg-[#FFD75E]/20 border border-[#FFD75E]/30 rounded-lg text-xs text-[#FFD75E]"
          style={{ fontWeight: 400 }}
        >
          IA3 - Validator
        </motion.div>
      </div>
    );
  };

  if (inline) {
    return (
      <div className="flex items-center gap-3">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          {getIcon()}
        </motion.div>
        <span className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
          {message}
        </span>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-12"
    >
      <motion.div
        animate={{ 
          scale: [1, 1.1, 1],
          rotate: type === "general" ? 360 : 0
        }}
        transition={{ 
          duration: type === "general" ? 2 : 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="mb-4"
      >
        {getIcon()}
      </motion.div>
      
      <p className="text-[#ECECEC] mb-2" style={{ fontWeight: 400 }}>
        {message}
      </p>
      
      {type === "cognitive" && (
        <p className="text-xs text-[#8E8E93] mb-4" style={{ fontWeight: 400 }}>
          Agentes cognitivos trabalhando em sinergia
        </p>
      )}

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

      {getAgentIndicators()}
    </motion.div>
  );
}
