import csv
import os
import random
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("FAILUREGUARD_DATA_DIR", str(BASE_DIR / "data")))
MACHINES = ["PUMP_A", "PUMP_B", "MOTOR_C", "COMPRESSOR_D"]
FIELDS = ["machine_id", "timestamp", "temperature", "vibration", "pressure"]


def generate_reading(machine_id, tick):
    if machine_id == "PUMP_A" and tick > 10:
        temperature = round(random.uniform(82, 95), 2)
        vibration = round(random.uniform(3.2, 4.8), 3)
        pressure = round(random.uniform(2.0, 3.0), 2)
    else:
        temperature = round(random.uniform(62, 74), 2)
        vibration = round(random.uniform(1.0, 2.4), 3)
        pressure = round(random.uniform(3.6, 4.8), 2)

    return {
        "machine_id": machine_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": temperature,
        "vibration": vibration,
        "pressure": pressure,
    }


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / "sensor_readings.csv"

    with filepath.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        handle.flush()

    print(f"Sensor simulator started; writing to {filepath}", flush=True)
    print("PUMP_A anomaly begins after approximately 20 seconds.", flush=True)

    tick = 0
    while True:
        with filepath.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            for machine in MACHINES:
                writer.writerow(generate_reading(machine, tick))
            handle.flush()
        print(f"Tick {tick} | {datetime.now():%H:%M:%S}", flush=True)
        tick += 1
        time.sleep(2)


if __name__ == "__main__":
    main()
