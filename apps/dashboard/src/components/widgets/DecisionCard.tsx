import { CheckCircle, AlertOctagon, Info } from "lucide-react";

export default function DecisionCard({ decision }: { decision: any }) {
  const isSafe = decision.safety_verdict === "SAFE";
  const isRejected = decision.safety_verdict === "REJECTED";

  return (
    <div className="glass-panel p-6 mb-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-bold text-lg text-[var(--color-primary)]">
          {decision.action_type} <span className="text-[var(--color-secondary)] text-sm ml-2">[{new Date(decision.timestamp).toLocaleTimeString()}]</span>
        </h3>
        <div className={`px-3 py-1 rounded flex items-center gap-2 text-xs font-bold ${
          isSafe ? "bg-[var(--color-success)]/20 text-[var(--color-success)]" :
          isRejected ? "bg-[var(--color-heating)]/20 text-[var(--color-heating)]" :
          "bg-[var(--color-safety)]/20 text-[var(--color-safety)]"
        }`}>
          {isSafe ? <CheckCircle size={14} /> : isRejected ? <AlertOctagon size={14} /> : <Info size={14} />}
          {decision.safety_verdict}
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-xs text-[var(--color-secondary)] uppercase mb-1">AI Proposal</div>
          <div className="font-mono text-sm text-[var(--color-accent)] p-2 bg-black/50 rounded">
            {JSON.stringify(decision.proposal, null, 2)}
          </div>
        </div>
        <div>
          <div className="text-xs text-[var(--color-secondary)] uppercase mb-1">Safety Kernel Result</div>
          <div className="font-mono text-sm text-[var(--color-primary)] p-2 bg-black/50 rounded">
            {JSON.stringify(decision.actuation, null, 2)}
          </div>
        </div>
      </div>
    </div>
  );
}
