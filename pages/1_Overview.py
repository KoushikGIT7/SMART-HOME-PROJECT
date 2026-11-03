"""
Page 1: Overview
=================
KPI cards, animated gauges, 30-day trend sparkline, and water summary.
"""

from __future__ import annotations

import sys
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# Re-use cached loaders from app.py
from app import (
    inject_global_css,
    load_and_clean_data,
    load_water_data,
    load_config_cached,
    get_forecast_results,
    render_sidebar,
)
from src.bill_estimator import BillEstimator
from src.co2_calculator import CO2Calculator
from src.report_generator import EnergyAuditReportGenerator

st.set_page_config(page_title="Overview · Smart Home AI", page_icon="🏠", layout="wide")
inject_global_css()
render_sidebar()

# ─── Load data ───────────────────────────────────────────────────────────────
cfg = load_config_cached()
df = load_and_clean_data()
water_df = load_water_data(0)

bill_est = BillEstimator(cfg)
co2_calc = CO2Calculator(cfg)

bill_data = bill_est.estimate(df, water_df)
co2_data = co2_calc.calculate(df)

_, future_fc = get_forecast_results()

# Last 30 days
last30 = df[df.index >= df.index[-1] - pd.Timedelta(days=30)]

# ─── Page header ─────────────────────────────────────────────────────────────
st.markdown(
    "<div class='page-title'>🏠 Overview</div>"
    "<div class='page-subtitle'>Your home's energy health at a glance</div>",
    unsafe_allow_html=True,
)

# ─── KPI Cards (row 1) ────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

# ─── Compute real month-over-month delta ──────────────────────────────────────
avg_daily_kwh = df["Global_active_power"].mean() * 24
monthly_kwh = bill_data["monthly_kwh"]
monthly_bill = bill_data["monthly_bill_inr"]
monthly_co2 = co2_data["monthly_co2_kg"]

# Real MoM delta: compare last 30 days vs prior 30 days
_now = df.index[-1]
_cur30 = df[df.index >= _now - pd.Timedelta(days=30)]["Global_active_power"].mean()
_prev30 = df[
    (df.index >= _now - pd.Timedelta(days=60)) &
    (df.index < _now - pd.Timedelta(days=30))
]["Global_active_power"].mean()
_mom_pct = ((_cur30 - _prev30) / _prev30 * 100) if _prev30 and _prev30 != 0 else 0.0
_mom_arrow = "▲" if _mom_pct >= 0 else "▼"
_mom_badge = "warn" if _mom_pct >= 0 else "good"
_mom_label = f"{_mom_arrow} {abs(_mom_pct):.1f}% vs prior 30 days"

def kpi_card(col, icon, title, value, sub, badge_text=None, badge_class="good"):
    badge_html = (
        f"<div class='kpi-badge {badge_class}'>{badge_text}</div>"
        if badge_text
        else ""
    )
    col.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>{icon} {title}</div>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-sub'>{sub}</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

kpi_card(c1, "⚡", "Monthly Usage", f"{monthly_kwh:.0f}", "kWh / month",
         _mom_label, _mom_badge)
kpi_card(c2, "💸", "Est. Monthly Bill",
         f"₹{monthly_bill:,.0f}", "incl. fixed charges",
         "BESCOM tiered tariff", "good")
kpi_card(c3, "🌱", "CO₂ Footprint",
         f"{monthly_co2:.0f}", "kg CO₂ / month",
         f"≈ {co2_data['trees_equivalent']:.0f} trees to offset", "warn")
kpi_card(c4, "💧", "Water Bill",
         f"₹{bill_data['water_monthly_bill_inr']:,.0f}", "est. monthly water cost",
         "Est. from usage pattern", "good")

# ─── Row 2: Gauge + Sparkline ─────────────────────────────────────────────────
st.markdown("<div class='section-header'>Current Usage Gauge</div>", unsafe_allow_html=True)

col_gauge, col_spark = st.columns([1, 2])

