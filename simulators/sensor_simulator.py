import csv
import time
import random
import os
from datetime import datetime

MACHINES = ["PUMP_A", "PUMP_B", "MOTOR_C", "COMPRESSOR_D"]

def generate_reading(machine_id, tick):
    if machine_id == "PUMP_A" and tick > 10:
        temperature = round(random.uniform(82, 95), 2)
        vibration   = round(random.uniform(3.2, 4.8), 3)
        pressure    = round(random.uniform(2.0, 3.0), 2)
    else:
        temperature = round(random.uniform(62, 74), 2)
        vibration   = round(random.uniform(1.0, 2.4), 3)
        pressure    = round(random.uniform(3.6, 4.8), 2)

    return {
        "machine_id":  machine_id,
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": temperature,
        "vibration":   vibration,
        "pressure":    pressure,
    }

def main():
    os.makedirs("data", exist_ok=True)
    filepath = "data/sensor_readings.csv"

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "machine_id", "timestamp",
            "temperature", "vibration", "pressure"
        ])
        writer.writeheader()

    print("✅ Simulator started!")
    print("⏳ PUMP_A anomaly begins after ~20 seconds")

    tick = 0
    while True:
        with open(filepath, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "machine_id", "timestamp",
                "temperature", "vibration", "pressure"
            ])
            for machine in MACHINES:
                reading = generate_reading(machine, tick)
                writer.writerow(reading)

        print(f"Tick {tick} ✓ | {datetime.now().strftime('%H:%M:%S')}")
        tick += 1
        time.sleep(2)

if __name__ == "__main__":
    main()