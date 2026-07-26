import asyncio
import websockets
import json

async def check():
    async with websockets.connect("ws://localhost:8000/ws/telemetry") as ws:
        for i in range(10):
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"[{i}] Timestamp: {data.get('sim_time')} HVAC Power: {data.get('hvac_power')} kW Z1 Temp: {data.get('zones', {}).get('Z1', {}).get('temp')} C Z1 Setpoint: {data.get('zones', {}).get('Z1', {}).get('setpoint')} C")


asyncio.run(check())
