"""Start and supervise the complete FailureGuard AI local demo.

Usage:
    python run_local.py

Stop all child processes with Ctrl+C. This script is intended for local
development, not for deployment on Streamlit hosting platforms.
"""
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable
API_HOST = os.getenv("FAILUREGUARD_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("PORT", "8000"))
API_URL = f"http://{API_HOST}:{API_PORT}"
STARTUP_TIMEOUT = float(os.getenv("FAILUREGUARD_STARTUP_TIMEOUT", "45"))

children: list[tuple[str, subprocess.Popen]] = []


def start_process(name: str, command: list[str], env: dict[str, str] | None = None) -> subprocess.Popen:
    print(f"[start] {name}: {' '.join(command)}", flush=True)
    process = subprocess.Popen(command, cwd=BASE_DIR, env=env)
    children.append((name, process))
    return process


def stop_children() -> None:
    for name, process in reversed(children):
        if process.poll() is None:
            print(f"[stop] {name}", flush=True)
            process.terminate()
    deadline = time.monotonic() + 8
    for _, process in reversed(children):
        if process.poll() is None:
            remaining = max(0, deadline - time.monotonic())
            try:
                process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                process.kill()
    for _, process in reversed(children):
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass


def wait_for_file(path: Path, process: subprocess.Popen, name: str) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"{name} exited early with code {process.returncode}")
        if path.is_file() and path.stat().st_size > 0:
            return
        time.sleep(0.25)
    raise TimeoutError(f"Timed out waiting for {path}. Check the {name} logs above.")


def wait_for_api(process: subprocess.Popen) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT
    url = f"{API_URL}/healthz"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Backend exited early with code {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.5)
    raise TimeoutError(f"Backend did not become healthy at {url}")


def main() -> int:
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    sensor_csv = data_dir / "sensor_readings.csv"

    # The simulator creates the CSV header before the streaming reader starts.
    simulator = start_process("sensor simulator", [PYTHON, "simulators/sensor_simulator.py"])
    wait_for_file(sensor_csv, simulator, "sensor simulator")

    start_process("sensor Pathway pipeline", [PYTHON, "pipeline/pathway_pipeline.py"])
    start_process("document Pathway watcher", [PYTHON, "pipeline/pathway_rag_server.py"])

    backend_env = os.environ.copy()
    backend_env["FAILUREGUARD_DATA_DIR"] = str(data_dir)
    backend_env["FAILUREGUARD_DOCUMENTS_DIR"] = str(BASE_DIR / "documents")
    backend_env["API_URL"] = API_URL
    backend = start_process(
        "FastAPI backend",
        [PYTHON, "-m", "uvicorn", "backend.app:app", "--host", API_HOST, "--port", str(API_PORT)],
        env=backend_env,
    )
    wait_for_api(backend)

    dashboard_env = os.environ.copy()
    dashboard_env["API_URL"] = API_URL
    dashboard = start_process(
        "Streamlit dashboard",
        [PYTHON, "-m", "streamlit", "run", "frontend/dashboard.py"],
        env=dashboard_env,
    )

    print("\nFailureGuard AI local demo is running.", flush=True)
    print(f"Dashboard: http://localhost:8501", flush=True)
    print(f"Backend:   {API_URL}", flush=True)
    print("Press Ctrl+C to stop all services.\n", flush=True)

    while True:
        for name, process in children:
            return_code = process.poll()
            if return_code is not None:
                raise RuntimeError(f"{name} exited unexpectedly with code {return_code}")
        time.sleep(1)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nShutting down FailureGuard AI...", flush=True)
        sys.exit(0)
    except Exception as exc:
        print(f"Startup/runtime error: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
    finally:
        stop_children()
