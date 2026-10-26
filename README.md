FailureGuard AI

Live Real-Time Predictive Maintenance System powered by streaming analytics and AI

Live Demo: https://anvii18-predictive-maintenance-app-966ivk.streamlit.app/

Overview-

-FailureGuard AI is a predictive-maintenance demonstration that combines simulated sensor telemetry, streaming analytics, and an optional LLM assistant. Verify the linked live demo and its backend separately before describing the complete system as production-deployed. It:

-Monitors industrial equipment continuously

-Detects anomalies before failures occur

-Computes real-time health scores

-Provides AI-driven contextual repair guidance to technicians

This platform uses streaming analytics and large language models to combine live telemetry with technical documentation for precise recommendations.

🏗 System Architecture
Industrial Sensors
         ↓
Sensor Simulator (updates every 2 sec)
         ↓
Pathway Streaming Engine
         ↓
   ├── Real-Time Anomaly Detection
   └── Live Document Watcher
         ↓
FastAPI Backend (REST API)
         ↓
Groq LLM (Two-Step Intelligent RAG)
         ↓
Streamlit Dashboard (Live Visualization)

Key Features -

-Real-time streaming analytics

-Instant anomaly detection

-Live documentation indexing

-AI repair assistant

-Auto update without system restart

-Local demo runner with supervised service shutdown

Tech Stack-
Component	Technology
Streaming Engine	Pathway 0.29.1
REST API Backend	FastAPI + Uvicorn
Frontend	Streamlit + Plotly
AI Layer	Groq API + LLaMA 3.3 70B
Deployment	Streamlit Cloud

 
How It Works

-Sensor Stream
Pathway continuously watches sensor_readings.csv
Computes:
Health score
Anomaly status
Alert messages
Writes results to processed_readings.jsonl

-Document Watcher
Pathway watches your documents/ folder in streaming mode
Detects updates instantly
Re-indexes technical documents in real time
No manual refresh or server restart required

📚 Knowledge Base (Live Indexed)

-pump_manual.txt
Operating ranges
Common issues
Maintenance schedule
Spare parts lists

-maintenance_log.txt
Historical repair records
Root causes
Actions taken and costs
Technician notes

troubleshooting.txt
Step-by-step repair procedures
Emergency protocols
Contact information

API Endpoints
Method	Endpoint	Description
GET	/sensors	Latest machine sensor readings
GET	/health	Health score per machine
GET	/alerts	Only active anomalies
GET	/summary	Fleet-wide health statistics
POST	/query	AI repair guidance


Project Structure
predictive_maintenance/
│
├── simulators/                    # Sensor data generator
│   └── sensor_simulator.py
│
├── pipeline/                     # Streaming pipelines
│   ├── pathway_pipeline.py
│   └── pathway_rag_server.py
│
├── documents/                    # Live Indexed Knowledge Base
│   ├── pump_manual.txt
│   ├── maintenance_log.txt
│   └── troubleshooting.txt
│
├── backend/                      # REST API
│   └── app.py
│
├── frontend/                     # Streamlit dashboard
│   └── dashboard.py
│
├── data/                        # Pathway generated outputs
│   ├── sensor_readings.csv
│   ├── processed_readings.jsonl
│   └── documents_index.jsonl
│
└── requirements.txt

-What Makes This a True Pathway Project

Unlike many demos using Pathway superficially, FailureGuard AI uses two streaming pipelines:

Pipeline 1 — Sensor Stream
sensor_stream = pw.io.csv.read(
    "data/sensor_readings.csv",
    schema=SensorSchema,
    mode="streaming"
)
processed = sensor_stream.select(
    health_score=pw.apply(compute_health_score, ...),
    is_anomaly=pw.apply(check_anomaly, ...),
    alert_message=pw.apply(build_alert, ...)
)
pw.io.jsonlines.write(processed, "data/processed_readings.jsonl")
Pipeline 2 — Document Watcher
documents = pw.io.fs.read(
    "documents/",
    format="binary",
    mode="streaming",
    with_metadata=True
)

Pathway detects file changes instantly, and the AI layer automatically reflects updates — no manual trigger, no restart.

-Real-World Impact
Target sectors: Manufacturing • Oil & Gas • Power Stations • Water Treatment
Impact: Predict failures hours before they occur
Cost savings: Up to 60% lower emergency repair costs

Safety: Prevents hazardous equipment breakdowns


## Run the complete demo locally

Use Python 3.11 in a virtual environment. From the repository root:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

python -m pip install -r requirements.txt
python run_local.py
```

The runner starts the sensor simulator, both Pathway pipelines, the FastAPI backend, and the Streamlit dashboard. Open http://localhost:8501. Press Ctrl+C in the terminal to stop the services. If startup fails, read the terminal output for the first service that exits.

For manual development, the dashboard can still be started with `streamlit run app.py`; this launches the UI only. Set `API_URL` to the backend base URL if it is not at `http://127.0.0.1:8000`.

Optional environment variables:

- `GROQ_API_KEY`: enables the hosted LLM assistant; without it the assistant returns data-based demo responses.
- `GROQ_MODEL`: overrides the configured Groq model.
- `FAILUREGUARD_DATA_DIR`: overrides the local data directory.
- `FAILUREGUARD_DOCUMENTS_DIR`: overrides the document directory.
- `FAILUREGUARD_API_HOST` and `PORT`: configure the local backend bind address and port.

## Run backend regression tests

```bash
python -m pip install fastapi uvicorn groq pytest httpx
python -m pytest -q
```

GitHub Actions runs the backend regression suite on pushes to the improvement branches and on pull requests into `main`. Passing these tests verifies the covered API and health-rule behavior; it does not replace a full local test of Pathway streaming and the hosted deployment.

