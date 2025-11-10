import { useState } from "react";
import { Play, Sparkles, Terminal, Code2, RefreshCw, Upload, FolderTree, FileCode, Settings, Rocket, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

interface FileItem {
  name: string;
  type: "file" | "folder";
  content?: string;
  children?: FileItem[];
}

export function CodePage() {
  const [activeMode, setActiveMode] = useState<"manual" | "autonomous">("manual");
  const [selectedFile, setSelectedFile] = useState("src/main.tsx");
  const [code, setCode] = useState(`// Sistema de Recomendação ML
import tensorflow as tf
import numpy as np
from typing import List, Dict

class RecommendationEngine:
    def __init__(self, embedding_dim: int = 128):
        self.model = self._build_model(embedding_dim)
        self.embedding_dim = embedding_dim
    
    def _build_model(self, dim: int) -> tf.keras.Model:
        """Constrói o modelo de recomendação"""
        user_input = tf.keras.Input(shape=(1,), name='user_id')
        item_input = tf.keras.Input(shape=(1,), name='item_id')
        
        user_embedding = tf.keras.layers.Embedding(
            input_dim=10000,
            output_dim=dim,
            name='user_embedding'
        )(user_input)
        
        item_embedding = tf.keras.layers.Embedding(
            input_dim=5000,
            output_dim=dim,
            name='item_embedding'
        )(item_input)
        
        dot_product = tf.keras.layers.Dot(
            axes=2,
            name='dot_product'
        )([user_embedding, item_embedding])
        
        output = tf.keras.layers.Flatten()(dot_product)
        
        model = tf.keras.Model(
            inputs=[user_input, item_input],
            outputs=output
        )
        
        return model
    
    def train(self, user_ids: np.ndarray, item_ids: np.ndarray, 
              ratings: np.ndarray, epochs: int = 10):
        """Treina o modelo de recomendação"""
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return self.model.fit(
            [user_ids, item_ids],
            ratings,
            epochs=epochs,
            batch_size=32,
            validation_split=0.2,
            verbose=1
        )
    
    def recommend(self, user_id: int, n_items: int = 10) -> List[int]:
        """Gera recomendações para um usuário"""
        # Implementação de recomendação
        all_items = np.arange(5000)
        user_ids = np.full(len(all_items), user_id)
        
        predictions = self.model.predict([user_ids, all_items])
        top_items = np.argsort(predictions.flatten())[-n_items:][::-1]
        
        return top_items.tolist()

# Exemplo de uso
if __name__ == "__main__":
    engine = RecommendationEngine()
    print("Modelo inicializado com sucesso!")
`);

  const [logs, setLogs] = useState([
    { time: "14:32:01", type: "info", message: "Environment ready" },
    { time: "14:32:02", type: "success", message: "Dependencies installed: tensorflow, numpy" },
    { time: "14:32:03", type: "info", message: "Python 3.11.0 detected" },
  ]);

  const [isRunning, setIsRunning] = useState(false);
  const [isRefactoring, setIsRefactoring] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const fileTree: FileItem[] = [
    {
      name: "src",
      type: "folder",
      children: [
        { name: "main.tsx", type: "file" },
        { name: "engine.py", type: "file" },
        { name: "utils.ts", type: "file" },
      ],
    },
    {
      name: "tests",
      type: "folder",
      children: [
        { name: "test_engine.py", type: "file" },
      ],
    },
    { name: "package.json", type: "file" },
    { name: "requirements.txt", type: "file" },
  ];

  const handleRun = () => {
    setIsRunning(true);
    setLogs([...logs, {
      time: new Date().toLocaleTimeString(),
      type: "info",
      message: "Executing code..."
    }]);

    setTimeout(() => {
      setLogs(prev => [...prev, {
        time: new Date().toLocaleTimeString(),
        type: "success",
        message: "✓ Modelo inicializado com sucesso!"
      }, {
        time: new Date().toLocaleTimeString(),
        type: "info",
        message: "Memory usage: 247 MB"
      }]);
      setIsRunning(false);
    }, 2000);
  };

  const handleDeploy = () => {
    setIsDeploying(true);
    setLogs([...logs, {
      time: new Date().toLocaleTimeString(),
      type: "info",
      message: "🚀 Iniciando deploy..."
    }]);

    setTimeout(() => {
      setLogs(prev => [...prev, {
        time: new Date().toLocaleTimeString(),
        type: "info",
        message: "Building Docker image..."
      }, {
        time: new Date().toLocaleTimeString(),
        type: "info",
        message: "Pushing to registry..."
      }, {
        time: new Date().toLocaleTimeString(),
        type: "success",
        message: "✓ Deploy concluído com sucesso!"
      }, {
        time: new Date().toLocaleTimeString(),
        type: "info",
        message: "URL: https://nexus-ml-engine.app"
      }]);
      setIsDeploying(false);
    }, 4000);
  };

  const handleGenerateCode = async () => {
    if (isGenerating) {
      return;
    }

    setLogs((prev) => [
      ...prev,
      {
        time: new Date().toLocaleTimeString(),
        type: "info",
        message: "Solicitando geracao de codigo ao agente...",
      },
    ]);

    setIsGenerating(true);

    try {
      const response = await fetch("/api/code/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: "Gere um Hello World em Python" }),
      });

      if (!response.ok) {
        throw new Error("Falha ao gerar codigo.");
      }

      const data: { code: string } = await response.json();
      setCode(data.code);
      setLogs((prev) => [
        ...prev,
        {
          time: new Date().toLocaleTimeString(),
          type: "success",
          message: "Codigo gerado pelo agente com sucesso.",
        },
      ]);
    } catch (error) {
      console.error(error);
      setLogs((prev) => [
        ...prev,
        {
          time: new Date().toLocaleTimeString(),
          type: "error",
          message: "Erro ao solicitar geracao de codigo.",
        },
      ]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRefactorCode = async () => {
    if (isRefactoring) {
      return;
    }

    setLogs((prev) => [
      ...prev,
      {
        time: new Date().toLocaleTimeString(),
        type: "info",
        message: "Enviando codigo para refatoracao...",
      },
    ]);

    setIsRefactoring(true);

    try {
      const response = await fetch("/api/code/refactor", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        throw new Error("Falha ao refatorar o codigo.");
      }

      const data: { code: string } = await response.json();
      setCode(data.code);
      setLogs((prev) => [
        ...prev,
        {
          time: new Date().toLocaleTimeString(),
          type: "success",
          message: "Refatoracao aplicada pelo agente.",
        },
      ]);
    } catch (error) {
      console.error(error);
      setLogs((prev) => [
        ...prev,
        {
          time: new Date().toLocaleTimeString(),
          type: "error",
          message: "Erro ao solicitar refatoracao.",
        },
      ]);
    } finally {
      setIsRefactoring(false);
    }
  };

  const renderFileTree = (items: FileItem[], depth = 0) => {
    return items.map((item, idx) => (
      <div key={idx}>
        <button
          onClick={() => item.type === "file" && setSelectedFile(item.name)}
          className={`w-full px-3 py-1.5 rounded text-left text-sm transition-colors flex items-center gap-2 ${
            selectedFile === item.name
              ? "bg-[#20808D]/20 text-[#20808D]"
              : "text-[#ECECEC] hover:bg-[#3E3F45]"
          }`}
          style={{ paddingLeft: `${depth * 16 + 12}px`, fontWeight: 400 }}
        >
          {item.type === "folder" ? (
            <FolderTree className="w-4 h-4 text-[#FFD75E]" />
          ) : (
            <FileCode className="w-4 h-4 text-[#20808D]" />
          )}
          {item.name}
        </button>
        {item.children && renderFileTree(item.children, depth + 1)}
      </div>
    ));
  };

  return (
    <div className="h-screen flex flex-col bg-[#202123]">
      {/* Header */}
      <div className="border-b border-[#3E3F45] bg-[#2A2B2E] px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl text-[#ECECEC] mb-1" style={{ fontWeight: 500 }}>
              Desenvolvimento
            </h1>
            <p className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>
              Geração, refatoração e deploy de código com IA
            </p>
          </div>

          <div className="flex gap-3">
            <div className="flex gap-2 bg-[#202123] border border-[#3E3F45] rounded-lg p-1">
              <button
                onClick={() => setActiveMode("manual")}
                className={`px-4 py-1.5 rounded text-sm transition-all ${
                  activeMode === "manual"
                    ? "bg-[#20808D] text-white shadow-sm"
                    : "text-[#8E8E93] hover:text-[#ECECEC]"
                }`}
                style={{ fontWeight: 400 }}
              >
                Manual
              </button>
              <button
                onClick={() => setActiveMode("autonomous")}
                className={`px-4 py-1.5 rounded text-sm transition-all ${
                  activeMode === "autonomous"
                    ? "bg-[#20808D] text-white shadow-sm"
                    : "text-[#8E8E93] hover:text-[#ECECEC]"
                }`}
                style={{ fontWeight: 400 }}
              >
                <Sparkles className="w-3 h-3 inline mr-1" />
                Autônomo
              </button>
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleRun}
                disabled={isRunning}
                className="px-4 py-2 bg-[#20808D] hover:bg-[#268a98] text-white rounded-lg text-sm transition-all flex items-center gap-2 disabled:opacity-50"
                style={{ fontWeight: 400 }}
              >
                <Play className="w-4 h-4" />
                {isRunning ? "Executando..." : "Executar"}
              </button>

              <button
                onClick={handleRefactorCode}
                disabled={isRefactoring}
                className="px-4 py-2 bg-[#7B61FF] hover:bg-[#8B71FF] text-white rounded-lg text-sm transition-all flex items-center gap-2 disabled:cursor-not-allowed disabled:opacity-50"
                style={{ fontWeight: 400 }}
              >
                {isRefactoring ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
                {isRefactoring ? "Refatorando..." : "Refatorar"}
              </button>

              <button
                onClick={handleGenerateCode}
                disabled={isGenerating}
                className="px-4 py-2 bg-[#2A2B2E] hover:bg-[#3A3B3E] border border-[#3E3F45] text-[#ECECEC] rounded-lg text-sm transition-all flex items-center gap-2 disabled:cursor-not-allowed disabled:opacity-50"
                style={{ fontWeight: 400 }}
              >
                {isGenerating ? (
                  <Loader2 className="w-4 h-4 animate-spin text-[#FFD75E]" />
                ) : (
                  <Sparkles className="w-4 h-4 text-[#FFD75E]" />
                )}
                {isGenerating ? "Gerando..." : "Gerar"}
              </button>

              <button
                onClick={handleDeploy}
                disabled={isDeploying}
                className="px-4 py-2 bg-gradient-to-r from-[#00C896] to-[#00A876] hover:shadow-lg text-white rounded-lg text-sm transition-all flex items-center gap-2 disabled:opacity-50"
                style={{ fontWeight: 400 }}
              >
                <Rocket className="w-4 h-4" />
                {isDeploying ? "Deploying..." : "Deploy"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* File Navigator */}
        <div className="w-64 border-r border-[#3E3F45] bg-[#2A2B2E] overflow-y-auto">
          <div className="p-3 border-b border-[#3E3F45] flex items-center justify-between">
            <span className="text-sm text-[#8E8E93]" style={{ fontWeight: 500 }}>ARQUIVOS</span>
            <button className="w-7 h-7 flex items-center justify-center hover:bg-[#3E3F45] rounded transition-colors">
              <Upload className="w-4 h-4 text-[#8E8E93]" />
            </button>
          </div>
          <div className="p-2">
            {renderFileTree(fileTree)}
          </div>
        </div>

        {/* Editor */}
        <div className="flex-1 flex flex-col">
          <div className="px-6 py-3 border-b border-[#3E3F45] flex items-center justify-between bg-[#2A2B2E]">
            <div className="flex items-center gap-2 text-sm text-[#8E8E93]">
              <Code2 className="w-4 h-4" />
              <span style={{ fontWeight: 400 }}>{selectedFile}</span>
            </div>
            <button className="w-7 h-7 flex items-center justify-center hover:bg-[#3E3F45] rounded transition-colors">
              <Settings className="w-4 h-4 text-[#8E8E93]" />
            </button>
          </div>

          <div className="flex-1 p-6 overflow-auto bg-[#202123]">
            <textarea
              value={code}
              onChange={(event) => setCode(event.target.value)}
              className="w-full h-full resize-none rounded-lg border border-[#3E3F45] bg-[#1B1C1F] px-4 py-4 text-[#ECECEC] font-mono text-sm leading-relaxed focus:border-[#20808D] focus:outline-none focus:ring-2 focus:ring-[#20808D]/40"
              style={{ fontWeight: 400 }}
            />
          </div>

          {/* Status Bar */}
          <div className="px-6 py-2 border-t border-[#3E3F45] bg-[#2A2B2E] flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs text-[#8E8E93]">
              <span>Python 3.11.0</span>
              <span>UTF-8</span>
              <span>Ln 47, Col 12</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-[#00C896] rounded-full" />
              <span className="text-xs text-[#8E8E93]">Pronto</span>
            </div>
          </div>
        </div>

        {/* Console */}
        <div className="w-96 border-l border-[#3E3F45] flex flex-col bg-[#2A2B2E]">
          <div className="px-4 py-3 border-b border-[#3E3F45] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#8E8E93]" />
              <span className="text-sm text-[#8E8E93]" style={{ fontWeight: 400 }}>Console</span>
            </div>
            <button className="text-xs text-[#8E8E93] hover:text-[#ECECEC]">
              Limpar
            </button>
          </div>

          <div className="flex-1 overflow-auto p-4 space-y-1">
            <AnimatePresence>
              {logs.map((log, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex gap-3 font-mono text-xs"
                >
                  <span className="text-[#8E8E93]">{log.time}</span>
                  <span
                    className={
                      log.type === "success"
                        ? "text-[#00C896]"
                        : log.type === "error"
                        ? "text-[#FF6B6B]"
                        : "text-[#ECECEC]"
                    }
                    style={{ fontWeight: 400 }}
                  >
                    {log.message}
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Contextual Logs Section */}
          <div className="border-t border-[#3E3F45] p-4">
            <div className="text-xs text-[#8E8E93] mb-2" style={{ fontWeight: 500, letterSpacing: '0.05em' }}>
              LOGS CONTEXTUAIS
            </div>
            <div className="space-y-2">
              <div className="text-xs text-[#ECECEC] bg-[#202123] border border-[#3E3F45] rounded p-2">
                <div className="text-[#20808D] mb-1">IA2 - Reasoner</div>
                <div style={{ fontWeight: 400 }}>Analisando padrões de código...</div>
              </div>
              <div className="text-xs text-[#ECECEC] bg-[#202123] border border-[#3E3F45] rounded p-2">
                <div className="text-[#7B61FF] mb-1">IA3 - Validator</div>
                <div style={{ fontWeight: 400 }}>Validação: 98% de confiança</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
