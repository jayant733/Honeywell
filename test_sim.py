import asyncio
from apps.api.main import telemetry_simulator

async def test_sim():
    print("Testing telemetry simulator...")
    task = asyncio.create_task(telemetry_simulator())
    await asyncio.sleep(60)
    print("Test complete.")

if __name__ == "__main__":
    asyncio.run(test_sim())
