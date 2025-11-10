import { useState } from "react";
import { Sliders, Palette, Database, Plug } from "lucide-react";
import { motion } from "motion/react";

export function SettingsPage() {
  const [settings, setSettings] = useState({
    streaming: true,
    autoSave: true,
    darkMode: true,
    notifications: false,
    temperature: 0.7,
    maxTokens: 2048,
  });

  const [activeSection, setActiveSection] = useState("system");

  const sections = [
    { id: "system", label: "Sistema", icon: Sliders },
    { id: "integrations", label: "Integrações", icon: Plug },
    { id: "appearance", label: "Aparência", icon: Palette },
    { id: "memory", label: "Memória", icon: Database },
  ];

  const handleToggle = (key: string) => {
    setSettings({ ...settings, [key]: !settings[key as keyof typeof settings] });
  };

  return (
    <div className="min-h-screen bg-[#202123] flex">
      {/* Sidebar Navigation */}
      <div className="w-56 border-r border-[#3E3F45] p-4">
        <div className="mb-6">
          <h2 className="text-lg text-[#ECECEC] px-3" style={{ fontWeight: 400 }}>
            Configurações
          </h2>
        </div>

        <nav className="space-y-1">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`w-full px-3 py-2 rounded-lg flex items-center gap-3 transition-all text-sm ${
                  activeSection === section.id
                    ? "bg-[#2A2B2E] text-[#ECECEC]"
                    : "text-[#8E8E93] hover:bg-[#2A2B2E] hover:text-[#ECECEC]"
                }`}
                style={{ fontWeight: 400 }}
              >
                <Icon className="w-4 h-4" strokeWidth={1.5} />
                {section.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 px-8 py-8">
        <div className="max-w-2xl">
          <AnimatePresence mode="wait">
            {activeSection === "system" && (
              <motion.div
                key="system"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <h2 className="text-xl text-[#ECECEC] mb-6" style={{ fontWeight: 400 }}>
                  Sistema
                </h2>

                <div className="space-y-6">
                  {/* Toggle Settings */}
                  <div className="bg-[#2A2B2E] rounded-xl border border-[#3E3F45] divide-y divide-[#3E3F45]">
                    <ToggleRow
                      label="Streaming de Respostas"
                      description="Exibir respostas em tempo real"
                      checked={settings.streaming}
                      onChange={() => handleToggle("streaming")}
                    />
                    <ToggleRow
                      label="Auto-salvar"
                      description="Salvar automaticamente as conversas"
                      checked={settings.autoSave}
                      onChange={() => handleToggle("autoSave")}
                    />
                    <ToggleRow
                      label="Notificações"
                      description="Receber alertas do sistema"
                      checked={settings.notifications}
                      onChange={() => handleToggle("notifications")}
                    />
                  </div>

                  {/* Slider Settings */}
                  <div className="bg-[#2A2B2E] rounded-xl border border-[#3E3F45] p-5 space-y-6">
                    <div>
                      <div className="flex justify-between mb-3">
                        <label className="text-sm text-[#ECECEC]" style={{ fontWeight: 400 }}>
                          Temperature
                        </label>
                        <span className="text-sm text-[#8E8E93]">
                          {settings.temperature}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={settings.temperature}
                        onChange={(e) =>
                          setSettings({ ...settings, temperature: parseFloat(e.target.value) })
                        }
                        className="w-full h-1 bg-[#3E3F45] rounded-full appearance-none cursor-pointer slider"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between mb-3">
                        <label className="text-sm text-[#ECECEC]" style={{ fontWeight: 400 }}>
                          Max Tokens
                        </label>
                        <span className="text-sm text-[#8E8E93]">
                          {settings.maxTokens}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="256"
                        max="4096"
                        step="256"
                        value={settings.maxTokens}
                        onChange={(e) =>
                          setSettings({ ...settings, maxTokens: parseInt(e.target.value) })
                        }
                        className="w-full h-1 bg-[#3E3F45] rounded-full appearance-none cursor-pointer slider"
                      />
                    </div>
                  </div>

                  <button className="px-5 py-2.5 bg-[#20808D] hover:bg-[#268a98] text-white rounded-full transition-all text-sm"
                    style={{ fontWeight: 400 }}
                  >
                    Salvar Alterações
                  </button>
                </div>
              </motion.div>
            )}

            {activeSection === "integrations" && (
              <motion.div
                key="integrations"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <h2 className="text-xl text-[#ECECEC] mb-6" style={{ fontWeight: 400 }}>
                  Integrações
                </h2>
                <div className="bg-[#2A2B2E] rounded-xl border border-[#3E3F45] p-8 text-center">
                  <p className="text-[#8E8E93]" style={{ fontWeight: 400 }}>
                    Nenhuma integração configurada
                  </p>
                </div>
              </motion.div>
            )}

            {activeSection === "appearance" && (
              <motion.div
                key="appearance"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <h2 className="text-xl text-[#ECECEC] mb-6" style={{ fontWeight: 400 }}>
                  Aparência
                </h2>
                <div className="bg-[#2A2B2E] rounded-xl border border-[#3E3F45]">
                  <ToggleRow
                    label="Modo Escuro"
                    description="Usar tema escuro na interface"
                    checked={settings.darkMode}
                    onChange={() => handleToggle("darkMode")}
                  />
                </div>
              </motion.div>
            )}

            {activeSection === "memory" && (
              <motion.div
                key="memory"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <h2 className="text-xl text-[#ECECEC] mb-6" style={{ fontWeight: 400 }}>
                  Memória
                </h2>
                <div className="bg-[#2A2B2E] rounded-xl border border-[#3E3F45] p-8 text-center">
                  <div className="text-3xl text-[#ECECEC] mb-2" style={{ fontWeight: 400 }}>
                    2.4 GB
                  </div>
                  <p className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
                    Memória em uso
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <div className="px-5 py-4 flex items-center justify-between">
      <div className="flex-1">
        <div className="text-sm text-[#ECECEC] mb-1" style={{ fontWeight: 400 }}>
          {label}
        </div>
        <div className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
          {description}
        </div>
      </div>
      <button
        onClick={onChange}
        className={`w-11 h-6 rounded-full transition-all relative ${
          checked ? "bg-[#20808D]" : "bg-[#3E3F45]"
        }`}
      >
        <motion.div
          animate={{ x: checked ? 22 : 2 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className="w-4 h-4 bg-white rounded-full absolute top-1"
        />
      </button>
    </div>
  );
}
