import os
import sys
import socket
import subprocess
import time
import uvicorn

def free_port(port=8000):
    """Automatically free port if another process is holding it."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) == 0:
                print(f"  * Port {port} is busy, freeing it automatically...")
                if sys.platform == 'win32':
                    subprocess.run(
                        f'powershell -Command "Get-Process -Id (Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force"',
                        shell=True,
                        capture_output=True
                    )
                time.sleep(1)
    except Exception:
        pass

def main():
    print("=====================================================================")
    print("  DTC Smart Occupancy System (DSOS) — Intelligent Delhi Transit Platform")
    print("  Delhi Transport Stack Hackathon — Problem 2: Crowdedness Planner")
    print("=====================================================================")
    print("  * Serving Full-Stack Application at: http://localhost:8000")
    print("  * Interactive Swagger API Docs at:   http://localhost:8000/docs")
    print("  * OpenAPI Specification at:          http://localhost:8000/openapi.json")
    print("=====================================================================\n")

    free_port(8000)
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
