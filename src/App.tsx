import { useState, useEffect } from "react";
import { NexusSidebar } from "./components/NexusSidebar";
import { HomePage } from "./components/HomePage";
import { ChatPage } from "./components/ChatPage";
import { CodePage } from "./components/CodePage";
import { UniversalInboxPage } from "./components/UniversalInboxPage";
import { TimelinePage } from "./components/TimelinePage";
import { MemoryPage } from "./components/MemoryPage";
import { CognitivePage } from "./components/CognitivePage";
import { SettingsPage } from "./components/SettingsPage";
import { ProactiveChatPage } from "./components/ProactiveChatPage";
import { NotificationSystem, useNotifications } from "./components/NotificationSystem";
import { QuickActionsMenu } from "./components/QuickActionsMenu";
import { motion, AnimatePresence } from "motion/react";

export default function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [selectedInboxItemId, setSelectedInboxItemId] = useState<string | null>(null);
  const { notifications, addNotification, dismissNotification } = useNotifications();

  // Demo: Adicionar notificações de exemplo
  useEffect(() => {
    const timers = [
      setTimeout(() => {
        addNotification("info", "Sistema Inicializado", "Nexus está pronto para uso");
      }, 1000),
      setTimeout(() => {
        addNotification("success", "Agentes Cognitivos Online", "IA1, IA2 e IA3 conectados");
      }, 2000),
    ];

    return () => timers.forEach(clearTimeout);
  }, []);

  const handleNavigate = (page: string) => {
    if (page.startsWith("proactiveChat:")) {
      const [, itemId] = page.split(":");
      setSelectedInboxItemId(itemId ?? null);
      setCurrentPage("proactiveChat");
      return;
    }

    setSelectedInboxItemId(null);
    setCurrentPage(page);
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return <HomePage onNavigate={handleNavigate} />;
      case "chat":
        return <ChatPage />;
      case "code":
        return <CodePage />;
      case "projects":
      case "universalInbox":
        return <UniversalInboxPage onNavigate={handleNavigate} />;
      case "timeline":
        return <TimelinePage />;
      case "memory":
        return <MemoryPage />;
      case "cognitive":
        return <CognitivePage />;
      case "settings":
        return <SettingsPage />;
      case "proactiveChat":
        return selectedInboxItemId ? (
          <ProactiveChatPage itemId={selectedInboxItemId} onNavigate={handleNavigate} />
        ) : (
          <UniversalInboxPage onNavigate={handleNavigate} />
        );
      default:
        return <HomePage onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#202123] text-white">
      <NexusSidebar currentPage={currentPage} onNavigate={handleNavigate} />
      
      <div className="pl-16">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Notification System */}
      <NotificationSystem
        notifications={notifications}
        onDismiss={dismissNotification}
      />

      {/* Quick Actions Menu */}
      <QuickActionsMenu onNavigate={handleNavigate} />

      <style>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #20808D;
          cursor: pointer;
        }

        .slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #20808D;
          cursor: pointer;
          border: none;
        }

        .slider::-webkit-slider-runnable-track {
          background: #3E3F45;
          border-radius: 8px;
        }

        .slider::-moz-range-track {
          background: #3E3F45;
          border-radius: 8px;
        }

        ::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }

        ::-webkit-scrollbar-track {
          background: transparent;
        }

        ::-webkit-scrollbar-thumb {
          background: #3E3F45;
          border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: #4E4F55;
        }
      `}</style>
    </div>
  );
}