with col_gauge:
    current_kw = float(df["Global_active_power"].iloc[-1])
    max_kw = float(df["Global_active_power"].quantile(0.99))
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_kw,
        delta={"reference": df["Global_active_power"].mean(), "suffix": " kW"},
        number={"suffix": " kW", "font": {"color": "#00d4ff", "size": 36}},
        title={"text": "Current Load", "font": {"color": "#94a3b8", "size": 14}},
        gauge={
            "axis": {"range": [0, max_kw], "tickcolor": "#475569"},
            "bar": {"color": "#00d4ff"},
            "bgcolor": "rgba(255,255,255,0.02)",
            "bordercolor": "rgba(0,212,255,0.2)",
            "steps": [
                {"range": [0, max_kw * 0.4], "color": "rgba(0,255,136,0.15)"},
                {"range": [max_kw * 0.4, max_kw * 0.75], "color": "rgba(255,170,0,0.15)"},
                {"range": [max_kw * 0.75, max_kw], "color": "rgba(255,68,68,0.15)"},
            ],
            "threshold": {
                "line": {"color": "#ff4444", "width": 3},
                "thickness": 0.75,
                "value": max_kw * 0.85,
            },
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    # Real timestamp label — makes clear this is historical data, not live
    st.markdown(
        f"<div style='text-align:center; font-size:0.75rem; color:#475569; margin-top:-0.5rem'>"
        f"📅 Last recorded: <b style='color:#64748b'>{df.index[-1].strftime('%d %b %Y, %H:%M')}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

with col_spark:
    st.markdown("<div class='section-header'>30-Day Energy Trend</div>", unsafe_allow_html=True)
    daily = last30["Global_active_power"].resample("D").mean()
    roll7 = daily.rolling(7, min_periods=1).mean()

    fig_spark = go.Figure()
    fig_spark.add_trace(go.Scatter(
        x=daily.index, y=daily.values,
        mode="lines",
        line=dict(color="rgba(0,212,255,0.4)", width=1),
        name="Daily avg",
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.06)",
    ))
    fig_spark.add_trace(go.Scatter(
        x=roll7.index, y=roll7.values,
        mode="lines",
        line=dict(color="#00d4ff", width=2.5),
        name="7-day avg",
    ))
    if future_fc is not None and len(future_fc) > 0:
        fig_spark.add_trace(go.Scatter(
            x=future_fc.index, y=future_fc["predicted"].values,
            mode="lines",
            line=dict(color="#7b5ea7", width=2, dash="dash"),
            name="Forecast",
        ))
    fig_spark.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color="#475569"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="kW"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#e2e8f0"),
        hovermode="x unified",
    )
    st.plotly_chart(fig_spark, use_container_width=True)

# ─── Row 3: Sub-meter pie + Water ─────────────────────────────────────────────
st.markdown("<div class='section-header'>Energy Breakdown & Water Usage</div>", unsafe_allow_html=True)
col_pie, col_water = st.columns(2)

with col_pie:
    bd = bill_data["submeter_breakdown"]
    labels = list(bd.keys())
    values = [v["monthly_kwh"] for v in bd.values()]
    colors = ["#00d4ff", "#7b5ea7", "#00ff88", "#ffaa00"]

    fig_pie = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#0a0e1a", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#e2e8f0", size=12),
        hovertemplate="<b>%{label}</b><br>%{value:.1f} kWh/mo<extra></extra>",
    ))
    fig_pie.add_annotation(
        text=f"<b>{monthly_kwh:.0f}</b><br><span style='font-size:10px'>kWh/mo</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#00d4ff"),
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(orientation="h", bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        height=300,
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(color="#e2e8f0"),
        title=dict(text="Sub-meter Attribution", font=dict(color="#94a3b8", size=13)),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_water:
    _w_daily_full = water_df["water_usage_litres"].resample("D").sum()
    w_daily = _w_daily_full[_w_daily_full.index >= _w_daily_full.index[-1] - pd.Timedelta(days=30)]
    _leak_full = water_df["water_leak_flag"].resample("D").max().astype(bool)
    leak_days = _leak_full[_leak_full.index >= _leak_full.index[-1] - pd.Timedelta(days=30)]

    fig_water = go.Figure()
    fig_water.add_trace(go.Bar(
        x=w_daily.index, y=w_daily.values,
        marker_color=[
            "#ff4444" if leak else "rgba(0,212,255,0.6)"
            for leak in leak_days.reindex(w_daily.index, fill_value=False)
        ],
        name="Daily Water Usage",
        hovertemplate="<b>%{x|%d %b}</b><br>%{y:.0f} L<extra></extra>",
    ))
    fig_water.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color="#475569"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="Litres"),
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#e2e8f0"),
        title=dict(text="Daily Water Consumption (🔴 = Leak detected)", font=dict(color="#94a3b8", size=13)),
    )
    st.plotly_chart(fig_water, use_container_width=True)

