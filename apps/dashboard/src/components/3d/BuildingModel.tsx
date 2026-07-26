"use client";

import { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useStore } from '@/lib/store';
import * as THREE from 'three';

// Simple fallback procedural boxes since we don't have a massive .glb model
export default function BuildingModel() {
  const telemetry = useStore((state) => state.telemetry);
  
  console.log("[3D TWIN TELEMETRY]", telemetry);
  
  // Create simple 3D representation of zones
  return (
    <group position={[0, 0, 0]}>
      {/* Zone 1: Perimeter */}
      <ZoneBox 
        id="Z1"
        position={[-5, 2, 0]} 
        args={[10, 4, 12]} 
        telemetry={telemetry}
      />
      {/* Zone 2: Core */}
      <ZoneBox 
        id="Z2"
        position={[7, 2, 0]} 
        args={[12, 4, 12]} 
        telemetry={telemetry}
      />
      {/* AI Pulse Ring */}
      <AIPulseRing telemetry={telemetry} />
    </group>
  );
}

function AIPulseRing({ telemetry }: any) {
  const meshRef = useRef<any>(null);
  const materialRef = useRef<any>(null);
  
  useFrame((state) => {
    if (meshRef.current && materialRef.current) {
      meshRef.current.rotation.y += 0.02;
      // Pulse rapidly if AI recently decided something
      const isActive = telemetry?.ai_decision != null;
      const pulseSpeed = isActive ? 10 : 2;
      materialRef.current.opacity = 0.2 + (Math.sin(state.clock.elapsedTime * pulseSpeed) + 1) * 0.2;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0.1, 5]} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[12, 14, 32]} />
      <meshBasicMaterial ref={materialRef} color="#a855f7" transparent opacity={0.5} side={THREE.DoubleSide} />
    </mesh>
  );
}

function ZoneBox({ id, position, args, telemetry }: any) {
  const meshRef = useRef<any>(null);
  const materialRef = useRef<any>(null);

  // Find zone temp, default to 22
  const zoneData = telemetry?.zones?.[id];
  const temp = zoneData?.temp || 22.0;
  
  // Interpolate color targets: Blue (<21) -> Green (21-23) -> Red (>23)
  let targetHex = "#10b981"; // Success Green
  if (temp < 21.0) targetHex = "#3b82f6"; // Cooling Blue
  if (temp > 23.0) targetHex = "#ef4444"; // Heating Red

  const targetColor = new THREE.Color(targetHex);
  
  useEffect(() => {
    if (telemetry) {
        console.log("------------------------------------------------");
        console.log(`3D TWIN UPDATED: ${id}`);
        console.log(`Temperature: ${temp.toFixed(1)}°C`);
        console.log(`Target Color: ${targetHex}`);
        console.log(`Animation State: Breathing (Speed: ${(telemetry?.hvac_power || 10) * 0.2})`);
        console.log("------------------------------------------------");
    }
  }, [telemetry?.timestamp, id, temp, targetHex, telemetry?.hvac_power]);

  useFrame((state, delta) => {
    if (materialRef.current) {
       materialRef.current.color.lerp(targetColor, delta * 2);
    }
    if (meshRef.current) {
        // Slight breathing animation to show the twin is "alive"
        // The frequency can be tied to power, but for now we just make it breathe
        const speed = (telemetry?.hvac_power || 10) * 0.2;
        const scaleY = 1 + Math.sin(state.clock.elapsedTime * speed + position[0]) * 0.05;
        meshRef.current.scale.setY(scaleY);
        meshRef.current.position.y = 0; // Relative to group
    }
  });

  return (
    <group position={position}>
      <mesh ref={meshRef} position={[0, 0, 0]}>
        <boxGeometry args={args} />
        <meshStandardMaterial 
          ref={materialRef}
          color="#10b981"
          transparent={true}
          opacity={0.8}
          roughness={0.2}
          metalness={0.8}
        />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(...args as [number, number, number])]} />
          <lineBasicMaterial color="#ffffff" opacity={0.2} transparent />
        </lineSegments>
      </mesh>
      
      {/* Roof Glow (HVAC Power) */}
      {telemetry?.hvac_power > 0 && (
        <pointLight position={[0, args[1]/2 + 1, 0]} color="#fbbf24" intensity={Math.min(telemetry.hvac_power * 0.5, 5)} distance={10} />
      )}
      
      {/* Floating People (Occupancy) */}
      {Array.from({ length: Math.min(zoneData?.occupants || 0, 10) }).map((_, i) => (
        <mesh key={`occ-${i}`} position={[(i % 3) - 1, args[1]/2 + 0.5, Math.floor(i / 3) - 1]}>
          <sphereGeometry args={[0.3, 8, 8]} />
          <meshBasicMaterial color="#fcd34d" />
        </mesh>
      ))}

      {/* Airflow Arrow (Fan speed proxy from power) */}
      {telemetry?.hvac_power > 0 && (
        <AirflowArrow height={args[1]/2} speed={telemetry.hvac_power * 0.5} />
      )}
    </group>
  );
}

function AirflowArrow({ height, speed }: { height: number, speed: number }) {
  const ref = useRef<any>(null);
  useFrame((state) => {
    if (ref.current) {
      ref.current.position.y = height + 1 + Math.sin(state.clock.elapsedTime * speed) * 0.5;
    }
  });
  
  return (
    <mesh ref={ref}>
      <coneGeometry args={[0.5, 1, 4]} />
      <meshBasicMaterial color="#38bdf8" transparent opacity={0.6} />
    </mesh>
  );
}
