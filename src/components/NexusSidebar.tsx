import { Search, MessageSquare, Code, Brain, Settings, Plus, Clock, Inbox, Network } from "lucide-react";
import { motion } from "motion/react";

interface NexusSidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export function NexusSidebar({ currentPage, onNavigate }: NexusSidebarProps) {
  const navItems = [
    { id: "home", icon: Search, label: "Search & Chat" },
    { id: "chat", icon: MessageSquare, label: "Personal Chat" },
    { id: "code", icon: Code, label: "Development" },
    { id: "universalInbox", icon: Inbox, label: "Caixa de Entrada Universal" },
    { id: "timeline", icon: Clock, label: "Timeline & Logs" },
    { id: "memory", icon: Network, label: "Synaptic Memory" },
    { id: "cognitive", icon: Brain, label: "Cognitive Monitor" },
  ];

  return (
    <div className="fixed left-0 top-0 h-screen w-16 bg-[#2A2B2E] flex flex-col items-center py-4 z-50 border-r border-[#3E3F45]">
      {/* Logo */}
      <button 
        onClick={() => onNavigate("home")}
        className="w-10 h-10 mb-6 flex items-center justify-center group relative"
      >
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#20808D] to-[#268a98] flex items-center justify-center shadow-lg">
          <span className="text-white text-sm" style={{ fontWeight: 600 }}>N</span>
        </div>
        
        {/* Pulse animation */}
        <div className="absolute inset-0 rounded-lg bg-[#20808D] opacity-0 group-hover:opacity-20 animate-pulse" />
      </button>

      {/* New Session Button */}
      <button 
        onClick={() => onNavigate("home")}
        className="w-10 h-10 mb-8 flex items-center justify-center hover:bg-[#3E3F45] rounded-lg transition-all group relative"
      >
        <Plus className="w-5 h-5 text-[#8E8E93] group-hover:text-[#20808D]" strokeWidth={2} />
        
        <div className="absolute left-full ml-4 px-3 py-1.5 bg-[#2A2B2E] border border-[#3E3F45] rounded-md opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 shadow-xl">
          <span className="text-xs text-[#ECECEC]" style={{ fontWeight: 400 }}>New Session</span>
        </div>
      </button>
      
      {/* Navigation */}
      <nav className="flex-1 flex flex-col gap-2 w-full px-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          
          return (
            <div key={item.id} className="relative group">
              <button
                onClick={() => onNavigate(item.id)}
                className={`w-full h-10 rounded-lg flex items-center justify-center transition-all relative overflow-hidden ${
                  isActive 
                    ? "bg-[#20808D]/20 text-[#20808D]" 
                    : "text-[#8E8E93] hover:bg-[#3E3F45] hover:text-[#ECECEC]"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-[#20808D]/10 border-l-2 border-[#20808D]"
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
                <Icon className="w-5 h-5 relative z-10" strokeWidth={1.5} />
              </button>
              
              {/* Tooltip */}
              <div className="absolute left-full ml-4 px-3 py-1.5 bg-[#2A2B2E] border border-[#3E3F45] rounded-md opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 shadow-xl">
                <span className="text-xs text-[#ECECEC]" style={{ fontWeight: 400 }}>{item.label}</span>
              </div>
            </div>
          );
        })}
      </nav>

      <div className="w-full h-px bg-[#3E3F45] my-2" />

      {/* Settings */}
      <div className="relative group">
        <button
          onClick={() => onNavigate("settings")}
          className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
            currentPage === "settings"
              ? "bg-[#20808D]/20 text-[#20808D]" 
              : "text-[#8E8E93] hover:bg-[#3E3F45] hover:text-[#ECECEC]"
          }`}
        >
          <Settings className="w-5 h-5" strokeWidth={1.5} />
        </button>
        
        <div className="absolute left-full ml-4 px-3 py-1.5 bg-[#2A2B2E] border border-[#3E3F45] rounded-md opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 shadow-xl">
          <span className="text-xs text-[#ECECEC]" style={{ fontWeight: 400 }}>Settings</span>
        </div>
      </div>
    </div>
  );
}
