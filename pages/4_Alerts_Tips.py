"""
Page 4: Alerts & Tips
======================
Anomaly severity table with filter badges, anomaly timeline chart,
ranked recommendation cards with savings badges, and CO₂ offset visualisation.
"""

from __future__ import annotations

import sys
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import (
    inject_global_css,
    load_and_clean_data,
    load_water_data,
    load_config_cached,
    get_anomaly_results,
    render_sidebar,
)
from src.recommendations import RecommendationEngine
from src.co2_calculator import CO2Calculator

st.set_page_config(page_title="Alerts & Tips · Smart Home AI", page_icon="🚨", layout="wide")
inject_global_css()
render_sidebar()

cfg = load_config_cached()
df = load_and_clean_data()
water_df = load_water_data(0)

co2_calc = CO2Calculator(cfg)
co2_data = co2_calc.calculate(df)

st.markdown(
    "<div class='page-title'>🚨 Alerts & Tips</div>"
    "<div class='page-subtitle'>Anomalies detected across energy and water usage, plus AI-generated savings recommendations</div>",
    unsafe_allow_html=True,
)

# ─── Load anomalies ─────────────────────────────────────────────────────────────
with st.spinner("Running anomaly detection…"):
    anom_df = get_anomaly_results()

anomalies = anom_df[anom_df["is_anomaly"] == True].copy()

# ─── Summary KPI row ───────────────────────────────────────────────────────────
total = len(anomalies)
n_crit = (anomalies["severity"] == "critical").sum()
n_warn = (anomalies["severity"] == "warning").sum()
n_info = (anomalies["severity"] == "info").sum()

k1, k2, k3, k4 = st.columns(4)

def anom_kpi(col, emoji, label, val, badge_class):
    col.markdown(
        f"<div class='kpi-card'>"
        f"<div class='kpi-title'>{emoji} {label}</div>"
        f"<div class='kpi-value' style='font-size:2rem'>{val}</div>"
        f"<div class='kpi-badge {badge_class}' style='margin-top:0.5rem'>{badge_class.upper()}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

anom_kpi(k1, "⚠️", "Total Anomalies", total, "warn")
anom_kpi(k2, "🔴", "Critical", n_crit, "bad")
anom_kpi(k3, "🟡", "Warnings", n_warn, "warn")
anom_kpi(k4, "🔵", "Info", n_info, "good")

# ─── Anomaly timeline ─────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Anomaly Timeline</div>", unsafe_allow_html=True)

color_map = {"critical": "#ff4444", "warning": "#ffaa00", "info": "#00d4ff"}
size_map = {"critical": 14, "warning": 10, "info": 7}

fig_timeline = go.Figure()

# Background consumption
if "actual" in anom_df.columns:
    base_series = anom_df["actual"].dropna()
else:
    base_series = df["Global_active_power"].reindex(anom_df.index)

fig_timeline.add_trace(go.Scatter(
    x=base_series.index, y=base_series.values,
    mode="lines",
    line=dict(color="rgba(0,212,255,0.3)", width=1),
    name="Consumption",
    hoverinfo="skip",
))

# Anomaly scatter by severity
for sev in ["info", "warning", "critical"]:
    mask = anomalies["severity"] == sev
    sub = anomalies[mask]
    if len(sub) == 0:
        continue
    y_vals = sub.get("actual", sub.get("iso_score", pd.Series(dtype=float)))
    if y_vals is None or len(y_vals) == 0:
        continue
    fig_timeline.add_trace(go.Scatter(
        x=sub.index, y=y_vals.reindex(sub.index).fillna(0),
        mode="markers",
        marker=dict(
            color=color_map[sev],
            size=size_map[sev],
            symbol="circle",
            line=dict(color="rgba(0,0,0,0.5)", width=1),
        ),
        name=sev.capitalize(),
        hovertemplate=f"<b>%{{x}}</b><br>Severity: {sev}<br>Value: %{{y:.3f}} kW<extra></extra>",
    ))

fig_timeline.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="kW"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    height=340, margin=dict(l=10, r=10, t=30, b=10), font=dict(color="#e2e8f0"),
    hovermode="x unified",
)
st.plotly_chart(fig_timeline, use_container_width=True)

# ─── Anomaly filter + table ────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Anomaly Log</div>", unsafe_allow_html=True)

col_sev_filter, col_count = st.columns([2, 1])
with col_sev_filter:
    sev_filter = st.multiselect(
        "Filter by severity",
        options=["critical", "warning", "info"],
        default=["critical", "warning"],
        key="anom_sev_filter",
    )
with col_count:
    max_rows = st.number_input("Max rows", 10, 500, 50, step=10, key="anom_max_rows")

filtered = anomalies[anomalies["severity"].isin(sev_filter)].tail(int(max_rows))

