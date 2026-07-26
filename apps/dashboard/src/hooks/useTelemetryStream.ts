"use client";

import { useEffect } from 'react';
import { useStore } from '@/lib/store';

export function useTelemetryStream() {
  const setTelemetry = useStore((state) => state.setTelemetry);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws/telemetry');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTelemetry(data);
    };

    return () => {
      ws.close();
    };
  }, [setTelemetry]);
}
