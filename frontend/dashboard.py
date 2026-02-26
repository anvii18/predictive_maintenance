import streamlit as st
import requests
import plotly.graph_objects as go
import time
from datetime import datetime
if "assistant_answer" not in st.session_state:
    st.session_state.assistant_answer = None

# ── Config ──
API_URL = "http://localhost:8000"
MACHINE_ORDER = ["MOTOR_C", "PUMP_B", "PUMP_A", "COMPRESSOR_D"]

st.set_page_config(
    page_title="FailureGuard AI",
    layout="wide",
    page_icon="🔧"
)

# ── Custom CSS for better look ──
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 10px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    .alert-box {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .normal-box {
        background-color: #00cc44;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──
def get_health_data():
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.json()
    except:
        return {}

def get_sensor_data():
    try:
        response = requests.get(f"{API_URL}/sensors", timeout=2)
        return response.json()
    except:
        return {}

def get_alerts():
    try:
        response = requests.get(f"{API_URL}/alerts", timeout=2)
        return response.json()
    except:
        return []

def ask_assistant(question):
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"question": question},
            timeout=15
        )
        return response.json().get("answer", "No response")
    except:
        return "Assistant unavailable. Make sure backend is running."

def make_gauge(value, title, min_val, max_val, threshold):
    color = "red" if value > threshold else "green"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        number={"font": {"size": 20}},
        gauge={
            "axis": {"range": [min_val, max_val]},
            "bar": {"color": color},
            "steps": [
                {"range": [min_val, threshold * 0.7], "color": "#e8f5e9"},
                {"range": [threshold * 0.7, threshold], "color": "#fff9c4"},
                {"range": [threshold, max_val], "color": "#ffebee"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 3},
                "thickness": 0.75,
                "value": threshold
            }
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(t=40, b=0, l=20, r=20)
    )
    return fig

def make_pressure_gauge(value, title, min_val, max_val, threshold):
    # Pressure is bad when LOW so color logic is reversed
    color = "red" if value < threshold else "green"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        number={"font": {"size": 20}},
        gauge={
            "axis": {"range": [min_val, max_val]},
            "bar": {"color": color},
            "steps": [
                {"range": [min_val, threshold], "color": "#ffebee"},
                {"range": [threshold, max_val], "color": "#e8f5e9"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 3},
                "thickness": 0.75,
                "value": threshold
            }
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(t=40, b=0, l=20, r=20)
    )
    return fig

def get_status_emoji(health_score):
    if health_score >= 80:
        return "🟢", "HEALTHY"
    elif health_score >= 60:
        return "🟡", "WARNING"
    elif health_score >= 40:
        return "🔴", "CRITICAL"
    else:
        return "🚨", "DANGER"

# ── Main App ──
st.markdown('<div class="main-header">🔧 FailureGuard AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Real-Time Predictive Maintenance • Powered by Pathway</div>', unsafe_allow_html=True)

# Live timestamp
st.markdown(f"**Last updated:** {datetime.now().strftime('%H:%M:%S')}")

st.divider()

# ── Section 1: Machine Health Overview ──
st.subheader("🏭 Machine Health Overview")

health_data = get_health_data()

if health_data:
    cols = st.columns(4)
    for i, machine_id in enumerate(MACHINE_ORDER):
        if machine_id in health_data:
            info = health_data[machine_id]
            score = info.get("health_score", 100)
            emoji, status = get_status_emoji(score)

            with cols[i]:
                st.metric(
                    label=f"{emoji} {machine_id}",
                    value=f"{score}%",
                    delta=status
                )
else:
    st.warning("⏳ Waiting for sensor data... Make sure simulator and pipeline are running!")

st.divider()

# ── Section 2: Live Sensor Gauges ──
st.subheader("📊 Live Sensor Readings")

sensor_data = get_sensor_data()

if sensor_data:
    for machine_id in MACHINE_ORDER:
        if machine_id in sensor_data:
            data = sensor_data[machine_id]
            score = data.get("health_score", 100)
            emoji, status = get_status_emoji(score)

            with st.expander(
                f"{emoji} {machine_id} — Health: {score}% — {status}",
                expanded=(score < 80)
            ):
                g1, g2, g3 = st.columns(3)

                with g1:
                    st.plotly_chart(
                        make_gauge(
                            data.get("temperature", 0),
                            "🌡️ Temperature (°C)",
                            0, 100, 80
                        ),
                        use_container_width="stretch",
                        key=f"{machine_id}_temp"
                    )

                with g2:
                    st.plotly_chart(
                        make_gauge(
                            data.get("vibration", 0),
                            "📳 Vibration (mm/s)",
                            0, 6, 3.0
                        ),
                        use_container_width="stretch",
                        key=f"{machine_id}_vibration"
                    )

                with g3:
                    st.plotly_chart(
                        make_pressure_gauge(
                            data.get("pressure", 0),
                            "💨 Pressure (bar)",
                            0, 8, 3.0
                        ),
                        use_container_width="stretch",
                        key=f"{machine_id}_pressure"
                    )

                st.caption(f"Last reading: {data.get('timestamp', 'N/A')}")
else:
    st.info("No sensor data yet")

st.divider()

# ── Section 3: Active Alerts ──
st.subheader("🚨 Active Alerts")

alerts = get_alerts()

if alerts:
    for alert in alerts:
        score = alert.get("health_score", 100)
        emoji, _ = get_status_emoji(score)
        st.error(
            f"{emoji} **{alert.get('machine_id')}** | "
            f"Health: {score}% | "
            f"{alert.get('alert_message', '')} | "
            f"Time: {alert.get('timestamp', '')}"
        )
else:
    st.success("✅ All machines operating normally — No active alerts")

st.divider()

# ── Section 4: AI Technician Assistant ──
st.subheader("🤖 AI Technician Assistant")
st.caption("Ask anything about machine health, repairs, or maintenance procedures")

# Show example questions
st.markdown("**Example questions:**")
ex1, ex2, ex3 = st.columns(3)
with ex1:
    st.code("What's wrong with PUMP_A?")
with ex2:
    st.code("How do I fix high vibration?")
with ex3:
    st.code("Which machine needs attention?")

question = st.text_input(
    "Your question:",
    placeholder="e.g. PUMP_A temperature is critical, what should I do?"
)

if st.button("🔍 Ask Assistant", type="primary"):
    if question:
        with st.spinner("Analyzing..."):
            st.session_state.assistant_answer = ask_assistant(question)
    else:
        st.warning("Please type a question first")

if st.session_state.assistant_answer:
    st.info(f"🤖 {st.session_state.assistant_answer}")

st.divider()

# ── Footer ──
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.8rem;'>
    FailureGuard AI • Built with Pathway + Streamlit • Hack For Green Bharat 2024
</div>
""", unsafe_allow_html=True)

# ── Auto Refresh ──
time.sleep(3)
st.rerun()