"""Streamlit entry point for FailureGuard AI.

For a complete local demo, run `python run_local.py` instead. Keeping the
dashboard entry point free of hidden background threads makes deployments
and restarts predictable.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DASHBOARD_FILE = BASE_DIR / "frontend" / "dashboard.py"

# Streamlit executes this file as a script. Execute the dashboard in this
# process so the existing Streamlit deployment command remains compatible.
exec(compile(DASHBOARD_FILE.read_text(encoding="utf-8"), str(DASHBOARD_FILE), "exec"))
