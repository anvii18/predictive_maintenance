"""Pure sensor health and anomaly rules, independent of the Pathway runtime."""


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
    return bool(temperature > 80.0 or vibration > 3.0 or pressure < 3.0)


def build_alert(machine_id, temperature, vibration, pressure):
    issues = []
    if temperature > 80:
        issues.append(f"High temp ({temperature}°C)")
    if vibration > 3.0:
        issues.append(f"High vibration ({vibration} mm/s)")
    if pressure < 3.0:
        issues.append(f"Low pressure ({pressure} bar)")
    return f"ALERT: {machine_id} — " + ", ".join(issues) if issues else ""
