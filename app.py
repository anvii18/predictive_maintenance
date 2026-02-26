import threading
import os
import sys
import time

# Use the SAME python that is running this script
PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_simulator():
    os.chdir(BASE_DIR)
    os.system(f"{PYTHON} simulators/sensor_simulator.py")

def run_pipeline():
    os.chdir(BASE_DIR)
    os.system(f"{PYTHON} pipeline/pathway_pipeline.py")

def run_rag():
    os.chdir(BASE_DIR)
    os.system(f"{PYTHON} pipeline/pathway_rag_server.py")

def run_backend():
    os.chdir(BASE_DIR)
    os.system(f"{PYTHON} backend/app.py")

# Start background processes
def start_background():
    threads = [
        threading.Thread(target=run_simulator, daemon=True),
        threading.Thread(target=run_pipeline, daemon=True),
        threading.Thread(target=run_rag, daemon=True),
        threading.Thread(target=run_backend, daemon=True),
    ]
    for t in threads:
        t.start()
        time.sleep(2)

# Only start once
if "BACKGROUND_STARTED" not in os.environ:
    os.environ["BACKGROUND_STARTED"] = "1"
    print("🚀 Starting background services...")
    start_background()
    print("⏳ Waiting for services to initialize...")
    time.sleep(8)
    print("✅ All services running!")

# Run dashboard
exec(open(os.path.join(BASE_DIR, "frontend/dashboard.py")).read())
