import { create } from 'zustand'

export interface Zone {
  id: string;
  name: string;
  temperature: number;
  occupancy: number;
  hvac_mode: string;
  setpoint: number;
}

interface BuildingState {
  zones: Zone[];
  hvac_power: number;
  timestamp: string;
}

interface AppState {
  telemetry: any | null;
  rawTelemetry: string | null;
  telemetryHistory: any[];
  wsStatus: string;
  lastMessageAt: number | null;
  mode: string;
  setTelemetry: (data: any) => void;
  setWsStatus: (status: string) => void;
  setMode: (mode: string) => void;
}

export const useStore = create<AppState>((set) => ({
  telemetry: null,
  rawTelemetry: null,
  telemetryHistory: [],
  wsStatus: 'DISCONNECTED',
  lastMessageAt: null,
  mode: 'SHADOW',
  setTelemetry: (data) => set((state) => {
    console.log("------------------------------------------------");
    console.log("ZUSTAND UPDATE");
    console.log("------------------------------------------------");
    console.log(`Previous state timestamp: ${state.telemetry?.timestamp || 'N/A'}`);
    console.log(`Incoming payload:`, data);
    console.log(`Store timestamp: ${Date.now()}`);
    
    // Maintain history of max 50 items
    const newHistory = [...state.telemetryHistory, data].slice(-50);
    
    console.log(`Updated state: telemetry, rawTelemetry, telemetryHistory, lastMessageAt`);
    console.log(`Changed fields: All telemetry fields`);
    console.log(`Rejected fields: None`);
    console.log("------------------------------------------------");
    
    return { 
      telemetry: data, 
      rawTelemetry: JSON.stringify(data, null, 2), 
      telemetryHistory: newHistory,
      lastMessageAt: Date.now() 
    };
  }),
  setWsStatus: (status) => set({ wsStatus: status }),
  setMode: (mode) => set({ mode }),
}))