# ─── Row 4: CO2 trend ─────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Monthly CO₂ Footprint</div>", unsafe_allow_html=True)
co2_monthly = co2_data["monthly_breakdown"]

fig_co2 = go.Figure()
fig_co2.add_trace(go.Bar(
    x=co2_monthly.index,
    y=co2_monthly["co2_kg"].values,
    marker=dict(
        color=co2_monthly["co2_kg"].values,
        colorscale=[[0, "rgba(0,255,136,0.7)"], [0.5, "rgba(255,170,0,0.7)"], [1, "rgba(255,68,68,0.8)"]],
        showscale=False,
    ),
    name="CO₂ kg",
    hovertemplate="<b>%{x|%b %Y}</b><br>%{y:.1f} kg CO₂<extra></extra>",
))
fig_co2.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="kg CO₂"),
    height=280,
    margin=dict(l=10, r=10, t=20, b=10),
    font=dict(color="#e2e8f0"),
)
st.plotly_chart(fig_co2, use_container_width=True)

# Footer equivalencies
eq1, eq2, eq3 = st.columns(3)
eq1.markdown(
    f"<div class='kpi-card'><div class='kpi-title'>🌳 Trees to Offset</div>"
    f"<div class='kpi-value'>{co2_data['trees_equivalent']:.0f}</div>"
    f"<div class='kpi-sub'>trees needed per year</div></div>",
    unsafe_allow_html=True,
)
eq2.markdown(
    f"<div class='kpi-card'><div class='kpi-title'>🚗 Car Distance Equivalent</div>"
    f"<div class='kpi-value'>{co2_data['car_km_equivalent']:,.0f}</div>"
    f"<div class='kpi-sub'>km driven (petrol car)</div></div>",
    unsafe_allow_html=True,
)
eq3.markdown(
    f"<div class='kpi-card'><div class='kpi-title'>📅 Daily CO₂</div>"
    f"<div class='kpi-value'>{co2_data['daily_co2_kg']:.2f}</div>"
    f"<div class='kpi-sub'>kg CO₂ per day</div></div>",
    unsafe_allow_html=True,
)

# ─── Row 5: Official Energy Audit & Energy Star Certificate ───────────────────
st.markdown("<div class='section-header'>🏛️ Official Energy Audit & Efficiency Certification</div>", unsafe_allow_html=True)
st.caption("Generate and inspect your certified residential efficiency grade and official audit document.")

col_btn1, col_btn2 = st.columns([2, 1])

rep_gen = EnergyAuditReportGenerator(cfg)
cert_html = rep_gen.generate_html_certificate(
    monthly_kwh=monthly_kwh,
    monthly_bill=monthly_bill,
    monthly_co2=monthly_co2,
    water_monthly_l=float(bill_data.get("monthly_water_litres", 4500)),
    anomalies_count=2,
    household_id="SH-AI-2026-8941",
)

with col_btn1:
    show_cert = st.toggle("📜 Display Official Energy Star Audit Certificate", value=True, key="tgl_audit_cert")

with col_btn2:
    st.download_button(
        label="📥 Download Certified Audit Report (HTML)",
        data=cert_html,
        file_name="Smart_Home_Energy_Audit_Certificate.html",
        mime="text/html",
        use_container_width=True,
    )

if show_cert:
    components.html(cert_html, height=620, scrolling=False)
