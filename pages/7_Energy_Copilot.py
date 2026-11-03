"""
Page 7: AI Energy Copilot & Smart Auditor
=========================================
Interactive conversational AI energy auditor.
Answers natural language queries about bills, appliance diagnostics,
solar ROI, Time-of-Use tariffs, and machine learning models.
100% local, software-based execution (zero external APIs).
"""

from __future__ import annotations

import sys
sys.path.insert(0, ".")

import streamlit as st

from app import (
    inject_global_css,
    load_and_clean_data,
    load_water_data,
    load_config_cached,
    render_sidebar,
)
from src.bill_estimator import BillEstimator
from src.copilot import EnergyCopilotEngine
from src.digital_twin import DigitalTwinEngine

st.set_page_config(
    page_title="AI Copilot · Smart Home AI",
    page_icon="💬",
    layout="wide",
)
inject_global_css()
render_sidebar()

cfg = load_config_cached()
df = load_and_clean_data()
water_df = load_water_data(0)

bill_est = BillEstimator(cfg)
bill_data = bill_est.estimate(df, water_df)

# Engine initialization
copilot = EnergyCopilotEngine(cfg)

# Get live telemetry from session state if available
telemetry = {}
if "digital_twin_engine" in st.session_state:
    twin: DigitalTwinEngine = st.session_state.digital_twin_engine
    telemetry = twin.get_telemetry()

st.markdown(
    """
    <div class='page-title'>💬 AI Energy Copilot & Auditor</div>
    <div class='page-subtitle'>
        Conversational Smart Energy Assistant · Instant Natural Language Diagnostics, Solar ROI, and Tariff Auditing
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── PRESET VIVA EVALUATOR CHIPS ───────────────────────────────────────────────
st.markdown("<div class='section-header'>💡 Quick Viva Prompts (Click to Ask)</div>", unsafe_allow_html=True)

presets = copilot.get_preset_queries()
chip_cols = st.columns(3)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": """👋 **Hello! I am your AI Smart Home Energy Copilot.**

I continuously analyze your household metrology, appliances, and BESCOM tiered billing slabs. You can ask me to:
- Explain why your electricity bill spiked.
- Calculate payback period and financial savings for rooftop solar panels.
- Suggest optimal appliance run schedules to exploit Time-of-Use off-peak rates.
- Explain the underlying LightGBM forecasting algorithm and SHAP feature rankings.

*Click any quick prompt above or type your question below!*""",
        }
    ]

# Render prompt chips
for i, query_text in enumerate(presets):
    col = chip_cols[i % 3]
    if col.button(f"🔍 {query_text}", key=f"chip_{i}", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": query_text})
        answer = copilot.answer_query(
            query=query_text,
            telemetry=telemetry,
            monthly_kwh=bill_data.get("monthly_kwh", 385.0),
            monthly_bill=bill_data.get("monthly_bill_inr", 2480.0),
            anomalies_count=3,
        )
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

st.markdown("---")

# ─── CHAT MESSAGES DISPLAY ─────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── CHAT INPUT BOX ────────────────────────────────────────────────────────────
user_query = st.chat_input("Ask a question about your home energy, bills, solar, or models…")

if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("AI analyzing telemetry and tariff matrix…"):
            answer = copilot.answer_query(
                query=user_query,
                telemetry=telemetry,
                monthly_kwh=bill_data.get("monthly_kwh", 385.0),
                monthly_bill=bill_data.get("monthly_bill_inr", 2480.0),
                anomalies_count=3,
            )
            st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

if len(st.session_state.chat_history) > 1:
    if st.button("🗑️ Clear Conversation History", key="clear_chat"):
        st.session_state.chat_history = [st.session_state.chat_history[0]]
        st.rerun()
