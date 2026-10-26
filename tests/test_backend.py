import json

from fastapi.testclient import TestClient

from backend import app as backend


def test_healthz_is_live_without_sensor_files():
    with TestClient(backend.app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sensor_endpoints_read_latest_record_per_machine(tmp_path, monkeypatch):
    readings_file = tmp_path / "processed_readings.jsonl"
    readings_file.write_text(
        "\n".join([
            json.dumps({"machine_id": "PUMP_A", "health_score": 90, "is_anomaly": False}),
            json.dumps({"machine_id": "PUMP_A", "health_score": 35, "is_anomaly": True}),
            "{malformed json",
            json.dumps({"machine_id": "PUMP_B", "health_score": 75, "is_anomaly": False}),
        ]) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(backend, "READINGS_FILE", readings_file)

    with TestClient(backend.app) as client:
        sensors = client.get("/sensors")
        alerts = client.get("/alerts")
        summary = client.get("/summary")
        health = client.get("/health")

    assert sensors.status_code == 200
    assert sensors.json()["PUMP_A"]["health_score"] == 35
    assert [alert["machine_id"] for alert in alerts.json()] == ["PUMP_A"]
    assert summary.json()["total_machines"] == 2
    assert summary.json()["anomaly_machines"] == 1
    assert health.json()["PUMP_B"]["status"] == "warning"


def test_missing_sensor_file_returns_empty_results(tmp_path, monkeypatch):
    monkeypatch.setattr(backend, "READINGS_FILE", tmp_path / "missing.jsonl")
    with TestClient(backend.app) as client:
        assert client.get("/sensors").json() == {}
        assert client.get("/alerts").json() == []
        assert client.get("/summary").json()["total_machines"] == 0


def test_query_rejects_blank_and_oversized_questions():
    with TestClient(backend.app) as client:
        assert client.post("/query", json={"question": "   "}).status_code == 422
        assert client.post("/query", json={"question": "x" * 2001}).status_code == 422


def test_document_reader_falls_back_to_text_files(tmp_path, monkeypatch):
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    (docs_dir / "manual.txt").write_text("Check vibration before restart.", encoding="utf-8")
    monkeypatch.setattr(backend, "DOCUMENT_INDEX_FILE", tmp_path / "missing-index.jsonl")
    monkeypatch.setattr(backend, "DOCUMENTS_DIR", docs_dir)

    assert backend.read_documents() == {"manual.txt": "Check vibration before restart."}
