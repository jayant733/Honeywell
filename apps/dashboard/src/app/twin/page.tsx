"use client";

import { useTelemetryStream } from "@/hooks/useTelemetryStream";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import BuildingModel from "@/components/3d/BuildingModel";

export default function TwinPage() {
  useTelemetryStream();

  return (
    <div className="w-full h-[80vh] glass-panel overflow-hidden relative">
      <div className="absolute top-4 left-4 z-10 text-xs font-mono text-[var(--color-secondary)] uppercase bg-[var(--color-surface)] p-2 rounded border border-[var(--color-border)]">
        Live Digital Twin
      </div>
      <Canvas camera={{ position: [20, 20, 20], fov: 45 }}>
        <color attach="background" args={["#09090b"]} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <BuildingModel />
        <OrbitControls makeDefault />
        <gridHelper args={[50, 50, "#27272a", "#18181b"]} />
      </Canvas>
    </div>
  );
}
