import pathway as pw
import os

class SensorSchema(pw.Schema):
    machine_id:  str
    timestamp:   str
    temperature: float
    vibration:   float
    pressure:    float

def compute_health_score(temperature, vibration, pressure):
    score = 100.0
    if temperature > 80:
        score -= (temperature - 80) * 2.5
    if vibration > 3.0:
        score -= (vibration - 3.0) * 15
    if pressure < 3.0:
        score -= (3.0 - pressure) * 8
    return max(0.0, min(100.0, round(score, 1)))

def check_anomaly(temperature, vibration, pressure):
    return bool(
        temperature > 80.0 or
        vibration   > 3.0  or
        pressure    < 3.0
    )

def build_alert(machine_id, temperature, vibration, pressure):
    issues = []
    if temperature > 80:
        issues.append(f"High temp ({temperature}°C)")
    if vibration > 3.0:
        issues.append(f"High vibration ({vibration} mm/s)")
    if pressure < 3.0:
        issues.append(f"Low pressure ({pressure} bar)")
    return f"ALERT: {machine_id} — " + ", ".join(issues) if issues else ""

def run():
    os.makedirs("data", exist_ok=True)

    print("✅ Pathway pipeline starting...")
    print("👀 Watching data/sensor_readings.csv")

    sensor_stream = pw.io.csv.read(
        "data/sensor_readings.csv",
        schema=SensorSchema,
        mode="streaming"
    )

    processed = sensor_stream.select(
        machine_id    = pw.this.machine_id,
        timestamp     = pw.this.timestamp,
        temperature   = pw.this.temperature,
        vibration     = pw.this.vibration,
        pressure      = pw.this.pressure,
        health_score  = pw.apply(
            compute_health_score,
            pw.this.temperature,
            pw.this.vibration,
            pw.this.pressure
        ),
        is_anomaly    = pw.apply(
            check_anomaly,
            pw.this.temperature,
            pw.this.vibration,
            pw.this.pressure
        ),
        alert_message = pw.apply(
            build_alert,
            pw.this.machine_id,
            pw.this.temperature,
            pw.this.vibration,
            pw.this.pressure
        )
    )

    pw.io.jsonlines.write(processed, "data/processed_readings.jsonl")

    print("🚀 Pipeline running — processing live data")
    pw.run()

if __name__ == "__main__":
    run()