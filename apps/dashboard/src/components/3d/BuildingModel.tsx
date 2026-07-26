"use client";

import { useRef, useState, useEffect } from 'react';
import { useStore } from '@/lib/store';
import * as THREE from 'three';

// Simple fallback procedural boxes since we don't have a massive .glb model
export default function BuildingModel() {
  const telemetry = useStore((state) => state.telemetry);
  
  // Create simple 3D representation of zones
  return (
    <group position={[0, 0, 0]}>
      {/* Lobby */}
      <ZoneBox 
        id="zone_1"
        position={[0, 2, 0]} 
        args={[10, 4, 10]} 
        telemetry={telemetry}
      />
      {/* Office */}
      <ZoneBox 
        id="zone_2"
        position={[-10, 2, 5]} 
        args={[10, 4, 20]} 
        telemetry={telemetry}
      />
      {/* Conf Room */}
      <ZoneBox 
        id="zone_3"
        position={[10, 2, 0]} 
        args={[10, 4, 10]} 
        telemetry={telemetry}
      />
    </group>
  );
}

function ZoneBox({ id, position, args, telemetry }: any) {
  // Find zone temp, default to 22
  const zoneData = telemetry?.zones?.find((z: any) => z.id === id);
  const temp = zoneData?.temperature || 22.0;
  
  // Interpolate color: Blue (<21) -> Green (21-24) -> Red (>24)
  let color = "#10b981"; // Success Green
  if (temp < 21) color = "#3b82f6"; // Cooling Blue
  if (temp > 24) color = "#ef4444"; // Heating Red

  return (
    <mesh position={position}>
      <boxGeometry args={args} />
      <meshStandardMaterial 
        color={color}
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
  );
}
