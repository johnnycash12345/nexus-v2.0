import { useMemo, useState } from "react";
import { motion } from "motion/react";
import {
  Layers,
  Database,
  Search,
  Zap,
  Code,
  Activity,
  Gauge,
  ClipboardList,
} from "lucide-react";

type AgentStatus = "Online" | "Offline" | "Processing";

interface AgentCardData {
  id: string;
  name: string;
  description: string;
  icon: typeof Layers;
  color: string;
  status: AgentStatus;
  latency: number | null;
  throughput: string;
}

export function CognitivePage() {
  const [agents] = useState<AgentCardData[]>([
    {
      id: "orchestrator",
      name: "Agente Central (Orquestrador)",
      description: "Coordena fluxos entre todos os agentes especializados.",
      icon: Layers,
      color: "#20808D",
      status: "Online",
      latency: 28,
      throughput: "12 pipelines/min",
    },
    {
      id: "memory",
      name: "Agente de Memória (Neo4j/ChromaDB)",
      description: "Gerencia consultas e persistência no grafo cognitivo.",
      icon: Database,
      color: "#7B61FF",
      status: "Processing",
      latency: 41,
      throughput: "32 operações/min",
    },
    {
      id: "research",
      name: "Agente de Pesquisa (Web/Acadêmica)",
      description: "Executa buscas externas e consolida resultados relevantes.",
      icon: Search,
      color: "#FFD75E",
      status: "Online",
      latency: 63,
      throughput: "18 buscas/min",
    },
    {
      id: "executor",
      name: "Agente Executor (Integrações/API)",
      description: "Aciona automações em calendários, tarefas e serviços SaaS.",
      icon: Zap,
      color: "#00C896",
      status: "Offline",
      latency: null,
      throughput: "Sem atividade",
    },
    {
      id: "code",
      name: "Agente de Código (Refatoração/Geração)",
      description: "Produz e ajusta código com estratégia orientada a testes.",
      icon: Code,
      color: "#F97068",
      status: "Online",
      latency: 37,
      throughput: "9 commits virtuais/min",
    },
  ]);

  const statusColors: Record<AgentStatus, string> = useMemo(
    () => ({
      Online: "#00C896",
      Offline: "#FF6B6B",
      Processing: "#FFD75E",
    }),
    [],
  );

  const systemMetrics = useMemo(
    () => ({
      orchestratedSessions: 42,
      activePipelines: 7,
      pendingExecutions: 4,
      avgLatency: Math.round(
        agents
          .filter((agent) => typeof agent.latency === "number")
          .reduce((acc, agent) => acc + (agent.latency ?? 0), 0) /
          Math.max(agents.filter((agent) => typeof agent.latency === "number").length, 1),
      ),
    }),
    [agents],
  );

  const logs = [
    {
      time: "14:42:10",
      agent: "Agente Central",
      message: "Coordenou pipeline de triagem para Caixa de Entrada Universal.",
    },
    {
      time: "14:42:13",
      agent: "Agente de Memória",
      message: "Persistiu 6 novas relações no grafo cognitivo.",
    },
    {
      time: "14:42:18",
      agent: "Agente de Pesquisa",
      message: "Retornou 3 artigos acadêmicos relevantes para o contexto.",
    },
    {
      time: "14:42:26",
      agent: "Agente de Código",
      message: "Gerou refatoração para módulo de notificações.",
    },
  ];

  return (
    <div className="min-h-screen bg-[#202123] px-6 py-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl text-[#ECECEC]" style={{ fontWeight: 500 }}>
            Cognitive Monitor
          </h1>
          <p className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
            Status operacional dos agentes Nexus (Fases V1.0 / V2.0).
          </p>
        </div>

        {/* Agents Grid */}
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {agents.map((agent) => {
            const Icon = agent.icon;
            const statusColor = statusColors[agent.status];

            return (
              <motion.div
                key={agent.id}
                whileHover={{ y: -3 }}
                className="rounded-xl border border-[#3E3F45] bg-[#2A2B2E] p-5 shadow-sm transition-all hover:border-[#4E4F55]"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div
                    className="flex h-10 w-10 items-center justify-center rounded-lg"
                    style={{ backgroundColor: `${agent.color}20` }}
                  >
                    <Icon className="h-5 w-5" style={{ color: agent.color }} strokeWidth={1.6} />
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: statusColor }}
                    />
                    <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 500 }}>
                      {agent.status}
                    </span>
                  </div>
                </div>

                <h3 className="text-[#ECECEC]" style={{ fontWeight: 500 }}>
                  {agent.name}
                </h3>
                <p className="mb-4 text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
                  {agent.description}
                </p>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-xs text-[#8E8E93]">Latência</div>
                    <div className="text-lg text-[#ECECEC]" style={{ fontWeight: 500 }}>
                      {typeof agent.latency === "number" ? `${agent.latency}ms` : "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-[#8E8E93]">Throughput</div>
                    <div className="text-lg text-[#ECECEC]" style={{ fontWeight: 500 }}>
                      {agent.throughput}
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* System Metrics */}
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-[#3E3F45] bg-[#2A2B2E] p-5">
            <div className="mb-4 flex items-center gap-2">
              <Activity className="h-4 w-4 text-[#8E8E93]" />
              <h3 className="text-sm text-[#8E8E93]" style={{ fontWeight: 500 }}>
                Sessões Orquestradas
              </h3>
            </div>
            <div className="text-3xl text-[#ECECEC]" style={{ fontWeight: 500 }}>
              {systemMetrics.orchestratedSessions}
            </div>
            <div className="text-xs text-[#20808D]" style={{ fontWeight: 400 }}>
              +18% nas últimas 24h
            </div>
          </div>

          <div className="rounded-xl border border-[#3E3F45] bg-[#2A2B2E] p-5">
            <div className="mb-4 flex items-center gap-2">
              <Gauge className="h-4 w-4 text-[#8E8E93]" />
              <h3 className="text-sm text-[#8E8E93]" style={{ fontWeight: 500 }}>
                Latência Média
              </h3>
            </div>
            <div className="text-3xl text-[#ECECEC]" style={{ fontWeight: 500 }}>
              {systemMetrics.avgLatency}ms
            </div>
            <div className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
              Baseado em {agents.filter((agent) => typeof agent.latency === "number").length} agentes ativos
            </div>
          </div>
        </div>

        {/* Operational Overview */}
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-[#3E3F45] bg-[#2A2B2E] p-5">
            <div className="mb-4 flex items-center gap-2">
              <ClipboardList className="h-4 w-4 text-[#8E8E93]" />
              <h3 className="text-sm text-[#8E8E93]" style={{ fontWeight: 500 }}>
                Pipeline Atual
              </h3>
            </div>
            <div className="flex items-center justify-between text-sm text-[#ECECEC]">
              <span>Pipelines Ativos</span>
              <span style={{ fontWeight: 500 }}>{systemMetrics.activePipelines}</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-sm text-[#ECECEC]">
              <span>Execuções Pendentes</span>
              <span style={{ fontWeight: 500 }}>{systemMetrics.pendingExecutions}</span>
            </div>
          </div>

          {/* Logs */}
          <div className="overflow-hidden rounded-xl border border-[#3E3F45] bg-[#2A2B2E]">
            <div className="border-b border-[#3E3F45] px-5 py-4">
              <h3 className="text-sm text-[#8E8E93]" style={{ fontWeight: 500 }}>
                Logs Recentes
              </h3>
            </div>
            <div className="max-h-56 space-y-3 overflow-auto px-5 py-4">
              {logs.map((log, index) => (
                <motion.div
                  key={`${log.time}-${index}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex gap-3 font-mono text-xs"
                >
                  <span className="text-[#8E8E93]">{log.time}</span>
                  <span className="text-[#20808D]">[{log.agent}]</span>
                  <span className="text-[#ECECEC]" style={{ fontWeight: 400 }}>
                    {log.message}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
