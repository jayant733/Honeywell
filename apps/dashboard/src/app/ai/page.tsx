"use client";

import DecisionCard from "@/components/widgets/DecisionCard";
import { useEffect, useState } from "react";

export default function AiControlCenter() {
  const [decisions, setDecisions] = useState([]);

  useEffect(() => {
    // Fetch mock decisions initially, to be wired to /api/decisions
    const mockDecisions = [
      {
        id: "evt_1001",
        timestamp: new Date().toISOString(),
        action_type: "HVAC_SETPOINT_UPDATE",
        safety_verdict: "CLIPPED",
        proposal: { zone: "Z1", setpoint: 16.0, mode: "COOLING" },
        actuation: { zone: "Z1", setpoint: 18.0, mode: "COOLING", reason: "Min cooling setpoint is 18C" }
      },
      {
        id: "evt_1002",
        timestamp: new Date(Date.now() - 300000).toISOString(),
        action_type: "HVAC_SETPOINT_UPDATE",
        safety_verdict: "SAFE",
        proposal: { zone: "Z2", setpoint: 22.0, mode: "COOLING" },
        actuation: { zone: "Z2", setpoint: 22.0, mode: "COOLING" }
      }
    ];
    setDecisions(mockDecisions as any);
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Control Center</h1>
          <p className="text-[var(--color-secondary)] mt-2">Transparent audit log of Qwen 14B proposals vs Safety Kernel validation.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full text-sm font-mono">
          <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse"></span>
          QWEN_14B_ACTIVE
        </div>
      </div>

      <div className="space-y-4">
        {decisions.map((dec: any) => (
          <DecisionCard key={dec.id} decision={dec} />
        ))}
      </div>
    </div>
  );
}
