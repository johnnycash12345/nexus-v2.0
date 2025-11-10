import React from "react";

type EvolutionAuthDialogProps = {
  open: boolean;
  explanation: string;
  onAuthorize: () => void;
  onDeny: () => void;
};

/**
 * Modal de autorização para evoluções críticas.
 * Exibe uma camada sobre toda a aplicação com opções de Autorizar ou Negar.
 */
export function EvolutionAuthDialog({
  open,
  explanation,
  onAuthorize,
  onDeny,
}: EvolutionAuthDialogProps) {
  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="evolution-auth-title"
      aria-describedby="evolution-auth-description"
    >
      <div className="w-full max-w-lg rounded-xl border border-red-400 bg-zinc-900 p-6 shadow-2xl">
        <header className="mb-4">
          <h2
            id="evolution-auth-title"
            className="text-xl font-bold text-red-400"
          >
            ⚠️ SOLICITAÇÃO DE AUTO-EVOLUÇÃO
          </h2>
        </header>

        <section className="mb-6">
          <p
            id="evolution-auth-description"
            className="whitespace-pre-wrap text-sm text-zinc-200"
          >
            {explanation}
          </p>
        </section>

        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            className="flex-1 rounded-lg bg-green-500 px-4 py-2 text-sm font-semibold text-black transition hover:bg-green-400 focus:outline-none focus:ring-2 focus:ring-green-300"
            onClick={onAuthorize}
          >
            AUTORIZAR (Senão, não faça nada)
          </button>
          <button
            type="button"
            className="flex-1 rounded-lg border border-red-400 px-4 py-2 text-sm font-semibold text-red-300 transition hover:bg-red-500/10 focus:outline-none focus:ring-2 focus:ring-red-400"
            onClick={onDeny}
          >
            NEGAR
          </button>
        </div>
      </div>
    </div>
  );
}

export default EvolutionAuthDialog;
