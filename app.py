import threading
import subprocess
import sys
import os
import time

def run_simulator():
    os.system("python3 simulators/sensor_simulator.py")

def run_pipeline():
    os.system("python3 pipeline/pathway_pipeline.py")

def run_rag():
    os.system("python3 pipeline/pathway_rag_server.py")

def run_backend():
    os.system("python3 backend/app.py")

def run_frontend():
    os.system("streamlit run frontend/dashboard.py --server.address 0.0.0.0")

if __name__ == "__main__":
    print("🚀 Starting FailureGuard AI...")

    # Start all processes in separate threads
    threads = [
        threading.Thread(target=run_simulator),
        threading.Thread(target=run_pipeline),
        threading.Thread(target=run_rag),
        threading.Thread(target=run_backend),
        threading.Thread(target=run_frontend),
    ]

    for t in threads:
        t.daemon = True
        t.start()
        time.sleep(2)  # Small delay between each startup

    print("✅ All systems running!")
    print("🌐 Open browser at http://localhost:8501")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
