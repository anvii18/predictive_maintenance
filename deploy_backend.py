"""Run the simulator, Pathway pipelines, and FastAPI as one hosted backend service.

Used by Render via render.yaml. The Streamlit frontend is deployed separately
and connects to this service through its API_URL setting.
"""
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable
HOST = os.getenv("FAILUREGUARD_API_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DATA_DIR = Path(os.getenv("FAILUREGUARD_DATA_DIR", str(BASE_DIR / "data"))).resolve()
DOCUMENTS_DIR = Path(os.getenv("FAILUREGUARD_DOCUMENTS_DIR", str(BASE_DIR / "documents"))).resolve()
STARTUP_TIMEOUT = float(os.getenv("FAILUREGUARD_STARTUP_TIMEOUT", "60"))

children: list[tuple[str, subprocess.Popen]] = []
stop_requested = False


def request_stop(_signum, _frame):
    global stop_requested
    stop_requested = True


def start(name: str, command: list[str], env: dict[str, str]) -> subprocess.Popen:
    print(f"[start] {name}: {' '.join(command)}", flush=True)
    process = subprocess.Popen(command, cwd=BASE_DIR, env=env)
    children.append((name, process))
    return process


def wait_for_sensor_file(process: subprocess.Popen) -> None:
    target = DATA_DIR / "sensor_readings.csv"
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline and not stop_requested:
        if process.poll() is not None:
            raise RuntimeError(f"Sensor simulator exited with code {process.returncode}")
        if target.exists() and target.stat().st_size > 0:
            return
        time.sleep(0.25)
    raise TimeoutError(f"Timed out waiting for {target}")


def wait_for_api(process: subprocess.Popen) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT
    url = f"http://127.0.0.1:{PORT}/healthz"
    while time.monotonic() < deadline and not stop_requested:
        if process.poll() is not None:
            raise RuntimeError(f"FastAPI exited with code {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.5)
    raise TimeoutError(f"FastAPI did not become healthy at {url}")


def stop_children() -> None:
    for name, process in reversed(children):
        if process.poll() is None:
            print(f"[stop] {name}", flush=True)
            process.terminate()
    deadline = time.monotonic() + 10
    for _, process in reversed(children):
        if process.poll() is None:
            try:
                process.wait(timeout=max(0.1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                process.kill()
    for _, process in reversed(children):
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass


def main() -> int:
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["FAILUREGUARD_DATA_DIR"] = str(DATA_DIR)
    env["FAILUREGUARD_DOCUMENTS_DIR"] = str(DOCUMENTS_DIR)

    simulator = start("sensor simulator", [PYTHON, "simulators/sensor_simulator.py"], env)
    wait_for_sensor_file(simulator)
    start("Pathway sensor pipeline", [PYTHON, "pipeline/pathway_pipeline.py"], env)
    start("Pathway document watcher", [PYTHON, "pipeline/pathway_rag_server.py"], env)

    api = start(
        "FastAPI",
        [PYTHON, "-m", "uvicorn", "backend.app:app", "--host", HOST, "--port", str(PORT)],
        env,
    )
    wait_for_api(api)
    print(f"FailureGuard backend is healthy on port {PORT}.", flush=True)

    while not stop_requested:
        for name, process in children:
            code = process.poll()
            if code is not None:
                raise RuntimeError(f"{name} exited unexpectedly with code {code}")
        time.sleep(1)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Hosted backend startup/runtime error: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
    finally:
        stop_children()
