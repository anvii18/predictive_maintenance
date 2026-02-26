FailureGuard AI

Live Real-Time Predictive Maintenance System powered by streaming analytics and AI

Live Demo: https://anvii18-predictive-maintenance-app-966ivk.streamlit.app/

Overview-

-FailureGuard AI is a production-deployed, real-time predictive maintenance platform that:

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

-Production-grade deployed app

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

👩‍💻 Team Roles
