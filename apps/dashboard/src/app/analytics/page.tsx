"use client";

import SavingsChart from "@/components/charts/SavingsChart";

export default function AnalyticsPage() {
  return (
    <div className="max-w-6xl mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Executive Analytics</h1>
        <p className="text-[var(--color-secondary)] mt-2">Comparison of AI autonomous control vs deterministic baseline.</p>
      </div>

      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="glass-panel p-6 border-l-4 border-[var(--color-success)]">
          <div className="text-sm font-semibold text-[var(--color-secondary)] uppercase mb-2">Net Energy Savings</div>
          <div className="text-4xl font-bold text-[var(--color-success)]">48.5%</div>
          <div className="text-sm text-[var(--color-secondary)] mt-2">Compared to baseline 2,000 kWh</div>
        </div>
        <div className="glass-panel p-6 border-l-4 border-[var(--color-primary)]">
          <div className="text-sm font-semibold text-[var(--color-secondary)] uppercase mb-2">Comfort Debt Delta</div>
          <div className="text-4xl font-bold text-[var(--color-primary)]">+0.12 °C-hr</div>
          <div className="text-sm text-[var(--color-secondary)] mt-2">Negligible comfort impact</div>
        </div>
        <div className="glass-panel p-6 border-l-4 border-[var(--color-accent)]">
          <div className="text-sm font-semibold text-[var(--color-secondary)] uppercase mb-2">Carbon Avoided</div>
          <div className="text-4xl font-bold text-[var(--color-accent)]">1.2 Tons</div>
          <div className="text-sm text-[var(--color-secondary)] mt-2">Using carbon-aware pre-cooling</div>
        </div>
      </div>

      <div className="glass-panel p-6">
        <h3 className="font-bold mb-6 text-lg">HVAC Energy Load Profile (24h)</h3>
        <SavingsChart />
        <div className="mt-4 text-sm text-[var(--color-secondary)] p-4 bg-black/30 rounded">
          <strong>Observation:</strong> The AI pre-cools the building at 08:00 (using slightly more energy than baseline) to allow the HVAC systems to coast during the peak heat/carbon hours at 12:00 and 16:00, resulting in massive net savings.
        </div>
      </div>
    </div>
  );
}
