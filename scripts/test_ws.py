import asyncio
import websockets

async def test_ws():
    async with websockets.connect("ws://localhost:8000/ws/telemetry") as ws:
        print("Connected!")
        for _ in range(3):
            msg = await ws.recv()
            print(f"Received: {msg}")

asyncio.run(test_ws())
