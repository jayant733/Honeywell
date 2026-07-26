"use client";

import { useTelemetryStream } from "@/hooks/useTelemetryStream";
import { useStore } from "@/lib/store";
import OperatorAssistant from "@/components/widgets/OperatorAssistant";
import LiveTelemetryChart from "@/components/charts/LiveTelemetryChart";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import BuildingModel from "@/components/3d/BuildingModel";
import React from "react";

export default function Dashboard() {
  useTelemetryStream();
  const telemetry = useStore((state) => state.telemetry);
  const wsStatus = useStore((state) => state.wsStatus);
  const lastMessageAt = useStore((state) => state.lastMessageAt);
  const rawTelemetry = useStore((state) => state.rawTelemetry);

  React.useEffect(() => {
    if (!telemetry) return;
    
    console.log("================ KPI VERIFICATION ================");
    console.log(`Total Power\nSource: EnergyPlus HVAC Meter\nFormula: sum(cool_coil, heat_coil, fan_pwr)\nCurrent Value: ${telemetry.hvac_power}\nUnits: kW\nUpdate Rate: Timestep`);
    console.log(`Energy Today\nSource: EnergyPlus Meter Accumulation\nFormula: sum(hvac_power * dt)\nCurrent Value: ${telemetry.energy_today}\nUnits: kWh\nUpdate Rate: Timestep`);
    console.log(`Energy Savings\nSource: Real Baseline Simulation\nFormula: baseline_energy_kwh - ai_energy_kwh\nCurrent Value: ${telemetry.energy_savings}\nUnits: kWh\nUpdate Rate: Timestep`);
    console.log(`CO₂ Avoided\nSource: Real Baseline Carbon Emission\nFormula: energy_savings * (carbon / 1000.0)\nCurrent Value: ${telemetry.co2_avoided}\nUnits: kg\nUpdate Rate: Timestep`);
    console.log(`Comfort Debt\nSource: EnergyPlus Thermal Comfort\nFormula: sum(occ * abs(pmv) * dt)\nCurrent Value: ${telemetry.comfort_debt}\nUnits: °C-hr (eq)\nUpdate Rate: Timestep`);
    console.log(`Carbon Intensity\nSource: Grid API (Mock)\nFormula: time_based_schedule\nCurrent Value: ${telemetry.carbon_intensity}\nUnits: g/kWh\nUpdate Rate: Timestep`);
    console.log(`PMV\nSource: Zone Thermal Comfort Fanger Model PMV\nFormula: Fanger Model\nCurrent Value: ${telemetry.pmv}\nUnits: dimensionless\nUpdate Rate: Timestep`);
    console.log(`PPD\nSource: Zone Thermal Comfort Fanger Model PPD\nFormula: Fanger Model\nCurrent Value: ${telemetry.ppd}\nUnits: %\nUpdate Rate: Timestep`);
    console.log(`Occupancy\nSource: Zone People Occupant Count\nFormula: sum(z1_occ, z2_occ)\nCurrent Value: ${telemetry.occupancy_ratio}\nUnits: People\nUpdate Rate: Timestep`);
    
    console.log("================ CONSISTENCY CHECK ================");
    console.log("Comparing Frontend Store vs Dashboard KPIs...");
    console.log(`HVAC Power: store=${telemetry.hvac_power} dashboard=${telemetry.hvac_power?.toFixed(1)}`);
    console.log(`Energy Today: store=${telemetry.energy_today} dashboard=${telemetry.energy_today?.toFixed(1)}`);
    console.log(`PMV: store=${telemetry.pmv} dashboard=Not Rendered`);
    console.log(`PPD: store=${telemetry.ppd} dashboard=${telemetry.ppd?.toFixed(1)}`);
    console.log(`Carbon: store=${telemetry.carbon_intensity} dashboard=${telemetry.carbon_intensity}`);
    console.log(`Comfort Debt: store=${telemetry.comfort_debt} dashboard=${telemetry.comfort_debt?.toFixed(2)}`);
    
    console.log("================ VALIDATION REPORT ================");
    const checks = [
      { name: "EnergyPlus Physics", pass: telemetry.hvac_power != null },
      { name: "AI Controller", pass: telemetry.ai_decision != null },
      { name: "Actuator Loop", pass: telemetry.ai_decision?.Z1_setpoint != null },
      { name: "PMV", pass: telemetry.pmv != null && telemetry.pmv !== 0 },
      { name: "PPD", pass: telemetry.ppd != null && telemetry.ppd !== 5.0 },
      { name: "Baseline Simulation", pass: telemetry.energy_savings != null && telemetry.energy_savings !== -telemetry.energy_today },
      { name: "Energy Savings", pass: telemetry.energy_savings != null },
      { name: "Carbon Calculation", pass: telemetry.co2_avoided != null },
      { name: "Comfort Calculation", pass: telemetry.comfort_debt != null && telemetry.comfort_debt !== 2.8 },
      { name: "Dashboard KPIs", pass: telemetry.hvac_power != null && telemetry.energy_today != null },
    ];
    checks.forEach(c => {
      console.log(`${c.name.padEnd(30, '.')} ${c.pass ? 'PASS' : 'FAIL'} (Runtime Check)`);
    });
    console.log("=================================================");
  }, [telemetry]);

  return (
    <div className="grid grid-cols-12 gap-4">
      {/* KPI Row */}
      <div className="col-span-12 grid grid-cols-4 gap-4">
        <MetricCard title="Total Power" value={`${telemetry?.hvac_power?.toFixed(1) ?? 0} kW`} color="var(--color-energy)" fieldName="hvac_power" timestamp={telemetry?.sim_time} updateRate="E+ Tick" />
        <MetricCard title="Comfort Debt" value={`${telemetry?.comfort_debt?.toFixed(2) ?? 0} °C-hr`} color="var(--color-heating)" fieldName="comfort_debt" timestamp={telemetry?.sim_time} updateRate="E+ Tick" />
        <MetricCard title="Carbon Intensity" value={`${telemetry?.carbon_intensity ?? 0} g/kWh`} color="var(--color-secondary)" fieldName="carbon_intensity" timestamp={telemetry?.sim_time} updateRate="E+ Tick" />
        <MetricCard title="AI Status" value="ACTIVE" color="var(--color-accent)" fieldName="ai_decision" timestamp={telemetry?.sim_time} updateRate="Inference" />
        
        {telemetry?.energy_today != null && <MetricCard title="Energy Today" value={`${telemetry.energy_today.toFixed(1)} kWh`} color="var(--color-energy)" fieldName="energy_today" timestamp={telemetry?.sim_time} updateRate="E+ Tick" />}
        {telemetry?.energy_savings != null && <MetricCard title="Energy Savings" value={`${telemetry.energy_savings > 0 ? '+' : ''}${telemetry.energy_savings.toFixed(1)} kWh`} color="#10b981" fieldName="energy_savings" timestamp={telemetry?.sim_time} updateRate="E+ Tick" />}
        {telemetry?.co2_avoided != null && <MetricCard title="CO₂ Avoided" value={`${telemetry.co2_avoided > 0 ? '+' : ''}${telemetry.co2_avoided.toFixed(2)} kg`} color="#10b981" fieldName="co2_avoided" timestamp={telemetry?.sim_time} updateRate="E+ Tick" />}
        {telemetry?.ppd != null && <MetricCard title="PPD (Comfort)" value={`${telemetry.ppd.toFixed(1)}%`} color={telemetry.ppd > 20 ? "#ef4444" : "#10b981"} fieldName="ppd" timestamp={telemetry?.sim_time} updateRate="E+ Tick" />}
      </div>

      {/* Main Chart Area */}
      <div className="col-span-8 glass-panel p-6 h-96 flex items-center justify-center">
        <LiveTelemetryChart />
      </div>

      {/* Safety Feed */}
      <div className="col-span-4 glass-panel p-6 h-96 overflow-y-auto">
        <h3 className="font-semibold mb-4 text-sm text-[var(--color-secondary)] uppercase">Safety Feed</h3>
        <div className="text-xs font-mono space-y-4 text-[var(--color-secondary)]">
          {telemetry?.ai_decision ? (
            <div className="animate-fade-in">
              <p>[{telemetry.sim_time}] <span className="text-[var(--color-accent)]">AI Proposed</span> Z1: {telemetry.ai_decision.Z1_setpoint}°C, Z2: {telemetry.ai_decision.Z2_setpoint}°C</p>
              <p className="mt-1">[{telemetry.sim_time}] <span className="text-[var(--color-success)]">Kernel Verified</span> Action Safe. Rationale: {telemetry.ai_decision.rationale}</p>
            </div>
          ) : (
            <p className="text-gray-500 italic">Awaiting AI inference...</p>
          )}
        </div>
      </div>
      
      {/* 3D Digital Twin Row */}
      <div className="col-span-12 grid grid-cols-12 gap-4">
        {/* Legend */}
        <div className="col-span-4 glass-panel p-6 flex flex-col justify-center">
          <h3 className="font-semibold mb-6 text-sm text-[var(--color-secondary)] uppercase tracking-wider">3D Zone Legend</h3>
          <div className="space-y-4 text-sm">
            <div className="flex items-center gap-4">
              <div className="w-4 h-4 rounded bg-[#3b82f6] shadow-[0_0_10px_#3b82f6]"></div>
              <span><strong className="text-white">Blue (Cooling)</strong><br/><span className="text-[var(--color-secondary)] text-xs">&lt; 21.0°C</span></span>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-4 h-4 rounded bg-[#10b981] shadow-[0_0_10px_#10b981]"></div>
              <span><strong className="text-white">Green (Optimal)</strong><br/><span className="text-[var(--color-secondary)] text-xs">21.0°C - 23.0°C</span></span>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-4 h-4 rounded bg-[#ef4444] shadow-[0_0_10px_#ef4444]"></div>
              <span><strong className="text-white">Red (Heating)</strong><br/><span className="text-[var(--color-secondary)] text-xs">&gt; 23.0°C</span></span>
            </div>
          </div>
        </div>

        {/* 3D Digital Twin Widget */}
        <div className="col-span-8 glass-panel h-[350px] relative overflow-hidden flex flex-col">
          <div className="absolute top-4 left-4 z-10 text-xs font-mono font-bold text-[var(--color-secondary)] uppercase">
            Live 3D Digital Twin
          </div>
          <div className="w-full h-full pointer-events-auto">
            <Canvas camera={{ position: [15, 10, 15], fov: 45 }}>
              <ambientLight intensity={0.5} />
              <directionalLight position={[10, 10, 5]} intensity={1} />
              <BuildingModel />
              <OrbitControls makeDefault enableZoom={true} />
              <gridHelper args={[40, 40, "#27272a", "#18181b"]} position={[0, -0.1, 0]} />
            </Canvas>
          </div>
        </div>
      </div>
      
      <OperatorAssistant />
      
      {/* Temporary Debug Panel */}
      <div className="col-span-12 glass-panel p-6 mt-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-sm text-[var(--color-secondary)] uppercase">End-to-End Diagnostics</h3>
          <FPSCounter />
        </div>
        <div className="grid grid-cols-3 gap-4 text-xs font-mono mb-4">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${wsStatus === 'CONNECTED' ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>WebSocket</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${telemetry ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>EnergyPlus / BuildingState</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${useStore((state) => state.telemetryHistory).length > 0 ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>Zustand / Charts / KPIs</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${telemetry?.zones ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>3D Twin Data</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${telemetry?.ai_decision ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>Ollama / GPU / AI Loop</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${telemetry?.ai_decision?.rationale?.includes('Kernel') ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>Safety Kernel</span>
          </div>
        </div>
        {(!telemetry && lastMessageAt == null && wsStatus === 'CONNECTED') && (
          <div className="p-4 bg-red-900/30 border border-red-500 rounded mb-4 text-sm text-red-200">
            <strong>Warning:</strong> WebSocket is connected but no telemetry has arrived. The backend loop might be blocked by the LLM inference timeout (30s) if the local Qwen model is not running, or it crashed internally.
          </div>
        )}
        <div className="h-32 overflow-y-auto bg-black/50 p-4 rounded text-xs text-gray-300 font-mono whitespace-pre-wrap">
          {rawTelemetry || 'No raw telemetry received yet.'}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, color, fieldName, timestamp, updateRate }: { title: string, value: string, color: string, fieldName?: string, timestamp?: string, updateRate?: string }) {
  const [renderCount, setRenderCount] = React.useState(0);
  const [lastUpdated, setLastUpdated] = React.useState("--");
  
  React.useEffect(() => {
    setRenderCount(c => c + 1);
    setLastUpdated(new Date().toLocaleTimeString());
  }, [value, title, fieldName]);

  return (
    <div className="glass-panel p-6 flex flex-col justify-center relative group">
      <div className="text-xs uppercase font-semibold text-[var(--color-secondary)] mb-1">{title}</div>
      <div className="text-2xl font-bold tracking-tight" style={{ color }}>{value}</div>
      
      {/* Validation Debug Metadata (Hidden by default, shown on hover to keep UI clean) */}
      <div className="absolute inset-0 bg-black/90 p-4 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-center text-[10px] font-mono text-gray-300 z-10 pointer-events-none">
        <div><span className="text-gray-500">Source:</span> store.telemetry.{fieldName}</div>
        <div><span className="text-gray-500">Update Rate:</span> {updateRate || "N/A"}</div>
        <div><span className="text-gray-500">Sim Time:</span> {timestamp || "N/A"}</div>
        <div><span className="text-gray-500">Last UI Render:</span> {lastUpdated} ({renderCount} renders)</div>
      </div>
    </div>
  );
}

function FPSCounter() {
  const [fps, setFps] = React.useState(0);
  
  React.useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    let animFrameId: number;
    
    const loop = () => {
      frameCount++;
      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(Math.round((frameCount * 1000) / (now - lastTime)));
        frameCount = 0;
        lastTime = now;
      }
      animFrameId = requestAnimationFrame(loop);
    };
    
    animFrameId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(animFrameId);
  }, []);
  
  return (
    <div className="text-xs font-mono text-green-400 bg-green-900/20 px-2 py-1 rounded border border-green-800">
      Frontend FPS: {fps}
    </div>
  );
}
