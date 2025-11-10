import { useEffect, useState } from "react";
import { Network, Search, Filter, Plus, GitBranch, Database, Brain, Code, FileText, Link as LinkIcon } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

type NodeType = "concept" | "entity" | "code" | "decision" | "pattern";

interface Node {
  id: string;
  label: string;
  type: NodeType;
  relevance: number;
  connections: number;
  dateAdded: string;
  description: string;
  metadata?: any;
}

interface Connection {
  from: string;
  to: string;
  strength: number;
  type: string;
}

interface GraphNodeVis {
  id: string;
  label: string;
  type: NodeType;
  val: number;
}

interface GraphLinkVis {
  source: string;
  target: string;
  label: string;
}

export function MemoryPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<NodeType | "all">("all");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"graph" | "list">("graph");

  const [nodes, setNodes] = useState<Node[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [graphData, setGraphData] = useState<{
    nodes: GraphNodeVis[];
    links: GraphLinkVis[];
  }>({
    nodes: [],
    links: [],
  });

  const resolveNodeType = (rawType: string): NodeType => {
    const normalized = rawType.toLowerCase();
    if (normalized.includes("lembrete")) return "decision";
    if (normalized.includes("projeto")) return "pattern";
    if (normalized.includes("codigo") || normalized.includes("code")) return "code";
    if (normalized.includes("nota")) return "entity";
    if (normalized.includes("chat")) return "concept";
    return "concept";
  };

  useEffect(() => {
    fetch("/api/memory/graph")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        const enrichedNodes = (data.nodes || []).map((node: any) => {
          const properties = node.properties || {};
          const label = properties.content || node.label || node.id;
          const rawType = properties.type || node.label || "";
          const nodeType = resolveNodeType(String(rawType));
          return {
            id: String(node.id),
            label: String(label),
            type: nodeType,
            val: 5,
            properties,
          };
        });

        const graphLinks = (data.links || []).map((link: any) => ({
          source: String(link.source),
          target: String(link.target),
          label: link.type || "RELACIONADO_A",
        }));

        setGraphData({
          nodes: enrichedNodes.map(({ id, label, type, val }) => ({
            id,
            label,
            type,
            val,
          })),
          links: graphLinks,
        });

        const connectionCount = new Map<string, number>();
        graphLinks.forEach((link) => {
          connectionCount.set(link.source, (connectionCount.get(link.source) ?? 0) + 1);
          connectionCount.set(link.target, (connectionCount.get(link.target) ?? 0) + 1);
        });

        const detailedNodes: Node[] = enrichedNodes.map((node) => {
          const metadata = node.properties || {};
          const rawRelevance = metadata.relevance;
          const relevance =
            typeof rawRelevance === "number"
              ? Math.max(0, Math.min(rawRelevance, 1))
              : 0.5;
          const connectionsTotal = connectionCount.get(node.id) ?? 0;
          const dateAdded =
            typeof metadata.created_at === "string" && metadata.created_at
              ? metadata.created_at
              : new Date().toISOString();
          const description =
            typeof metadata.description === "string" && metadata.description
              ? metadata.description
              : metadata.content || `Memoria ${node.label}`;

          return {
            id: node.id,
            label: node.label,
            type: node.type,
            relevance,
            connections: connectionsTotal,
            dateAdded,
            description,
            metadata,
          };
        });

        setNodes(detailedNodes);
        setConnections(
          graphLinks.map((link) => ({
            from: link.source,
            to: link.target,
            strength: 1,
            type: link.label,
          }))
        );
      })
      .catch((err) => {
        console.error("Erro ao carregar grafo:", err);
        setGraphData({ nodes: [], links: [] });
        setNodes([]);
        setConnections([]);
      });
  }, []);

  const nodeTypeConfig = {
    concept: { label: "Conceito", color: "#20808D", icon: Brain },
    entity: { label: "Entidade", color: "#7B61FF", icon: Database },
    code: { label: "Código", color: "#FFD75E", icon: Code },
    decision: { label: "Decisão", color: "#00C896", icon: FileText },
    pattern: { label: "Padrão", color: "#00C6FF", icon: GitBranch },
  };

  const filteredNodes = nodes.filter(node => {
    const matchesType = filterType === "all" || node.type === filterType;
    const matchesSearch = node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         node.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const filteredNodeIds = new Set(filteredNodes.map((node) => node.id));
  const renderedGraphNodes = graphData.nodes.filter((node) => filteredNodeIds.has(node.id));
  const nodeIndexMap = new Map(renderedGraphNodes.map((node, idx) => [node.id, idx]));

  const getConnectedNodes = (nodeId: string) => {
    const connected = connections
      .filter((c) => c.from === nodeId || c.to === nodeId)
      .map((c) => (c.from === nodeId ? c.to : c.from));
    return nodes.filter(n => connected.includes(n.id));
  };

  const getNodeStats = () => {
    if (nodes.length === 0) {
      return {
        total: 0,
        totalConnections: connections.length,
        avgRelevance: "0",
        mostConnectedLabel: "Sem dados",
      };
    }

    return {
      total: nodes.length,
      totalConnections: connections.length,
      avgRelevance: (nodes.reduce((sum, n) => sum + n.relevance, 0) / nodes.length * 100).toFixed(0),
      mostConnectedLabel: nodes.reduce((max, n) => n.connections > max.connections ? n : max, nodes[0]).label,
    };
  };

  const stats = getNodeStats();

  return (
    <div className="min-h-screen bg-[#202123]">
      {/* Header */}
      <div className="border-b border-[#3E3F45] bg-[#2A2B2E]">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl text-[#ECECEC] mb-2" style={{ fontWeight: 500 }}>
                Memória Sináptica
              </h1>
              <p className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
                Banco de dados de grafo com conhecimento validado e consolidado
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setViewMode(viewMode === "graph" ? "list" : "graph")}
                className="px-4 py-2.5 bg-[#202123] border border-[#3E3F45] text-[#ECECEC] rounded-lg hover:border-[#4E4F55] transition-all text-sm"
                style={{ fontWeight: 400 }}
              >
                {viewMode === "graph" ? "Visão Lista" : "Visão Grafo"}
              </button>
              <button className="px-5 py-2.5 bg-gradient-to-r from-[#20808D] to-[#268a98] text-white rounded-lg flex items-center gap-2 hover:shadow-lg hover:shadow-[#20808D]/20 transition-all">
                <Plus className="w-4 h-4" />
                <span style={{ fontWeight: 500 }}>Novo Nó</span>
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-[#202123] border border-[#3E3F45] rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Network className="w-4 h-4 text-[#20808D]" />
                <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>Total de Nós</span>
              </div>
              <div className="text-2xl text-[#ECECEC]" style={{ fontWeight: 500 }}>{stats.total}</div>
            </div>
            <div className="bg-[#202123] border border-[#3E3F45] rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <LinkIcon className="w-4 h-4 text-[#7B61FF]" />
                <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>Conexões</span>
              </div>
              <div className="text-2xl text-[#ECECEC]" style={{ fontWeight: 500 }}>{stats.totalConnections}</div>
            </div>
            <div className="bg-[#202123] border border-[#3E3F45] rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="w-4 h-4 text-[#FFD75E]" />
                <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>Relevância Média</span>
              </div>
              <div className="text-2xl text-[#ECECEC]" style={{ fontWeight: 500 }}>{stats.avgRelevance}%</div>
            </div>
            <div className="bg-[#202123] border border-[#3E3F45] rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <GitBranch className="w-4 h-4 text-[#00C896]" />
                <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>Mais Conectado</span>
              </div>
              <div className="text-sm text-[#ECECEC] truncate" style={{ fontWeight: 500 }}>
                {stats.mostConnectedLabel}
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8E8E93]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar conhecimento..."
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
              {Object.entries(nodeTypeConfig).map(([type, config]) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type as NodeType)}
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

      {/* Content */}
      <div className="p-8">
        {viewMode === "graph" ? (
          // Graph View - Simplified representation
          <div className="bg-[#2A2B2E] border border-[#3E3F45] rounded-xl p-8 min-h-[600px] relative overflow-hidden">
            <div className="absolute inset-0 flex items-center justify-center">
              <svg className="w-full h-full">
                {/* Draw connections */}
                {graphData.links.map((link, idx) => {
                  const fromIndex = nodeIndexMap.get(link.source);
                  const toIndex = nodeIndexMap.get(link.target);
                  if (fromIndex === undefined || toIndex === undefined) {
                    return null;
                  }

                  const fromNode = nodes.find((n) => n.id === link.source);
                  const toNode = nodes.find((n) => n.id === link.target);
                  if (!fromNode || !toNode) {
                    return null;
                  }

                  const fromX = 150 + (fromIndex * 180) % 900;
                  const fromY = 150 + Math.floor(fromIndex / 5) * 180;
                  const toX = 150 + (toIndex * 180) % 900;
                  const toY = 150 + Math.floor(toIndex / 5) * 180;

                  const strengthMatch = connections.find(
                    (conn) =>
                      (conn.from === link.source && conn.to === link.target) ||
                      (conn.from === link.target && conn.to === link.source)
                  );
                  const strokeWidth = (strengthMatch?.strength ?? 1) * 3;

                  return (
                    <line
                      key={idx}
                      x1={fromX}
                      y1={fromY}
                      x2={toX}
                      y2={toY}
                      stroke="#3E3F45"
                      strokeWidth={strokeWidth}
                      opacity={0.6}
                    />
                  );
                })}
              </svg>
            </div>

            {/* Draw nodes */}
            <div className="relative">
              {renderedGraphNodes.map((graphNode, idx) => {
                const detail = nodes.find((n) => n.id === graphNode.id);
                if (!detail) {
                  return null;
                }
                const NodeIcon = nodeTypeConfig[detail.type].icon;
                const x = 150 + (idx * 180) % 900;
                const y = 150 + (Math.floor(idx / 5) * 180);
                
                return (
                  <motion.div
                    key={graphNode.id}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.05 }}
                    whileHover={{ scale: 1.1 }}
                    onClick={() => setSelectedNode(graphNode.id === selectedNode ? null : graphNode.id)}
                    className="absolute cursor-pointer group"
                    style={{ left: x, top: y }}
                  >
                    <div
                      className={`w-20 h-20 rounded-xl flex flex-col items-center justify-center transition-all ${
                        selectedNode === graphNode.id
                          ? "ring-2 shadow-lg"
                          : "hover:ring-2 hover:ring-opacity-50"
                      }`}
                      style={{
                        backgroundColor: nodeTypeConfig[detail.type].color + '20',
                        borderColor: nodeTypeConfig[detail.type].color,
                        ringColor: nodeTypeConfig[detail.type].color,
                      }}
                    >
                      <NodeIcon
                        className="w-8 h-8 mb-1"
                        style={{ color: nodeTypeConfig[detail.type].color }}
                        strokeWidth={1.5}
                      />
                      <span className="text-xs text-[#ECECEC] text-center px-1 truncate w-full" style={{ fontWeight: 400 }}>
                        {detail.label}
                      </span>
                    </div>
                    
                    {/* Connection count badge */}
                    <div
                      className="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs text-white"
                      style={{ backgroundColor: nodeTypeConfig[detail.type].color, fontWeight: 500 }}
                    >
                      {detail.connections}
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-[#202123] border border-[#3E3F45] rounded-lg p-4">
              <div className="text-xs text-[#8E8E93] mb-2" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                LEGENDA
              </div>
              <div className="space-y-1">
                {Object.entries(nodeTypeConfig).map(([type, config]) => {
                  const Icon = config.icon;
                  return (
                    <div key={type} className="flex items-center gap-2">
                      <Icon className="w-3 h-3" style={{ color: config.color }} strokeWidth={1.5} />
                      <span className="text-xs text-[#ECECEC]" style={{ fontWeight: 400 }}>
                        {config.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          // List View
          <div className="grid grid-cols-2 gap-6">
            <AnimatePresence>
              {filteredNodes.map((node, idx) => {
                const NodeIcon = nodeTypeConfig[node.type].icon;
                const isSelected = selectedNode === node.id;
                const connectedNodes = getConnectedNodes(node.id);
                
                return (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: idx * 0.05 }}
                    whileHover={{ y: -4 }}
                    onClick={() => setSelectedNode(node.id === selectedNode ? null : node.id)}
                    className={`bg-[#2A2B2E] border rounded-xl p-6 transition-all cursor-pointer ${
                      isSelected
                        ? "border-[#20808D] shadow-lg shadow-[#20808D]/10"
                        : "border-[#3E3F45] hover:border-[#4E4F55]"
                    }`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-12 h-12 rounded-lg flex items-center justify-center relative"
                          style={{ backgroundColor: nodeTypeConfig[node.type].color + '20' }}
                        >
                          <NodeIcon
                            className="w-6 h-6"
                            style={{ color: nodeTypeConfig[node.type].color }}
                            strokeWidth={1.5}
                          />
                          <div
                            className="absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-xs text-white"
                            style={{ backgroundColor: nodeTypeConfig[node.type].color, fontWeight: 600 }}
                          >
                            {node.connections}
                          </div>
                        </div>
                        <div>
                          <h3 className="text-[#ECECEC] mb-1" style={{ fontWeight: 500 }}>
                            {node.label}
                          </h3>
                          <span
                            className="text-xs px-2 py-0.5 rounded"
                            style={{
                              backgroundColor: nodeTypeConfig[node.type].color + '20',
                              color: nodeTypeConfig[node.type].color,
                              fontWeight: 400
                            }}
                          >
                            {nodeTypeConfig[node.type].label}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-[#ECECEC] mb-1" style={{ fontWeight: 500 }}>
                          {(node.relevance * 100).toFixed(0)}%
                        </div>
                        <div className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
                          Relevância
                        </div>
                      </div>
                    </div>

                    <p className="text-sm text-[#8E8E93] mb-4" style={{ fontWeight: 400 }}>
                      {node.description}
                    </p>

                    {isSelected && connectedNodes.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        className="pt-4 border-t border-[#3E3F45]"
                      >
                        <div className="text-xs text-[#8E8E93] mb-2" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
                          CONEXÕES ({connectedNodes.length})
                        </div>
                        <div className="space-y-2">
                          {connectedNodes.slice(0, 3).map(connectedNode => {
                            const ConnIcon = nodeTypeConfig[connectedNode.type].icon;
                            return (
                              <div
                                key={connectedNode.id}
                                className="flex items-center gap-2 p-2 bg-[#202123] border border-[#3E3F45] rounded-lg"
                              >
                                <ConnIcon
                                  className="w-4 h-4"
                                  style={{ color: nodeTypeConfig[connectedNode.type].color }}
                                  strokeWidth={1.5}
                                />
                                <span className="text-xs text-[#ECECEC] flex-1" style={{ fontWeight: 400 }}>
                                  {connectedNode.label}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </motion.div>
                    )}

                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-[#3E3F45]">
                      <span className="text-xs text-[#8E8E93]" style={{ fontWeight: 400 }}>
                        Adicionado em {new Date(node.dateAdded).toLocaleDateString('pt-BR')}
                      </span>
                      <button className="text-xs text-[#20808D] hover:underline" style={{ fontWeight: 400 }}>
                        Ver detalhes
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}

        {filteredNodes.length === 0 && (
          <div className="text-center py-16">
            <Network className="w-16 h-16 text-[#3E3F45] mx-auto mb-4" />
            <p className="text-[#8E8E93] text-lg mb-2" style={{ fontWeight: 400 }}>
              Nenhum nó encontrado
            </p>
            <p className="text-[#8E8E93] text-sm" style={{ fontWeight: 400 }}>
              Tente ajustar seus filtros de busca
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
