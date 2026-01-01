
import subprocess
import time
import sys
import os
import signal

# List of services to run
SERVICES = [
    {"name": "INGEST", "command": [sys.executable, "scripts/ingest.py"]},
    {"name": "WORKER", "command": [sys.executable, "app/worker.py"]},
    {"name": "ANALYZER", "command": [sys.executable, "app/services/analyzer.py"]},
    {"name": "SQUAD", "command": [sys.executable, "run_squad.py"]},
]

processes = []

def start_services():
    print("="*50)
    print("   SENTINEL GRAPH - UNIFIED ORCHESTRATOR")
    print("="*50)
    
    for service in SERVICES:
        print(f"[*] Starting {service['name']}...")
        p = subprocess.Popen(
            service["command"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append({"name": service["name"], "proc": p})
        time.sleep(2) # Give it a moment to start

    print("\n[OK] All services are core and running.")
    print("[URL] Dashboard Access: http://localhost:8000")
    print("[CTRL+C] to stop all services.\n")

def monitor_and_log():
    try:
        while True:
            for service in processes:
                p = service["proc"]
                if p.poll() is not None:
                    print(f"[!] {service['name']} CRASHED with exit code {p.returncode}")
                    # In a real "best" orchestrator, we would restart it here
                    # But for now, we just notify
                
                # Non-blocking read of stdout
                # (Simple version: just print first line if available)
                # In practice, for a dev tool, we'd want to stream to files or separate threads
            
            time.sleep(5)
    except KeyboardInterrupt:
        stop_services()

def stop_services():
    print("\n[*] Shutting down Sentinel Graph...")
    for service in processes:
        print(f"[*] Stopping {service['name']}...")
        service["proc"].terminate()
    print("[OK] All services stopped.")
    sys.exit(0)

if __name__ == "__main__":
    start_services()
    monitor_and_log()