if len(filtered) > 0:
    display_cols = []
    rename_map = {}
    for col in ["actual", "predicted", "z_score", "iso_score", "water_usage", "severity"]:
        if col in filtered.columns:
            display_cols.append(col)
            rename_map[col] = col.replace("_", " ").title()

    table_df = filtered[display_cols].copy()
    table_df.index = filtered.index.strftime("%Y-%m-%d %H:%M")
    table_df = table_df.rename(columns=rename_map)

    def colour_severity(val):
        c = {"Critical": "#ff4444", "Warning": "#ffaa00", "Info": "#00d4ff"}.get(str(val).capitalize(), "")
        return f"color: {c}; font-weight: 600" if c else ""

    styled = table_df.style.map(colour_severity, subset=["Severity"]).format(
        {col: "{:.4f}" for col in table_df.columns if col != "Severity"}
    )
    st.dataframe(styled, use_container_width=True, height=320)
else:
    st.info("No anomalies match the selected severity filter.")

# ─── Recommendations ──────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>💡 Savings Recommendations</div>", unsafe_allow_html=True)

rec_engine = RecommendationEngine(cfg)
recs = rec_engine.generate(df)

col_sort = st.selectbox(
    "Sort by",
    ["Priority Score", "Monthly Savings (₹)", "CO₂ Saved (kg)"],
    key="rec_sort",
)
sort_key_map = {
    "Priority Score": "priority_score",
    "Monthly Savings (₹)": "estimated_monthly_saving_inr",
    "CO₂ Saved (kg)": "estimated_co2_saved_kg",
}
recs = sorted(recs, key=lambda r: getattr(r, sort_key_map[col_sort]), reverse=True)

total_saving = sum(r.estimated_monthly_saving_inr for r in recs)
total_co2_saved = sum(r.estimated_co2_saved_kg for r in recs)

ts1, ts2 = st.columns(2)
ts1.markdown(
    f"<div class='kpi-card'><div class='kpi-title'>💰 Max Potential Saving</div>"
    f"<div class='kpi-value'>₹{total_saving:,.0f}</div>"
    f"<div class='kpi-sub'>per month if all recommendations applied</div></div>",
    unsafe_allow_html=True,
)
ts2.markdown(
    f"<div class='kpi-card'><div class='kpi-title'>🌱 CO₂ Reduction Potential</div>"
    f"<div class='kpi-value'>{total_co2_saved:.0f} kg</div>"
    f"<div class='kpi-sub'>CO₂ saved per month</div></div>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

for rec in recs:
    priority_bar = int(rec.priority_score)
    bar_color = (
        "#ff4444" if priority_bar >= 80
        else "#ffaa00" if priority_bar >= 60
        else "#00d4ff"
    )
    evidence_html = (
        f"<div style='font-size:0.75rem; color:#475569; margin-top:0.4rem'>📊 {rec.evidence}</div>"
        if rec.evidence
        else ""
    )
    st.markdown(
        f"""
        <div class='rec-card'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start'>
                <div>
                    <span style='font-size:1.5rem'>{rec.icon}</span>
                    <span style='font-size:1rem; font-weight:600; color:#e2e8f0; margin-left:0.5rem'>{rec.title}</span>
                    <span style='font-size:0.75rem; color:#475569; margin-left:0.5rem; background:rgba(255,255,255,0.06);
                           padding:0.15rem 0.5rem; border-radius:999px'>{rec.category}</span>
                </div>
                <div style='text-align:right'>
                    <div class='rec-saving'>₹{rec.estimated_monthly_saving_inr:,}/mo</div>
                    <div class='rec-co2'>🌱 {rec.estimated_co2_saved_kg:.1f} kg CO₂ saved</div>
                </div>
            </div>
            <p style='color:#94a3b8; font-size:0.87rem; margin-top:0.6rem; line-height:1.6'>{rec.description}</p>
            <div style='margin-top:0.5rem'>
                <div style='font-size:0.7rem; color:#475569; margin-bottom:0.2rem'>Priority: {priority_bar}/100</div>
                <div style='background:rgba(255,255,255,0.07); border-radius:999px; height:5px; overflow:hidden'>
                    <div style='width:{priority_bar}%; height:100%; background:{bar_color}; border-radius:999px'></div>
                </div>
            </div>
            {evidence_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── CO₂ offset visualisation ─────────────────────────────────────────────────
st.markdown("<div class='section-header'>CO₂ Offset Potential</div>", unsafe_allow_html=True)

monthly_co2 = co2_data["monthly_co2_kg"]
reducible_co2 = min(total_co2_saved, monthly_co2)

fig_co2 = go.Figure(go.Bar(
    x=["Current Footprint", "After Recommendations"],
    y=[monthly_co2, max(0, monthly_co2 - reducible_co2)],
    marker_color=["#ff4444", "#00ff88"],
    text=[f"{monthly_co2:.0f} kg", f"{max(0, monthly_co2 - reducible_co2):.0f} kg"],
    textposition="outside",
    textfont=dict(color="#e2e8f0"),
    width=0.4,
))
fig_co2.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="kg CO₂ / month"),
    height=300, margin=dict(l=10, r=10, t=30, b=10), font=dict(color="#e2e8f0"),
    title=dict(text="Monthly CO₂ Reduction Potential", font=dict(color="#94a3b8", size=13)),
)
st.plotly_chart(fig_co2, use_container_width=True)
