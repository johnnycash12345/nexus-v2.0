import { useState } from "react";
import { Clock, Filter, CheckCircle, XCircle, AlertTriangle, Code, Brain, FileText, Search } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

type LogType = "decision" | "error" | "milestone" | "code" | "research" | "validation";

interface TimelineLog {
  id: number;
  timestamp: string;
  type: LogType;
  title: string;
  description: string;
  project?: string;
  agent?: string;
  metadata?: any;
}

export function TimelinePage() {
  const [filterType, setFilterType] = useState<LogType | "all">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLog, setSelectedLog] = useState<number | null>(null);

  const [logs] = useState<TimelineLog[]>([
    {
      id: 1,
      timestamp: "2024-01-28T14:32:45",
      type: "milestone",
      title: "Sistema de Recomendação ML - 65% Concluído",
      description: "Framework de treinamento implementado com sucesso. Próximo: otimização de hiperparâmetros",
      project: "Sistema de Recomendação ML",
      agent: "IA2 - Reasoner",
    },
    {
      id: 2,
      timestamp: "2024-01-28T13:15:22",
      type: "decision",
      title: "Arquitetura de Microserviços Aprovada",
      description: "Decisão tomada após análise de viabilidade: usar arquitetura de microserviços com Docker e Kubernetes",
      project: "API de Processamento NLP",
      agent: "IA3 - Validator",
      metadata: { confidence: 0.94, alternatives: 3 },
    },
    {
      id: 3,
      timestamp: "2024-01-28T12:08:17",
      type: "error",
      title: "Falha na Conexão com Banco de Dados",
      description: "Timeout ao conectar com PostgreSQL. Retry automático bem-sucedido após 3 tentativas",
      project: "Dashboard de Análise",
      agent: "IA1 - Extractor",
    },
    {
      id: 4,
      timestamp: "2024-01-28T10:42:33",
      type: "code",
      title: "Refatoração de Módulo de Autenticação",
      description: "Código otimizado seguindo padrões SOLID. Redução de 40% na complexidade ciclomática",
      project: "Sistema de Recomendação ML",
      agent: "Agente de Código",
      metadata: { linesChanged: 247, filesModified: 8 },
    },
    {
      id: 5,
      timestamp: "2024-01-28T09:25:11",
      type: "research",
      title: "Pesquisa Profunda Concluída",
      description: "Análise de 47 fontes sobre blockchain em supply chain. Relatório de viabilidade gerado",
      project: "Blockchain para Supply Chain",
      agent: "IA1 - Extractor",
      metadata: { sources: 47, confidence: 0.89 },
    },
    {
      id: 6,
      timestamp: "2024-01-28T08:15:44",
      type: "validation",
      title: "Conhecimento Validado e Adicionado à Memória",
      description: "Conceito 'Padrões de Design Observer' consolidado no Graph DB com 12 conexões",
      agent: "IA3 - Validator",
      metadata: { connections: 12, relevance: 0.92 },
    },
    {
      id: 7,
      timestamp: "2024-01-27T18:45:29",
      type: "milestone",
      title: "Deploy em Produção Realizado",
      description: "Otimização de Infraestrutura Cloud deployada com sucesso. Redução de 35% nos custos",
      project: "Otimização de Infraestrutura Cloud",
      agent: "IA2 - Reasoner",
      metadata: { costReduction: 35, uptime: 99.9 },
    },
    {
      id: 8,
      timestamp: "2024-01-27T16:22:15",
      type: "decision",
      title: "Framework TensorFlow Selecionado",
      description: "Após comparação com PyTorch, TensorFlow foi escolhido por melhor integração com produção",
      project: "Sistema de Recomendação ML",
      agent: "IA2 - Reasoner",
    },
  ]);

  const logTypeConfig = {
    decision: { label: "Decisão", color: "#20808D", icon: CheckCircle },
    error: { label: "Erro", color: "#FF6B6B", icon: XCircle },
    milestone: { label: "Marco", color: "#00C896", icon: CheckCircle },
    code: { label: "Código", color: "#FFD75E", icon: Code },
    research: { label: "Pesquisa", color: "#7B61FF", icon: Brain },
    validation: { label: "Validação", color: "#00C6FF", icon: FileText },
  };

  const filteredLogs = logs.filter(log => {
    const matchesType = filterType === "all" || log.type === filterType;
    const matchesSearch = log.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         log.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const date = new Date(timestamp);
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return "Agora há pouco";
    if (diffInHours < 24) return `Há ${diffInHours}h`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `Há ${diffInDays}d`;
  };

  return (
    <div className="min-h-screen bg-[#202123]">
      {/* Header */}
      <div className="border-b border-[#3E3F45] bg-[#2A2B2E]">
        <div className="px-8 py-6">
          <div className="mb-6">
            <h1 className="text-2xl text-[#ECECEC] mb-2" style={{ fontWeight: 500 }}>
              Timeline & Logs
            </h1>
            <p className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
              Histórico completo de decisões, marcos e atividades do sistema
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-6 gap-4 mb-6">
            {Object.entries(logTypeConfig).map(([type, config]) => {
              const count = logs.filter(l => l.type === type).length;
              const Icon = config.icon;
              return (
                <div key={type} className="bg-[#202123] border border-[#3E3F45] rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className="w-4 h-4" style={{ color: config.color }} strokeWidth={1.5} />
                    <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>{config.label}</span>
                  </div>
                  <div className="text-xl text-[#ECECEC]" style={{ fontWeight: 500 }}>{count}</div>
                </div>
              );
            })}
          </div>

          {/* Filters */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8E8E93]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar nos logs..."
                className="w-full pl-10 pr-4 py-2.5 bg-[#202123] border border-[#3E3F45] rounded-lg text-[#ECECEC] placeholder-[#8E8E93] focus:outline-none focus:ring-2 focus:ring-[#20808D] focus:border-transparent text-sm"
                style={{ fontWeight: 400 }}
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setFilterType("all")}
                className={`px-4 py-2.5 rounded-lg text-sm transition-all ${
                  filterType === "all"
                    ? "bg-[#20808D] text-white"
                    : "bg-[#202123] border border-[#3E3F45] text-[#8E8E93] hover:text-[#ECECEC]"
                }`}
                style={{ fontWeight: 400 }}
              >
                Todos
              </button>
              {Object.entries(logTypeConfig).map(([type, config]) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type as LogType)}
                  className={`px-4 py-2.5 rounded-lg text-sm transition-all ${
                    filterType === type
                      ? "text-white"
                      : "bg-[#202123] border border-[#3E3F45] text-[#8E8E93] hover:text-[#ECECEC]"
                  }`}
                  style={{ 
                    backgroundColor: filterType === type ? config.color : undefined,
                    fontWeight: 400 
                  }}
                >
                  {config.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="p-8">
        <div className="max-w-5xl mx-auto">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-px bg-[#3E3F45]" />

            <AnimatePresence>
              {filteredLogs.map((log, index) => {
                const LogIcon = logTypeConfig[log.type].icon;
                const isSelected = selectedLog === log.id;

                return (
                  <motion.div
                    key={log.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.05 }}
                    className="relative mb-6 ml-14"
                  >
                    {/* Timeline dot */}
                    <div
                      className="absolute left-[-44px] top-6 w-5 h-5 rounded-full border-2 flex items-center justify-center"
                      style={{
                        backgroundColor: '#202123',
                        borderColor: logTypeConfig[log.type].color,
                      }}
                    >
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: logTypeConfig[log.type].color }}
                      />
                    </div>

                    <motion.div
                      whileHover={{ x: 4 }}
                      onClick={() => setSelectedLog(isSelected ? null : log.id)}
                      className={`bg-[#2A2B2E] border rounded-xl p-5 transition-all cursor-pointer ${
                        isSelected 
                          ? "border-[#20808D] shadow-lg shadow-[#20808D]/10" 
                          : "border-[#3E3F45] hover:border-[#4E4F55]"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center"
                            style={{ backgroundColor: logTypeConfig[log.type].color + '20' }}
                          >
                            <LogIcon
                              className="w-5 h-5"
                              style={{ color: logTypeConfig[log.type].color }}
                              strokeWidth={1.5}
                            />
                          </div>
                          <div>
                            <h3 className="text-[#ECECEC] mb-1" style={{ fontWeight: 500 }}>
                              {log.title}
                            </h3>
                            <div className="flex items-center gap-2">
                              <span
                                className="text-xs px-2 py-0.5 rounded"
                                style={{
                                  backgroundColor: logTypeConfig[log.type].color + '20',
                                  color: logTypeConfig[log.type].color,
                                  fontWeight: 400
                                }}
                              >
                                {logTypeConfig[log.type].label}
                              </span>
                              {log.agent && (
                                <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
                                  {log.agent}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-[#8E8E93] mb-1" style={{ fontWeight: 400 }}>
                            {getTimeAgo(log.timestamp)}
                          </div>
                          <div className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
                            {formatTime(log.timestamp)}
                          </div>
                        </div>
                      </div>

                      <p className="text-sm text-[#ECECEC] mb-3" style={{ fontWeight: 400 }}>
                        {log.description}
                      </p>

                      {log.project && (
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
                            Projeto:
                          </span>
                          <span className="text-xs text-[#20808D] px-2 py-1 bg-[#20808D]/10 rounded" style={{ fontWeight: 400 }}>
                            {log.project}
                          </span>
                        </div>
                      )}

                      {isSelected && log.metadata && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          className="pt-3 border-t border-[#3E3F45] mt-3"
                        >
                          <div className="text-xs text-[#8E8E93] mb-2" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                            METADADOS
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            {Object.entries(log.metadata).map(([key, value]) => (
                              <div key={key} className="bg-[#202123] border border-[#3E3F45] rounded-lg p-3">
                                <div className="text-xs text-[#8E8E93] mb-1" style={{ fontWeight: 400 }}>
                                  {key}
                                </div>
                                <div className="text-sm text-[#ECECEC]" style={{ fontWeight: 500 }}>
                                  {typeof value === 'number' && value < 1 ? `${(value * 100).toFixed(0)}%` : value}
                                </div>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </motion.div>
                  </motion.div>
                );
              })}
            </AnimatePresence>

            {filteredLogs.length === 0 && (
              <div className="text-center py-16">
                <Clock className="w-16 h-16 text-[#3E3F45] mx-auto mb-4" />
                <p className="text-[#8E8E93] text-lg mb-2" style={{ fontWeight: 400 }}>
                  Nenhum log encontrado
                </p>
                <p className="text-[#8E8E93] text-sm" style={{ fontWeight: 400 }}>
                  Tente ajustar seus filtros de busca
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
