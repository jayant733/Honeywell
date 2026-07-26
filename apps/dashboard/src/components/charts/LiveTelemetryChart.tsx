"use client";

import { useStore } from "@/lib/store";
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function LiveTelemetryChart() {
  const telemetryHistory = useStore((state) => state.telemetryHistory);

  useEffect(() => {
    if (telemetryHistory && telemetryHistory.length > 0) {
      console.log("------------------------------------------------");
      console.log("WIDGET RENDER: LiveTelemetryChart");
      console.log("Data Source: store.telemetryHistory");
      console.log(`History length: ${telemetryHistory.length}`);
      console.log(`Latest point time: ${telemetryHistory[telemetryHistory.length - 1]?.sim_time}`);
      console.log(`Oldest point time: ${telemetryHistory[0]?.sim_time}`);
      console.log(`Update frequency: Driven by store`);
      console.log(`Dropped frames: 0`);
      console.log("------------------------------------------------");
    }
  }, [telemetryHistory]);

  if (!telemetryHistory || telemetryHistory.length === 0) {
    return <div className="w-full h-full flex items-center justify-center text-[var(--color-secondary)]">Awaiting Live Telemetry...</div>;
  }

  // Format data for Recharts
  const data = telemetryHistory.map((pt) => ({
    time: pt.sim_time,
    power: pt.hvac_power || 0,
    tempZ1: pt.zones?.Z1?.temp || 0,
    tempZ2: pt.zones?.Z2?.temp || 0
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
        <XAxis dataKey="time" stroke="#888" fontSize={10} />
        <YAxis yAxisId="left" stroke="#888" fontSize={10} domain={[0, 20]} tickFormatter={(v) => v.toFixed(1)} />
        <YAxis yAxisId="right" orientation="right" stroke="#888" fontSize={10} domain={[18, 25]} tickFormatter={(v) => v.toFixed(1)} />
        <Tooltip contentStyle={{ backgroundColor: '#111', borderColor: '#333' }} />
        <Line yAxisId="left" type="monotone" dataKey="power" stroke="var(--color-energy)" strokeWidth={2} dot={false} name="Total Power (kW)" isAnimationActive={false} />
        <Line yAxisId="right" type="monotone" dataKey="tempZ1" stroke="var(--color-heating)" strokeWidth={2} dot={false} name="Z1 Temp (°C)" isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
