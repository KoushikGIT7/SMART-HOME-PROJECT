"""
Page 5: Live Replay + Water Module
=====================================
Simulates real-time hourly streaming of historical data.
Controls: Play/Pause, Speed (1×/2×/5×/10×), Timeline slider.
Shows live energy line chart + water anomaly indicator.
"""

from __future__ import annotations

import sys
sys.path.insert(0, ".")

import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import (
    inject_global_css,
    load_and_clean_data,
    load_water_data,
    load_config_cached,
    render_sidebar,
)
from src.replay_simulator import ReplaySimulator

st.set_page_config(page_title="Live Replay · Smart Home AI", page_icon="🎬", layout="wide")
inject_global_css()
render_sidebar()

cfg = load_config_cached()
df = load_and_clean_data()
water_df = load_water_data(0)

# Merge energy + water
combined = df[["Global_active_power", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3"]].copy()
combined["water_usage_litres"] = water_df["water_usage_litres"].reindex(combined.index)
combined["water_leak_flag"] = water_df["water_leak_flag"].reindex(combined.index).fillna(False)

st.markdown(
    "<div class='page-title'>🎬 Live Replay Simulator</div>"
    "<div class='page-subtitle'>Stream historical data in real-time — watch energy and water usage unfold hour by hour</div>",
    unsafe_allow_html=True,
)

# ─── Replay controls ────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Playback Controls</div>", unsafe_allow_html=True)

sim = ReplaySimulator(combined, window_hours=72)
sim.render_controls()

# Reset button
if st.button("⏮️ Reset to Start", key="replay_reset_btn"):
    sim.reset()
    st.rerun()

# ─── Current timestamp display ──────────────────────────────────────────────────
current_ts = sim.get_timestamp()
is_playing = st.session_state.get("replay_playing", False)

live_dot = "<span class='live-indicator'></span>" if is_playing else ""
st.markdown(
    f"<div style='font-size:0.9rem; color:#64748b; margin: 0.5rem 0'>"
    f"{live_dot}<b style='color:#e2e8f0'>Current time:</b> "
    f"<span style='color:#00d4ff'>{current_ts.strftime('%A, %d %b %Y — %H:%M')}</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ─── Get current window ─────────────────────────────────────────────────────────
window = sim.current_window()

# ─── Live metric row ────────────────────────────────────────────────────────────
if len(window) > 0:
    latest = window.iloc[-1]
    current_kw = float(latest.get("Global_active_power", 0))
    current_water = float(latest.get("water_usage_litres", 0))
    water_leak = bool(latest.get("water_leak_flag", False))
    sm1 = float(latest.get("Sub_metering_1", 0))
    sm2 = float(latest.get("Sub_metering_2", 0))
    sm3 = float(latest.get("Sub_metering_3", 0))

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>⚡ Live Load</div>"
        f"<div class='kpi-value'>{current_kw:.3f}</div>"
        f"<div class='kpi-sub'>kW active power</div></div>",
        unsafe_allow_html=True,
    )
    m2.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>🍳 Kitchen (SM1)</div>"
        f"<div class='kpi-value'>{sm1:.0f}</div>"
        f"<div class='kpi-sub'>Wh this hour</div></div>",
        unsafe_allow_html=True,
    )
    m3.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>🧺 Laundry (SM2)</div>"
        f"<div class='kpi-value'>{sm2:.0f}</div>"
        f"<div class='kpi-sub'>Wh this hour</div></div>",
        unsafe_allow_html=True,
    )
    m4.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>❄️ HVAC (SM3)</div>"
        f"<div class='kpi-value'>{sm3:.0f}</div>"
        f"<div class='kpi-sub'>Wh this hour</div></div>",
        unsafe_allow_html=True,
    )

    leak_color = "#ff4444" if water_leak else "#00ff88"
    leak_text = "🚨 LEAK DETECTED" if water_leak else "✅ Normal"
    m5.markdown(
        f"<div class='kpi-card' style='border-color:{leak_color}40'>"
        f"<div class='kpi-title'>💧 Water</div>"
        f"<div class='kpi-value' style='font-size:1.5rem; color:{leak_color}'>{current_water:.1f}</div>"
        f"<div class='kpi-sub'>L this hour</div>"
        f"<div class='kpi-badge {'bad' if water_leak else 'good'}'>{leak_text}</div></div>",
        unsafe_allow_html=True,
    )
    if water_leak:
        st.markdown(
            """
            <script>
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(659, ctx.currentTime);
                osc.frequency.setValueAtTime(523, ctx.currentTime + 0.12);
                gain.gain.setValueAtTime(0.06, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.3);
            } catch(e) {}
            </script>
            """,
            unsafe_allow_html=True,
        )

