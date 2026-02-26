from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import json
import os

# ── Setup ──
app = FastAPI(title="FailureGuard AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Configure Groq ──
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ── Models ──
class QueryRequest(BaseModel):
    question: str

# ── Helper Functions ──
def read_latest_readings():
    filepath = "data/processed_readings.jsonl"

    if not os.path.exists(filepath):
        return {}

    readings = {}
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()

        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                machine_id = data.get("machine_id")
                if machine_id and machine_id not in readings:
                    readings[machine_id] = data
            except:
                continue
    except:
        return {}

    return readings

def read_documents():
    """
    Try Pathway live document index first.
    Falls back to reading files directly.
    """
    docs = {}

    # Try Pathway live index
    pathway_index = "data/documents_index.jsonl"
    if os.path.exists(pathway_index):
        try:
            with open(pathway_index, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    path = data.get("path", "")
                    content = data.get("content", "")
                    if path and content:
                        filename = os.path.basename(path)
                        docs[filename] = content
            if docs:
                print(f"✅ Loaded {len(docs)} docs from Pathway index")
                return docs
        except Exception as e:
            print(f"Pathway index failed, using fallback: {e}")

    # Fallback — read files directly
    doc_folder = "documents"
    if os.path.exists(doc_folder):
        for filename in os.listdir(doc_folder):
            if filename.endswith(".txt"):
                filepath = os.path.join(doc_folder, filename)
                try:
                    with open(filepath, "r") as f:
                        docs[filename] = f.read()
                except:
                    continue
    return docs

def get_health_status(score):
    if score >= 80:
        return "healthy", "green"
    elif score >= 60:
        return "warning", "yellow"
    elif score >= 40:
        return "critical", "red"
    else:
        return "danger", "darkred"

# ── API Endpoints ──

@app.get("/")
def root():
    return {"message": "FailureGuard AI Backend Running ✅"}

@app.get("/sensors")
def get_sensor_data():
    return read_latest_readings()

@app.get("/alerts")
def get_alerts():
    readings = read_latest_readings()
    alerts = []

    for machine_id, data in readings.items():
        if data.get("is_anomaly"):
            alerts.append({
                "machine_id": machine_id,
                "timestamp": data.get("timestamp"),
                "health_score": data.get("health_score"),
                "temperature": data.get("temperature"),
                "vibration": data.get("vibration"),
                "pressure": data.get("pressure"),
                "alert_message": data.get("alert_message", "")
            })

    return alerts

@app.get("/health")
def get_machine_health():
    readings = read_latest_readings()
    health_summary = {}

    for machine_id, data in readings.items():
        score = data.get("health_score", 100)
        status, color = get_health_status(score)

        health_summary[machine_id] = {
            "health_score": score,
            "status": status,
            "color": color,
            "is_anomaly": data.get("is_anomaly", False),
            "latest_reading": data
        }

    return health_summary

@app.get("/summary")
def get_summary():
    readings = read_latest_readings()

    total = len(readings)
    anomalies = sum(
        1 for d in readings.values()
        if d.get("is_anomaly")
    )
    healthy = total - anomalies

    avg_health = 0
    if readings:
        avg_health = sum(
            d.get("health_score", 100)
            for d in readings.values()
        ) / total

    return {
        "total_machines": total,
        "healthy_machines": healthy,
        "anomaly_machines": anomalies,
        "average_health_score": round(avg_health, 1)
    }

@app.post("/query")
def query_assistant(request: QueryRequest):
    readings = read_latest_readings()
    documents = read_documents()

    sensor_context = json.dumps(readings, indent=2)

    all_docs = ""
    for filename, content in documents.items():
        all_docs += f"\n--- {filename} ---\n{content}\n"

    if not groq_client:
        return {
            "answer": "Demo mode — No API key set. PUMP_A shows critical anomalies.",
            "sources": list(documents.keys())
        }

    try:
        # Step 1 — Smart retrieval using Groq
        retrieval_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a document retrieval system. Extract only the most relevant sections from the documents that relate to the question. Return only relevant excerpts."
                },
                {
                    "role": "user",
                    "content": f"Question: {request.question}\n\nDocuments:\n{all_docs}\n\nReturn only the most relevant sections."
                }
            ],
            max_tokens=300
        )

        relevant_context = retrieval_response.choices[0].message.content

        # Step 2 — Final answer using sensor data + retrieved docs
        final_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert industrial maintenance technician assistant."
                },
                {
                    "role": "user",
                    "content": f"""LIVE SENSOR DATA:
{sensor_context}

RELEVANT DOCUMENTATION:
{relevant_context}

QUESTION: {request.question}

Give a specific actionable answer based on sensor values and documentation."""
                }
            ],
            max_tokens=500
        )

        answer = final_response.choices[0].message.content

    except Exception as e:
        answer = f"Assistant error: {str(e)}"

    return {
        "answer": answer,
        "sources": list(documents.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)