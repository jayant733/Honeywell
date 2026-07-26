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
  telemetry: BuildingState | null;
  mode: string;
  setTelemetry: (data: BuildingState) => void;
  setMode: (mode: string) => void;
}

export const useStore = create<AppState>((set) => ({
  telemetry: null,
  mode: 'SHADOW',
  setTelemetry: (data) => set({ telemetry: data }),
  setMode: (mode) => set({ mode }),
}))
