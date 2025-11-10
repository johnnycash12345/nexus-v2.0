import { CheckCircle, Brain, Sparkles } from "lucide-react";
import { motion } from "motion/react";

interface SynapseConfirmationProps {
  show: boolean;
  onComplete: () => void;
}

export function SynapseConfirmation({ show, onComplete }: SynapseConfirmationProps) {
  if (!show) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8, y: 20 }}
      onAnimationComplete={() => {
        setTimeout(onComplete, 2000);
      }}
      className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50"
    >
      <div className="bg-[#2A2B2E] border border-[#20808D] rounded-2xl p-8 shadow-2xl">
        <div className="flex flex-col items-center gap-4">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 360],
            }}
            transition={{
              duration: 1,
              ease: "easeInOut",
            }}
            className="w-16 h-16 rounded-full bg-gradient-to-br from-[#20808D] to-[#268a98] flex items-center justify-center"
          >
            <Brain className="w-8 h-8 text-white" strokeWidth={1.5} />
          </motion.div>

          <div className="text-center">
            <div className="flex items-center gap-2 justify-center mb-2">
              <CheckCircle className="w-5 h-5 text-[#00C896]" strokeWidth={1.5} />
              <h3 className="text-lg text-[#ECECEC]" style={{ fontWeight: 500 }}>
                Sinapse Criada!
              </h3>
            </div>
            <p className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
              Conhecimento consolidado no Graph DB
            </p>
          </div>

          {/* Animated particles */}
          <div className="relative w-full h-8">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 1, y: 0, x: 0 }}
                animate={{
                  opacity: [1, 0],
                  y: [-20, -60],
                  x: [(i - 2) * 10, (i - 2) * 30],
                }}
                transition={{
                  duration: 1.5,
                  delay: i * 0.1,
                }}
                className="absolute top-0 left-1/2"
              >
                <Sparkles className="w-4 h-4 text-[#20808D]" />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
