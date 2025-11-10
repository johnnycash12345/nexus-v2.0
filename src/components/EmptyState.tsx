import { LucideIcon } from "lucide-react";
import { motion } from "motion/react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 px-6"
    >
      <motion.div
        animate={{
          y: [0, -10, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="mb-6"
      >
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#20808D]/20 to-[#268a98]/20 flex items-center justify-center">
          <Icon className="w-10 h-10 text-[#20808D]" strokeWidth={1.5} />
        </div>
      </motion.div>

      <h3 className="text-xl text-[#ECECEC] mb-2" style={{ fontWeight: 500 }}>
        {title}
      </h3>
      <p className="text-[#8E8E93] text-center mb-6 max-w-md" style={{ fontWeight: 400 }}>
        {description}
      </p>

      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-3 bg-gradient-to-r from-[#20808D] to-[#268a98] text-white rounded-lg hover:shadow-lg hover:shadow-[#20808D]/20 transition-all"
          style={{ fontWeight: 500 }}
        >
          {action.label}
        </button>
      )}
    </motion.div>
  );
}