# ─── Live energy chart ──────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Live Energy Stream</div>", unsafe_allow_html=True)

fig_live = go.Figure()

if len(window) > 0:
    # Main active power line
    fig_live.add_trace(go.Scatter(
        x=window.index, y=window["Global_active_power"],
        mode="lines",
        line=dict(color="#00d4ff", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.07)",
        name="Active Power (kW)",
        hovertemplate="<b>%{x}</b><br>%{y:.3f} kW<extra></extra>",
    ))

    # Sub-meters (normalised to kW scale for visibility)
    sm_data = {
        "Sub_metering_1": ("🍳 Kitchen", "#ffaa00"),
        "Sub_metering_2": ("🧺 Laundry", "#7b5ea7"),
        "Sub_metering_3": ("❄️ HVAC", "#00ff88"),
    }
    for sm_col, (sm_label, sm_color) in sm_data.items():
        if sm_col in window.columns:
            sm_kw = window[sm_col] / 1000.0  # Wh → kWh ≈ kW for hourly
            fig_live.add_trace(go.Scatter(
                x=window.index, y=sm_kw,
                mode="lines",
                line=dict(color=sm_color, width=1, dash="dot"),
                name=sm_label,
                hovertemplate=f"<b>%{{x}}</b><br>{sm_label}: %{{y:.3f}} kW<extra></extra>",
            ))

    # Highlight leak points
    leak_mask = window["water_leak_flag"].fillna(False)
    if leak_mask.any():
        leak_window = window[leak_mask]
        fig_live.add_trace(go.Scatter(
            x=leak_window.index,
            y=leak_window["Global_active_power"],
            mode="markers",
            marker=dict(color="#ff4444", size=10, symbol="x", line=dict(width=2, color="#ff0000")),
            name="⚠️ Water Leak",
            hovertemplate="<b>%{x}</b><br>⚠️ Leak detected<extra></extra>",
        ))

    # Mark latest point with a dot
    fig_live.add_trace(go.Scatter(
        x=[window.index[-1]],
        y=[window["Global_active_power"].iloc[-1]],
        mode="markers",
        marker=dict(color="#00ff88", size=12, symbol="circle", line=dict(width=2, color="#00d4ff")),
        name="▶ Now",
        showlegend=True,
    ))

fig_live.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="kW"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    height=380, margin=dict(l=10, r=10, t=40, b=10), font=dict(color="#e2e8f0"),
    hovermode="x unified",
    transition=dict(duration=300, easing="cubic-in-out"),
)
st.plotly_chart(fig_live, use_container_width=True, key=f"live_chart_{st.session_state.get('replay_idx', 0)}")

# ─── Live water chart ───────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Live Water Stream</div>", unsafe_allow_html=True)

fig_water = go.Figure()
if len(window) > 0 and "water_usage_litres" in window.columns:
    water_values = window["water_usage_litres"].fillna(0)
    leak_flags = window["water_leak_flag"].fillna(False)

    fig_water.add_trace(go.Bar(
        x=window.index, y=water_values,
        marker_color=["rgba(255,68,68,0.8)" if leak else "rgba(0,212,255,0.5)" for leak in leak_flags],
        name="Water Usage (L)",
        hovertemplate="<b>%{x}</b><br>%{y:.1f} L<extra></extra>",
    ))

fig_water.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="Litres"),
    legend=dict(orientation="h", bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    height=260, margin=dict(l=10, r=10, t=20, b=10), font=dict(color="#e2e8f0"),
    title=dict(text="🔴 Red bars = Water leak anomaly", font=dict(color="#94a3b8", size=12)),
)
st.plotly_chart(fig_water, use_container_width=True, key=f"water_chart_{st.session_state.get('replay_idx', 0)}")

# ─── Advance replay if playing ──────────────────────────────────────────────────
if sim.advance():
    speed = st.session_state.get("replay_speed", 1)
    delay = max(0.05, 0.8 / speed)   # 1×→0.8s, 2×→0.4s, 5×→0.16s, 10×→0.08s
    time.sleep(delay)
    st.rerun()
elif is_playing:
    st.session_state["replay_playing"] = False
    st.success("✅ Replay complete! Press ▶️ to restart or drag the timeline slider.")
