"""
Page 8: Smart Grid ToU & Microgrid Optimizer
============================================
Time-of-Use (ToU) 3-tier tariff arbitrage, peak demand shaving,
and 24-hour Rooftop Solar PV + Battery Storage (BESS) dispatch simulation.
100% software-based algorithmic optimization.
"""

from __future__ import annotations

import sys
sys.path.insert(0, ".")

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from app import (
    inject_global_css,
    load_config_cached,
    render_sidebar,
)
from src.optimizer import DeferrableTask, SmartGridOptimizer

st.set_page_config(
    page_title="Smart Optimizer · Smart Home AI",
    page_icon="⚡",
    layout="wide",
)
inject_global_css()
render_sidebar()

cfg = load_config_cached()
opt = SmartGridOptimizer(cfg)

st.markdown(
    """
    <div class='page-title'>⚡ Smart Grid ToU & Microgrid Optimizer</div>
    <div class='page-subtitle'>
        Dynamic 3-Tier Tariff Load Shifting · Peak Shaving & 24h Rooftop Solar + Battery Dispatch
    </div>
    """,
    unsafe_allow_html=True,
)

tab_tou, tab_solar = st.tabs([
    "⏰ Time-of-Use (ToU) Load Shifter",
    "☀️ Solar PV + Battery (BESS) Microgrid",
])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1: TIME-OF-USE (ToU) LOAD SHIFTING
# ────────────────────────────────────────────────────────────────────────────
with tab_tou:
    st.markdown("<div class='section-header'>Tariff Windows & Flexible Load Selection</div>", unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)
    t1.markdown(
        """
        <div style='background:rgba(255,68,68,0.08); border:1px solid rgba(255,68,68,0.3); border-radius:10px; padding:0.8rem;'>
            <div style='color:#ff4444; font-weight:700; font-size:0.85rem;'>🔴 PEAK EVENING (18:00 – 22:00)</div>
            <div style='font-size:1.4rem; font-weight:800; color:#ff4444;'>₹9.50 / kWh</div>
            <div style='font-size:0.75rem; color:#94a3b8;'>Highest grid congestion & peak demand charge</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    t2.markdown(
        """
        <div style='background:rgba(255,170,0,0.08); border:1px solid rgba(255,170,0,0.3); border-radius:10px; padding:0.8rem;'>
            <div style='color:#ffaa00; font-weight:700; font-size:0.85rem;'>🟡 STANDARD DAY (06:00 – 18:00)</div>
            <div style='font-size:1.4rem; font-weight:800; color:#ffaa00;'>₹6.50 / kWh</div>
            <div style='font-size:0.75rem; color:#94a3b8;'>Normal commercial and residential tariff</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    t3.markdown(
        """
        <div style='background:rgba(0,255,136,0.08); border:1px solid rgba(0,255,136,0.3); border-radius:10px; padding:0.8rem;'>
            <div style='color:#00ff88; font-weight:700; font-size:0.85rem;'>🟢 SUPER OFF-PEAK (22:00 – 06:00)</div>
            <div style='font-size:1.4rem; font-weight:800; color:#00ff88;'>₹3.50 / kWh</div>
            <div style='font-size:0.75rem; color:#94a3b8;'>63% cheaper than peak! Optimal for deferrable loads</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<b>Select Flexible Loads to Optimize:</b>", unsafe_allow_html=True)
    c_tsk1, c_tsk2, c_tsk3, c_tsk4 = st.columns(4)

    tasks_to_run = []
    with c_tsk1:
        if st.checkbox("🚗 EV Charger (3.3 kW, 4h)", value=True, key="chk_ev"):
            tasks_to_run.append(DeferrableTask("EV Charger", 4, 3.3, 18, 7))
    with c_tsk2:
        if st.checkbox("🧺 Washing Machine (1.2 kW, 2h)", value=True, key="chk_wm"):
            tasks_to_run.append(DeferrableTask("Washing Machine", 2, 1.2, 19, 23))
    with c_tsk3:
        if st.checkbox("🍽️ Dishwasher (1.1 kW, 2h)", value=True, key="chk_dw"):
            tasks_to_run.append(DeferrableTask("Dishwasher", 2, 1.1, 20, 24))
    with c_tsk4:
        if st.checkbox("🚿 Water Pre-Heat (2.2 kW, 1h)", value=True, key="chk_geyser"):
            tasks_to_run.append(DeferrableTask("Water Pre-Heat", 1, 2.2, 18, 22))

    res = opt.optimize_appliance_schedule(tasks_to_run)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Unmanaged Cost</div>
            <div class='kpi-value' style='font-size:1.8rem; color:#ff4444;'>₹{res['unmanaged_cost_day']:.1f}</div>
            <div class='kpi-sub'>Per Day (Peak Heavy)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    m2.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Optimized Cost</div>
            <div class='kpi-value' style='font-size:1.8rem; color:#00ff88;'>₹{res['optimized_cost_day']:.1f}</div>
            <div class='kpi-sub'>Per Day (Off-Peak Shifted)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    m3.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Monthly Savings</div>
            <div class='kpi-value' style='font-size:1.8rem; color:#00d4ff;'>₹{res['savings_month']:,.0f}</div>
            <div class='kpi-sub'>{res['savings_pct']:.1f}% Bill Reduction</div>
            <div class='kpi-badge good'>AI OPTIMIZED</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    m4.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Peak Grid Shaving</div>
            <div class='kpi-value' style='font-size:1.8rem; color:#7b5ea7;'>-{res['peak_reduction_pct']:.1f}%</div>
            <div class='kpi-sub'>{res['peak_kw_unmanaged']:.1f} kW → {res['peak_kw_optimized']:.1f} kW</div>
            <div class='kpi-badge good'>GRID FRIENDLY</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Comparison 24h Chart
    st.markdown("<div class='section-header'>24-Hour Load Profile: Unmanaged vs. AI-Optimized</div>", unsafe_allow_html=True)

    hours = list(range(24))
    hour_labels = [f"{h:02d}:00" for h in hours]

    fig_tou = go.Figure()

    # Tariff shading bands
    fig_tou.add_vrect(x0=18, x1=22, fillcolor="rgba(255, 68, 68, 0.08)", layer="below", line_width=0, annotation_text="Peak Window (₹9.50/kWh)", annotation_position="top left", annotation_font_color="#ff4444")
    fig_tou.add_vrect(x0=22, x1=23.9, fillcolor="rgba(0, 255, 136, 0.06)", layer="below", line_width=0, annotation_text="Super Off-Peak (₹3.50)", annotation_position="top left", annotation_font_color="#00ff88")
    fig_tou.add_vrect(x0=0, x1=6, fillcolor="rgba(0, 255, 136, 0.06)", layer="below", line_width=0)

    # Unmanaged curve
    fig_tou.add_trace(go.Scatter(
        x=hours, y=res["unmanaged_load"],
        mode="lines+markers",
        line=dict(color="#ff4444", width=2.5, dash="dot"),
        name="Unmanaged Demand (Baseline)",
        hovertemplate="<b>%{x}:00</b><br>Unmanaged: %{y:.2f} kW<extra></extra>",
    ))

    # Optimized curve
    fig_tou.add_trace(go.Scatter(
        x=hours, y=res["optimized_load"],
        mode="lines+markers",
        line=dict(color="#00d4ff", width=3),
        fill="tozeroy",
        fillcolor="rgba(0, 212, 255, 0.08)",
        name="AI-Optimized Demand (Shifted)",
        hovertemplate="<b>%{x}:00</b><br>Optimized: %{y:.2f} kW<extra></extra>",
    ))

    fig_tou.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickmode="array", tickvals=hours, ticktext=hour_labels, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Active Power (kW)", color="#94a3b8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
        height=380,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig_tou, use_container_width=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2: SOLAR MICROGRID & BATTERY STORAGE (BESS)
# ────────────────────────────────────────────────────────────────────────────
with tab_solar:
    st.markdown("<div class='section-header'>Microgrid System Sizing & Parameters</div>", unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        pv_size = st.slider("☀️ Rooftop Solar Capacity (kWp)", 1.0, 10.0, 4.5, 0.5, key="pv_size_sld")
    with col_s2:
        batt_size = st.slider("🔋 Home Battery Capacity (kWh)", 2.0, 20.0, 10.0, 1.0, key="batt_size_sld")
    with col_s3:
        fit_rate = st.slider("💸 Feed-in Export Tariff (₹/kWh)", 2.0, 6.0, 4.20, 0.1, key="fit_rate_sld")

    sim_res = opt.simulate_microgrid_24h(
        solar_pv_kwp=pv_size,
        battery_capacity_kwh=batt_size,
        feed_in_tariff=fit_rate,
    )

    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Daily Solar Generated</div>
            <div class='kpi-value' style='font-size:1.8rem; color:#ffaa00;'>{sim_res['total_solar_kwh']:.1f} kWh</div>
            <div class='kpi-sub'>Clean Local Energy</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    sm2.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Self-Sufficiency</div>
            <div class='kpi-value' style='font-size:1.8rem; color:#00ff88;'>{sim_res['self_sufficiency_pct']:.1f}%</div>
            <div class='kpi-sub'>Grid Independence</div>
            <div class='kpi-badge good'>MICROGRID ACTIVE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    sm3.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Monthly Net Savings</div>
            <div class='kpi-value' style='font-size:1.8rem; color:#00d4ff;'>₹{sim_res['monthly_savings']:,.0f}</div>
            <div class='kpi-sub'>Displaced Bill + Exports</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    sm4.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-title'>Daily CO₂ Avoided</div>
            <div class='kpi-value' style='font-size:1.8rem; color:#7b5ea7;'>{sim_res['co2_avoided_kg']:.1f} kg</div>
            <div class='kpi-sub'>~{sim_res['co2_avoided_kg']*30/22:.1f} Trees Equivalent</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 24-Hour Microgrid Power Flows
    st.markdown("<div class='section-header'>24-Hour Microgrid Energy Balance & Battery Dispatch</div>", unsafe_allow_html=True)

    fig_micro = go.Figure()

    # Solar PV Area
    fig_micro.add_trace(go.Scatter(
        x=sim_res["hours"], y=sim_res["solar_profile"],
        mode="lines",
        line=dict(color="#ffaa00", width=2),
        fill="tozeroy",
        fillcolor="rgba(255, 170, 0, 0.12)",
        name="☀️ Solar PV Generation (kW)",
    ))

    # Home Load Demand Line
    fig_micro.add_trace(go.Scatter(
        x=sim_res["hours"], y=sim_res["load_profile"],
        mode="lines",
        line=dict(color="#00d4ff", width=2.5),
        name="⚡ Household Demand (kW)",
    ))

    # Grid Import (Red bars)
    fig_micro.add_trace(go.Bar(
        x=sim_res["hours"], y=sim_res["grid_import"],
        marker_color="rgba(255, 68, 68, 0.5)",
        name="🔌 Grid Import (kW)",
    ))

    # Grid Export (Green bars)
    fig_micro.add_trace(go.Bar(
        x=sim_res["hours"], y=sim_res["grid_export"],
        marker_color="rgba(0, 255, 136, 0.5)",
        name="⚡ Grid Feed-In Export (kW)",
    ))

    # Battery SoC (%) on secondary y-axis
    fig_micro.add_trace(go.Scatter(
        x=sim_res["hours"], y=sim_res["soc_pct_curve"],
        mode="lines",
        line=dict(color="#00ff88", width=1.5, dash="dot"),
        name="🔋 Battery State of Charge (%)",
        yaxis="y2",
    ))

    fig_micro.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickmode="array", tickvals=hours, ticktext=hour_labels, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Power (kW)", color="#94a3b8"),
        yaxis2=dict(title="Battery SoC (%)", overlaying="y", side="right", range=[0, 105], showgrid=False, color="#00ff88"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig_micro, use_container_width=True)
