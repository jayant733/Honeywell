"use client";

import { useTelemetryStream } from "@/hooks/useTelemetryStream";
import { useStore } from "@/lib/store";
import OperatorAssistant from "@/components/widgets/OperatorAssistant";

export default function Dashboard() {
  useTelemetryStream();
  const telemetry = useStore((state) => state.telemetry);

  return (
    <div className="grid grid-cols-12 gap-4">
      {/* KPI Row */}
      <div className="col-span-12 grid grid-cols-4 gap-4">
        <MetricCard title="Total Power" value={`${telemetry?.hvac_power ?? 0} kW`} color="var(--color-energy)" />
        <MetricCard title="Comfort Debt" value="1.2 °C-hr" color="var(--color-heating)" />
        <MetricCard title="Carbon Intensity" value="340 g/kWh" color="var(--color-secondary)" />
        <MetricCard title="AI Status" value="ACTIVE" color="var(--color-accent)" />
      </div>

      {/* Main Chart Area */}
      <div className="col-span-8 glass-panel p-6 h-96 flex items-center justify-center">
        <span className="text-[var(--color-secondary)]">Live Telemetry Chart (Recharts)</span>
      </div>

      {/* Safety Feed */}
      <div className="col-span-4 glass-panel p-6 h-96 overflow-y-auto">
        <h3 className="font-semibold mb-4 text-sm text-[var(--color-secondary)] uppercase">Safety Feed</h3>
        <div className="text-xs font-mono space-y-2 text-[var(--color-secondary)]">
          <p>[14:02] <span className="text-[var(--color-accent)]">AI Proposed</span> Setpoint: 20.0</p>
          <p>[14:02] <span className="text-[var(--color-success)]">Kernel Verified</span> Setpoint: 20.0</p>
        </div>
      </div>
      
      <OperatorAssistant />
    </div>
  );
}

function MetricCard({ title, value, color }: { title: string, value: string, color: string }) {
  return (
    <div className="glass-panel p-6 flex flex-col justify-center">
      <div className="text-xs uppercase font-semibold text-[var(--color-secondary)] mb-1">{title}</div>
      <div className="text-2xl font-bold tracking-tight" style={{ color }}>{value}</div>
    </div>
  );
}
