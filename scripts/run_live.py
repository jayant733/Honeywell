"""Orchestration script for Sentinel Twin Hackathon Demo."""

import subprocess
import time
import sys
from pathlib import Path
import threading

def start_mcp_server():
    """Starts the MCP server in a separate process."""
    print("[Orchestrator] Starting MCP Server...")
    return subprocess.Popen(
        [sys.executable, "-m", "mcp", "run", "apps/api/mcp_server.py"],
        cwd=str(Path(__file__).parent.parent)
    )

def start_fastapi():
    """Starts the FastAPI backend."""
    print("[Orchestrator] Starting Sentinel Twin API...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8080"],
        cwd=str(Path(__file__).parent.parent)
    )

def main():
    mcp_proc = start_mcp_server()
    api_proc = start_fastapi()
    
    print("\n" + "="*50)
    print("Sentinel Twin Live Demo is RUNNING!")
    print(" - MCP Server: Active")
    print(" - FastAPI Backend: http://localhost:8080")
    print(" - Dashboard: http://localhost:3000 (Make sure to run 'npm run dev' in apps/dashboard)")
    print("="*50 + "\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        mcp_proc.terminate()
        api_proc.terminate()
        mcp_proc.wait()
        api_proc.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
