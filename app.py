"""
Smart Home Utility AI — Streamlit Entry Point
==============================================
Handles global configuration, CSS injection, data loading,
model training, and sidebar navigation.
"""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import logging
import sys
import warnings
from pathlib import Path

import streamlit as st
import yaml

# Suppress verbose warnings from LightGBM and SHAP
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# ────────────────────────────────────────────────────────────────────────────
# Page config — MUST be first Streamlit call
# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Home Utility AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ────────────────────────────────────────────────────────────────────────────
# Global CSS  — glassmorphism dark theme
# ────────────────────────────────────────────────────────────────────────────
def inject_global_css() -> None:
    # Base dark theme & glassmorphism (always applied on every page)
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Base */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 50%, #0a0e1a 100%);
            color: #e2e8f0;
        }

        /* Hide default Streamlit chrome */
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: rgba(10, 14, 26, 0.95);
            border-right: 1px solid rgba(0, 212, 255, 0.15);
        }
        [data-testid="stSidebar"] .css-1d391kg { padding-top: 1rem; }

        /* KPI / Glass Cards */
        .kpi-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            animation: fadeInUp 0.5s ease;
        }
        .kpi-card:hover {
            border-color: rgba(0, 212, 255, 0.4);
            transform: translateY(-3px);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.12);
        }
        .kpi-title {
            font-size: 0.78rem; font-weight: 500; text-transform: uppercase;
            letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 0.5rem;
        }
        .kpi-value {
            font-size: 2.2rem; font-weight: 700;
            background: linear-gradient(135deg, #00d4ff, #7b5ea7);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; line-height: 1.1;
        }
        .kpi-sub { font-size: 0.82rem; color: #64748b; margin-top: 0.4rem; }
        .kpi-badge {
            display: inline-block; font-size: 0.7rem; font-weight: 600;
            padding: 0.15rem 0.6rem; border-radius: 999px; margin-top: 0.5rem;
        }
        .kpi-badge.good { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
        .kpi-badge.warn { background: rgba(255,170,0,0.15);  color: #ffaa00; border: 1px solid rgba(255,170,0,0.3); }
        .kpi-badge.bad  { background: rgba(255,68,68,0.15);  color: #ff4444; border: 1px solid rgba(255,68,68,0.3); }

        /* Typography */
        .page-title {
            font-size: 1.9rem; font-weight: 700;
            background: linear-gradient(135deg, #00d4ff 0%, #7b5ea7 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; margin-bottom: 0.25rem;
        }
        .page-subtitle {
            font-size: 0.88rem; color: #64748b; margin-bottom: 1.5rem;
        }

        /* Status Pills */
        .status-pill {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem;
            font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
        }
        .status-pill.normal { background: rgba(0,255,136,0.12); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
        .status-pill.alert  { background: rgba(255,68,68,0.12);   color: #ff4444; border: 1px solid rgba(255,68,68,0.3); }
        .status-pill.leak   { background: rgba(0,212,255,0.12);  color: #00d4ff; border: 1px solid rgba(0,212,255,0.3); }

        /* Navigation cards */
        .nav-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px; padding: 1rem 1.2rem;
            margin-bottom: 0.75rem; transition: all 0.25s ease;
            cursor: pointer; text-decoration: none; display: block;
        }
        .nav-card:hover {
            background: rgba(0, 212, 255, 0.07);
            border-color: rgba(0, 212, 255, 0.35);
            transform: translateX(4px);
        }
        .nav-card-title { font-size: 0.95rem; font-weight: 600; color: #f1f5f9; }
        .nav-card-desc  { font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; }

        /* Animation */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(12px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )





# ────────────────────────────────────────────────────────────────────────────
# Cached data / model loading
# ────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_config_cached() -> dict:
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


@st.cache_resource(show_spinner="⬇️ Downloading & preparing dataset…")
def load_and_clean_data():
    """Download (if needed), clean, and return hourly energy DataFrame."""
    from src.dataset_loader import DatasetLoader
    from src.data_cleaning import DataCleaner

    cfg = load_config_cached()
    loader = DatasetLoader(cfg)
    raw_path = loader.get_raw_path()

    cleaner = DataCleaner(cfg)
    df = cleaner.clean(raw_path)
    return df


@st.cache_resource(show_spinner="💧 Generating water data…")
def load_water_data(n: int):
    """Generate synthetic water usage aligned to energy data index."""
    import pandas as pd
    from src.water_generator import WaterDataGenerator

    cfg = load_config_cached()
    gen = WaterDataGenerator(cfg)
    # We need the index — re-derive it
    df = load_and_clean_data()
    return gen.generate(df.index)


@st.cache_resource(show_spinner="🔧 Engineering features…")
def load_features():
    """Build full feature-engineered DataFrame."""
    from src.feature_engineering import FeatureEngineer

    cfg = load_config_cached()
    df = load_and_clean_data()
    eng = FeatureEngineer(cfg)
    return eng.build(df)


@st.cache_resource(show_spinner="🤖 Training / loading forecast model…")
def load_forecast_engine():
    """Train or load the LightGBM forecasting model."""
    from src.forecasting import ForecastingEngine

    cfg = load_config_cached()
    engine = ForecastingEngine(cfg)

    feat_df = load_features()

    if engine.is_trained():
        engine.load()
    else:
        with st.spinner("🏋️ Training LightGBM model (first run only)…"):
            engine.train(feat_df)

    return engine


@st.cache_resource(show_spinner="🔍 Preparing anomaly detector…")
def load_anomaly_engine():
    """Train or load IsolationForest."""
    from src.anomaly_detection import AnomalyDetectionEngine

    cfg = load_config_cached()
    engine = AnomalyDetectionEngine(cfg)
    feat_df = load_features()

    if engine.is_trained():
        engine.load()
    else:
        with st.spinner("🏋️ Training Isolation Forest (first run only)…"):
            feature_cols = [c for c in feat_df.columns if c != cfg["features"]["target"]]
            engine.train_isolation_forest(feat_df[feature_cols].dropna())

    return engine


@st.cache_data(show_spinner="📊 Running forecasts…", ttl=3600)
def get_forecast_results():
    """Get in-sample predictions and future forecast."""
    feat_df = load_features()
    engine = load_forecast_engine()
    in_sample = engine.predict_on_df(feat_df)
    future = engine.forecast_future(feat_df)
    return in_sample, future


@st.cache_data(show_spinner="🚨 Detecting anomalies…", ttl=3600)
def get_anomaly_results():
    """Run anomaly detection across all signals."""
    feat_df = load_features()
    water_df = load_water_data(0)  # arg unused but needed for cache key
    in_sample, _ = get_forecast_results()
    cfg = load_config_cached()
    target = cfg["features"]["target"]
    feature_cols = [c for c in feat_df.columns if c != target]

    engine = load_anomaly_engine()
    return engine.detect(feat_df[feature_cols].dropna(), in_sample, water_df)


@st.cache_resource(show_spinner="🔮 Initialising SHAP explainer…")
def load_explainer():
    """Initialise SHAP TreeExplainer."""
    from src.explainability import ExplainabilityEngine

    exp = ExplainabilityEngine()
    engine = load_forecast_engine()
    exp.setup(engine)
    return exp


# ────────────────────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align:center; padding: 1rem 0 1.5rem;'>
                <div style='font-size:2.5rem'>🏠</div>
                <div style='font-size:1.1rem; font-weight:700; color:#00d4ff'>Smart Home</div>
                <div style='font-size:0.8rem; color:#64748b'>Utility AI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        nav_items = [
            ("🏠", "1 Overview", "KPI metrics & official energy audit certificate"),
            ("🔍", "2 Analysis", "Deep dive into consumption patterns & heatmaps"),
            ("🔮", "3 Forecast", "LightGBM 24–72h predictions & SHAP explainability"),
            ("🚨", "4 Alerts & Tips", "Anomalies detected + ranked savings recommendations"),
            ("🎬", "5 Live Replay", "Real-time streaming replay + water leak detection"),
            ("🏠", "6 Digital Twin", "Virtual home & live software fault injection studio"),
            ("💬", "7 Energy Copilot", "Conversational AI auditor & solar ROI assistant"),
            ("⚡", "8 Smart Optimizer", "ToU 3-tier tariff arbitrage & solar microgrid"),
            ("👁️", "9 Vision Sentinel", "Edge AI occupancy detection & waste auto-cutoff"),
        ]
        for icon, name, tooltip in nav_items:
            st.markdown(
                f"<div title='{tooltip}' style='padding:0.25rem 0; font-size:0.85rem; color:#cbd5e1'>"
                f"{icon} &nbsp;{name}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Data provenance — shows this is real, traceable data
        try:
            df = load_and_clean_data()
            n_records = f"{len(df):,}"
            date_from = df.index[0].strftime('%b %Y')
            date_to = df.index[-1].strftime('%b %Y')
            st.markdown(
                f"<div style='font-size:0.72rem; color:#334155; text-align:center; "
                f"background:rgba(0,212,255,0.04); border:1px solid rgba(0,212,255,0.1); "
                f"border-radius:8px; padding:0.6rem 0.5rem; margin-top:0.5rem'>"
                f"<div style='color:#475569; font-weight:600; margin-bottom:0.3rem'>📡 Data Source</div>"
                f"<div style='color:#00d4ff'>UCI Household Power</div>"
                f"<div style='color:#475569; margin-top:0.2rem'>{n_records} hourly records</div>"
                f"<div style='color:#475569'>{date_from} → {date_to}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        except Exception:
            pass

        st.markdown(
            "<div style='position:absolute;bottom:1rem;width:100%;text-align:center;"
            "font-size:0.7rem;color:#334155'>v2.0.0 · 100% Software Simulated</div>",
            unsafe_allow_html=True,
        )


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

def main() -> None:
    inject_global_css()
    render_sidebar()

    # Landing content when accessed directly (not via page routing)
    st.markdown(
        """
        <div class='page-title'>🏠 Smart Home Utility AI</div>
        <div class='page-subtitle'>Autonomous Machine Learning & Real-Time Smart Home Digital Twin · 100% Software Demonstration</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style='background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.25); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;'>
            <div style='font-size: 1.2rem; font-weight: 700; color: #00d4ff; margin-bottom: 0.5rem;'>
                🎯 Comprehensive Academic & Viva Demonstration Suite
            </div>
            <p style='color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1rem;'>
                This project is a <b>100% software-based</b>, interactive smart home energy and water intelligence platform.
                It requires zero physical IoT hardware and features real-time digital twin emulation, machine learning forecasting,
                SHAP explainability, Time-of-Use tariff optimization, and edge computer vision.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Category Cards
    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        st.markdown(
            """
            <div class='kpi-card'>
                <div class='kpi-title'>📊 Descriptive & Predictive AI</div>
                <ul style='color:#cbd5e1; font-size:0.85rem; padding-left:1.2rem; line-height:1.9;'>
                    <li><b>1. Overview:</b> Metrology KPIs, gauges & official Energy Star Certificate.</li>
                    <li><b>2. Deep Analysis:</b> Heatmaps, sub-meter correlations & calendar patterns.</li>
                    <li><b>3. Forecast:</b> LightGBM 24/48/72h predictions with 95% confidence bands & SHAP.</li>
                    <li><b>4. Alerts & Tips:</b> Isolation Forest anomaly detection & ranked recommendations.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_c2:
        st.markdown(
            """
            <div class='kpi-card'>
                <div class='kpi-title'>🕹️ Real-Time Simulation & Self-Healing</div>
                <ul style='color:#cbd5e1; font-size:0.85rem; padding-left:1.2rem; line-height:1.9;'>
                    <li><b>5. Live Replay:</b> Hourly streaming historical replayer with water leak detection.</li>
                    <li><b>6. Digital Twin & Fault Studio:</b> Interactive appliance matrix, live electrical telemetry, <b>software fault injection</b> (AC seizure, water burst, vampire drain) & 1-click self-healing auto-mitigation.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_c3:
        st.markdown(
            """
            <div class='kpi-card'>
                <div class='kpi-title'>🧠 Autonomous Decision & Multi-Modal AI</div>
                <ul style='color:#cbd5e1; font-size:0.85rem; padding-left:1.2rem; line-height:1.9;'>
                    <li><b>7. Energy Copilot:</b> Conversational AI auditor answering natural language viva queries with instant numerical calculations.</li>
                    <li><b>8. Smart Optimizer:</b> 3-Tier Time-of-Use (ToU) load shifting & 24h Solar Microgrid dispatch.</li>
                    <li><b>9. Vision Sentinel:</b> OpenCV room occupancy detection with automated empty-room waste cutoff.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Pre-load data in background (triggers cache population with spinners)
    with st.spinner("🔄 Initialising AI systems…"):
        try:
            load_and_clean_data()
            load_water_data(0)
            load_features()
            load_forecast_engine()
            load_anomaly_engine()
            st.success("✅ All systems ready! Use the sidebar to navigate.")
        except Exception as e:
            st.error(f"⚠️ Initialisation error: {e}")
            st.info("Check your internet connection (required for first-time dataset download).")


if __name__ == "__main__":
    main()
