import { useState, useEffect } from "react";
import { X, CheckCircle, AlertTriangle, Info, Loader } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

export type NotificationType = "success" | "error" | "info" | "processing";

export interface Notification {
  id: number;
  type: NotificationType;
  title: string;
  message: string;
  duration?: number;
}

interface NotificationSystemProps {
  notifications: Notification[];
  onDismiss: (id: number) => void;
}

export function NotificationSystem({ notifications, onDismiss }: NotificationSystemProps) {
  const getIcon = (type: NotificationType) => {
    switch (type) {
      case "success":
        return <CheckCircle className="w-5 h-5 text-[#00C896]" strokeWidth={1.5} />;
      case "error":
        return <AlertTriangle className="w-5 h-5 text-[#FF6B6B]" strokeWidth={1.5} />;
      case "processing":
        return <Loader className="w-5 h-5 text-[#20808D] animate-spin" strokeWidth={1.5} />;
      default:
        return <Info className="w-5 h-5 text-[#7B61FF]" strokeWidth={1.5} />;
    }
  };

  const getColor = (type: NotificationType) => {
    switch (type) {
      case "success":
        return "#00C896";
      case "error":
        return "#FF6B6B";
      case "processing":
        return "#20808D";
      default:
        return "#7B61FF";
    }
  };

  useEffect(() => {
    notifications.forEach((notification) => {
      if (notification.duration && notification.type !== "processing") {
        const timer = setTimeout(() => {
          onDismiss(notification.id);
        }, notification.duration);
        return () => clearTimeout(timer);
      }
    });
  }, [notifications, onDismiss]);

  return (
    <div className="fixed top-6 right-6 z-50 space-y-3 w-96">
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: 100, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.8 }}
            className="bg-[#2A2B2E] border border-[#3E3F45] rounded-xl p-4 shadow-2xl backdrop-blur-sm"
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                {getIcon(notification.type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <h4 
                    className="text-sm text-[#ECECEC]" 
                    style={{ fontWeight: 500 }}
                  >
                    {notification.title}
                  </h4>
                  {notification.type !== "processing" && (
                    <button
                      onClick={() => onDismiss(notification.id)}
                      className="flex-shrink-0 w-5 h-5 flex items-center justify-center hover:bg-[#3E3F45] rounded transition-colors"
                    >
                      <X className="w-4 h-4 text-[#8E8E93]" />
                    </button>
                  )}
                </div>
                <p className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
                  {notification.message}
                </p>
              </div>
            </div>
            {notification.duration && notification.type !== "processing" && (
              <motion.div
                initial={{ width: "100%" }}
                animate={{ width: "0%" }}
                transition={{ duration: notification.duration / 1000, ease: "linear" }}
                className="h-0.5 mt-3 rounded-full"
                style={{ backgroundColor: getColor(notification.type) }}
              />
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

// Hook para gerenciar notificações
export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  let nextId = 1;

  const addNotification = (
    type: NotificationType,
    title: string,
    message: string,
    duration: number = 5000
  ) => {
    const notification: Notification = {
      id: nextId++,
      type,
      title,
      message,
      duration: type === "processing" ? undefined : duration,
    };
    setNotifications((prev) => [...prev, notification]);
    return notification.id;
  };

  const dismissNotification = (id: number) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const updateNotification = (id: number, updates: Partial<Notification>) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, ...updates } : n))
    );
  };

  return {
    notifications,
    addNotification,
    dismissNotification,
    updateNotification,
  };
}
