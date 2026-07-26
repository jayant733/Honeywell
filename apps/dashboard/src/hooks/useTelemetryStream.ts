"use client";

import { useEffect } from 'react';
import { useStore } from '@/lib/store';

export function useTelemetryStream() {
  const setTelemetry = useStore((state) => state.setTelemetry);

  const setWsStatus = useStore((state) => state.setWsStatus);

  useEffect(() => {
    console.log("Connecting websocket...");
    const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

    ws.onopen = () => {
      console.log("WEB SOCKET CONNECTED");
      console.log("=====================================================");
      console.log("WEBSOCKET CONNECTION ESTABLISHED");
      console.log("=====================================================");
      setWsStatus('CONNECTED');
    };
    ws.onclose = () => setWsStatus('DISCONNECTED');
    ws.onerror = () => setWsStatus('ERROR');

    let renderCount = 0;
    ws.onmessage = (event) => {
      renderCount++;
      const data = JSON.parse(event.data);
      console.log("================ FRONTEND RECEIVED ================");
      console.log("Entire payload:", JSON.stringify(data, null, 2));
      console.log(`Timestamp: ${data.timestamp}`);
      console.log(`Render Count: ${renderCount}`);
      console.log("Store Updated: YES");
      console.log("=================================================");
      
      setTelemetry(data);
    };

    return () => {
      ws.close();
    };
  }, [setTelemetry, setWsStatus]);
}
