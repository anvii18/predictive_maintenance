import os
from pathlib import Path

import pathway as pw

from pipeline.health_rules import build_alert, check_anomaly, compute_health_score

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("FAILUREGUARD_DATA_DIR", str(BASE_DIR / "data")))
SENSOR_FILE = DATA_DIR / "sensor_readings.csv"
OUTPUT_FILE = DATA_DIR / "processed_readings.jsonl"


class SensorSchema(pw.Schema):
    machine_id: str
    timestamp: str
    temperature: float
    vibration: float
    pressure: float


def run():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SENSOR_FILE.is_file():
        raise FileNotFoundError(
            f"{SENSOR_FILE} does not exist. Start simulators/sensor_simulator.py first."
        )

    print(f"Pathway sensor pipeline watching {SENSOR_FILE}", flush=True)
    sensor_stream = pw.io.csv.read(
        str(SENSOR_FILE),
        schema=SensorSchema,
        mode="streaming",
    )
    processed = sensor_stream.select(
        machine_id=pw.this.machine_id,
        timestamp=pw.this.timestamp,
        temperature=pw.this.temperature,
        vibration=pw.this.vibration,
        pressure=pw.this.pressure,
        health_score=pw.apply(
            compute_health_score, pw.this.temperature, pw.this.vibration, pw.this.pressure
        ),
        is_anomaly=pw.apply(
            check_anomaly, pw.this.temperature, pw.this.vibration, pw.this.pressure
        ),
        alert_message=pw.apply(
            build_alert,
            pw.this.machine_id,
            pw.this.temperature,
            pw.this.vibration,
            pw.this.pressure,
        ),
    )
    pw.io.jsonlines.write(processed, str(OUTPUT_FILE))
    print("Pathway sensor pipeline running.", flush=True)
    pw.run()


if __name__ == "__main__":
    run()
