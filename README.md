# FailureGuard AI — Predictive Maintenance Demo

A real-time predictive-maintenance prototype that simulates industrial sensor telemetry, processes readings with **Pathway**, exposes machine health through **FastAPI**, and visualizes the results in a **Streamlit** dashboard. An optional Groq-powered assistant answers maintenance questions using the current readings and local maintenance documents.

> **Scope:** This is an educational prototype using simulated sensor data, not a validated industrial safety system. An anomaly flag is a rule-based warning, not a guarantee that a failure will occur.

## Demo and repository

- **Repository:** https://github.com/anvii18/predictive_maintenance
- **Hosted dashboard:** https://anvii18-predictive-maintenance-app-966ivk.streamlit.app/
- **Local full-stack demo:** run the steps below. The hosted dashboard and local full-stack setup are separate; the hosted UI needs a reachable backend configured through `API_URL` to display live pipeline data.

## What it demonstrates

- **Streaming telemetry:** a simulator writes readings for four machines every two seconds.
- **Rule-based anomaly detection:** temperature, vibration, and pressure thresholds produce a health score and alert message.
- **Live data pipeline:** Pathway reads the sensor CSV in streaming mode and writes processed records to JSONL.
- **REST API:** FastAPI serves current readings, machine health, active alerts, fleet summary, and assistant queries.
- **Document watcher:** Pathway watches the `documents/` folder and indexes maintenance text as files change.
- **Dashboard:** Streamlit and Plotly display health metrics, sensor gauges, and active alerts.
- **Optional LLM assistant:** set `GROQ_API_KEY` to enable generated maintenance guidance; without it, the API returns a clearly labelled rule-based demo response.
- **Regression checks:** GitHub Actions checks Python syntax and runs backend tests.

## Architecture

```text
Sensor simulator ──> sensor_readings.csv ──> Pathway sensor pipeline
                                                │
                                                v
                                      processed_readings.jsonl
                                                │
Maintenance .txt ──> Pathway document watcher   v
                         │                FastAPI backend
                         v                      │
                 documents_index.jsonl           v
                                          Streamlit + Plotly
                                                │
                                     Optional Groq assistant
```

## Run the complete demo locally

**Requirements:** Python 3.11 recommended. Pathway and its dependencies may take a few minutes to install.

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run_local.py
```

Open **http://localhost:8501**. The runner starts the simulator, both Pathway pipelines, the API, and the dashboard; it waits for the sensor file and API health check before continuing. Press **Ctrl+C** in the same terminal to stop the child processes.

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

### Expected demo behaviour

1. The dashboard starts showing readings for four simulated machines.
2. After approximately 20–24 seconds, `PUMP_A` begins receiving deliberately abnormal simulated readings.
3. The Pathway pipeline should flag the anomaly, lower the health score, and surface an alert on the dashboard.
4. Add or edit a `.txt` file in `documents/` to exercise the document watcher. Configure a Groq key if you want generated answers rather than the no-key demo response.

The timing and thresholds are for demonstration only. They are not trained failure-prediction models and should not be used for real equipment decisions.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/healthz` | Liveness check |
| GET | `/sensors` | Latest reading per machine |
| GET | `/health` | Health score and status |
| GET | `/alerts` | Machines currently flagged by the rules |
| GET | `/summary` | Fleet-level counts and average health |
| POST | `/query` | Maintenance assistant response |

With the local demo running, try **http://127.0.0.1:8000/docs** for interactive API documentation.

## Configuration

Optional environment variables:

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Enables the hosted LLM assistant; keep this secret |
| `GROQ_MODEL` | Overrides the configured Groq model |
| `API_URL` | Backend base URL used by the dashboard |
| `FAILUREGUARD_DATA_DIR` | Overrides the directory for sensor and pipeline output files |
| `FAILUREGUARD_DOCUMENTS_DIR` | Overrides the maintenance-document directory |
| `FAILUREGUARD_API_HOST` | Local API bind host; defaults to `127.0.0.1` |
| `PORT` | API port; defaults to `8000` |
| `FAILUREGUARD_STARTUP_TIMEOUT` | Startup wait limit in seconds; defaults to `45` |

For a hosted frontend, set `API_URL` to a publicly reachable backend URL in the hosting platform's secrets/settings. Do not put API keys in source control.

## Tests

Create/activate the virtual environment, then run:

```bash
python -m pip install fastapi uvicorn groq pytest httpx
python -m compileall -q backend frontend pipeline simulators run_local.py app.py
python -m pytest -q
```

GitHub Actions runs the syntax check and backend regression tests for pushes to improvement branches and pull requests into `main`. These checks cover the tested API and rule logic; they do **not** substitute for manually verifying the full Pathway streaming flow or the hosted deployment.

## Project layout

```text
backend/app.py                 FastAPI routes and assistant
frontend/dashboard.py           Streamlit + Plotly UI
pipeline/pathway_pipeline.py    Sensor streaming pipeline
pipeline/pathway_rag_server.py  Live document watcher
pipeline/health_rules.py        Testable health and alert rules
simulators/sensor_simulator.py  Synthetic telemetry generator
documents/                      Example maintenance documents
tests/test_backend.py           Backend regression tests
run_local.py                    Full local process supervisor
```

## Limitations and next steps

- Telemetry is synthetic; the demo does not ingest real equipment data.
- Health scores and alerts use transparent thresholds, not a validated predictive model.
- The LLM assistant is optional and should be treated as advisory; verify all maintenance procedures against approved documentation.
- Before presenting the hosted URL as a fully working end-to-end demo, verify that its configured backend is online and that the dashboard receives live data.
