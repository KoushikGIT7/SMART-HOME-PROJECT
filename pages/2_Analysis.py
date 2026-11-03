"""
Page 2: Analysis
=================
Deep-dive analysis: heatmaps, sub-meter breakdown, correlation matrix,
interactive time-range selector, and aggregation toggle.
"""

from __future__ import annotations

import sys
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from app import inject_global_css, load_and_clean_data, load_config_cached, render_sidebar

st.set_page_config(page_title="Analysis · Smart Home AI", page_icon="🔍", layout="wide")
inject_global_css()
render_sidebar()

# ─── Load ──────────────────────────────────────────────────────────────────────
cfg = load_config_cached()
df = load_and_clean_data()

st.markdown(
    "<div class='page-title'>🔍 Deep Analysis</div>"
    "<div class='page-subtitle'>Explore consumption patterns across time, appliances, and correlations</div>",
    unsafe_allow_html=True,
)

# ─── Filters ───────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Filters</div>", unsafe_allow_html=True)
col_date, col_agg = st.columns([3, 1])

with col_date:
    min_d = df.index.min().date()
    max_d = df.index.max().date()
    date_range = st.date_input(
        "Date Range",
        value=(max_d - pd.Timedelta("90D"), max_d),
        min_value=min_d,
        max_value=max_d,
        key="analysis_date_range",
    )

with col_agg:
    agg_choice = st.selectbox(
        "Aggregation",
        options=["Hourly", "Daily", "Weekly"],
        index=1,
        key="analysis_agg",
    )

# Apply filters
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    mask = (df.index.date >= start) & (df.index.date <= end)
    df_sel = df.loc[mask].copy()
else:
    df_sel = df.copy()

if len(df_sel) == 0:
    st.warning("No data in selected range.")
    st.stop()

freq_map = {"Hourly": "1h", "Daily": "D", "Weekly": "W"}
agg_freq = freq_map[agg_choice]
df_agg = df_sel.resample(agg_freq).mean()

# ─── Section 1: Time-series area chart ─────────────────────────────────────────
st.markdown("<div class='section-header'>Energy Consumption Over Time</div>", unsafe_allow_html=True)

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(
    x=df_agg.index, y=df_agg["Global_active_power"],
    mode="lines",
    line=dict(color="#00d4ff", width=1.5),
    fill="tozeroy",
    fillcolor="rgba(0,212,255,0.08)",
    name="Active Power",
    hovertemplate="<b>%{x}</b><br>%{y:.3f} kW<extra></extra>",
))
if "Global_reactive_power" in df_agg.columns:
    fig_ts.add_trace(go.Scatter(
        x=df_agg.index, y=df_agg["Global_reactive_power"],
        mode="lines",
        line=dict(color="rgba(123,94,167,0.7)", width=1),
        name="Reactive Power",
        hovertemplate="<b>%{x}</b><br>%{y:.3f} kVAR<extra></extra>",
    ))
fig_ts.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="kW / kVAR"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    height=320, margin=dict(l=10, r=10, t=30, b=10), font=dict(color="#e2e8f0"),
    hovermode="x unified",
)
st.plotly_chart(fig_ts, use_container_width=True)

# ─── Section 2: Heatmap (hour × weekday) ───────────────────────────────────────
st.markdown("<div class='section-header'>Consumption Heatmap (Hour × Day of Week)</div>", unsafe_allow_html=True)

pivot = (
    df_sel.assign(hour=df_sel.index.hour, dow=df_sel.index.dayofweek)
    .groupby(["dow", "hour"])["Global_active_power"]
    .mean()
    .unstack(level="hour")
)
dow_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
pivot.index = [dow_labels[i] for i in pivot.index]

fig_hmap = go.Figure(go.Heatmap(
    z=pivot.values,
    x=[f"{h:02d}:00" for h in pivot.columns],
    y=pivot.index.tolist(),
    colorscale=[
        [0.0, "#0d1526"],
        [0.3, "#0a2a4a"],
        [0.6, "#00d4ff"],
        [0.8, "#7b5ea7"],
        [1.0, "#ff4444"],
    ],
    hovertemplate="<b>%{y}</b> at <b>%{x}</b><br>%{z:.3f} kW<extra></extra>",
    showscale=True,
    colorbar=dict(
        title=dict(text="kW", font=dict(color="#94a3b8")),
        tickfont=dict(color="#94a3b8"),
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.1)",
    ),
))
fig_hmap.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(color="#475569", tickangle=-45),
    yaxis=dict(color="#475569"),
    height=340, margin=dict(l=10, r=10, t=20, b=10), font=dict(color="#e2e8f0"),
)
st.plotly_chart(fig_hmap, use_container_width=True)

# ─── Section 3: Sub-meter stacked area ─────────────────────────────────────────
st.markdown("<div class='section-header'>Sub-meter Breakdown</div>", unsafe_allow_html=True)

sm_cols = [c for c in ["Sub_metering_1", "Sub_metering_2", "Sub_metering_3"] if c in df_agg.columns]
sm_labels = {"Sub_metering_1": "🍳 Kitchen", "Sub_metering_2": "🧺 Laundry", "Sub_metering_3": "❄️ HVAC"}
sm_colors = {"Sub_metering_1": "#00d4ff", "Sub_metering_2": "#7b5ea7", "Sub_metering_3": "#00ff88"}
sm_fill_colors = {
    "Sub_metering_1": "rgba(0,212,255,0.35)",
    "Sub_metering_2": "rgba(123,94,167,0.35)",
    "Sub_metering_3": "rgba(0,255,136,0.35)",
}

fig_sm = go.Figure()
for sm in sm_cols:
    # Convert Wh → kWh for comparability
    y_vals = df_agg[sm] / 1000.0
    fig_sm.add_trace(go.Scatter(
        x=df_agg.index, y=y_vals,
        mode="lines",
        stackgroup="one",
        name=sm_labels.get(sm, sm),
        line=dict(color=sm_colors.get(sm, "#fff"), width=0.5),
        fillcolor=sm_fill_colors.get(sm, "rgba(255,255,255,0.3)"),
        hovertemplate="<b>%{x}</b><br>%{y:.3f} kWh<extra></extra>",
    ))

fig_sm.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="kWh"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    height=300, margin=dict(l=10, r=10, t=30, b=10), font=dict(color="#e2e8f0"),
    hovermode="x unified",
)
st.plotly_chart(fig_sm, use_container_width=True)

# ─── Section 4: Hourly profile comparison ──────────────────────────────────────
st.markdown("<div class='section-header'>Hourly Profile — Weekday vs Weekend</div>", unsafe_allow_html=True)

hourly_wd = df_sel[df_sel.index.dayofweek < 5].groupby(df_sel[df_sel.index.dayofweek < 5].index.hour)["Global_active_power"].mean()
hourly_we = df_sel[df_sel.index.dayofweek >= 5].groupby(df_sel[df_sel.index.dayofweek >= 5].index.hour)["Global_active_power"].mean()

fig_profile = go.Figure()
fig_profile.add_trace(go.Scatter(
    x=hourly_wd.index, y=hourly_wd.values,
    mode="lines+markers",
    name="Weekday",
    line=dict(color="#00d4ff", width=2.5),
    marker=dict(size=5),
))
fig_profile.add_trace(go.Scatter(
    x=hourly_we.index, y=hourly_we.values,
    mode="lines+markers",
    name="Weekend",
    line=dict(color="#7b5ea7", width=2.5, dash="dot"),
    marker=dict(size=5),
))
fig_profile.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#475569", title="Hour of Day", tickvals=list(range(0, 24, 2))),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="Avg kW"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    height=300, margin=dict(l=10, r=10, t=30, b=10), font=dict(color="#e2e8f0"),
)
st.plotly_chart(fig_profile, use_container_width=True)

# ─── Section 5: Correlation matrix ─────────────────────────────────────────────
st.markdown("<div class='section-header'>Feature Correlation Matrix</div>", unsafe_allow_html=True)

num_cols = [c for c in df_sel.columns if df_sel[c].dtype in [np.float64, np.float32]]
corr = df_sel[num_cols].corr()
labels = {
    "Global_active_power": "Active Power",
    "Global_reactive_power": "Reactive Power",
    "Voltage": "Voltage",
    "Global_intensity": "Intensity",
    "Sub_metering_1": "SM1 Kitchen",
    "Sub_metering_2": "SM2 Laundry",
    "Sub_metering_3": "SM3 HVAC",
}
corr.index = [labels.get(c, c) for c in corr.index]
corr.columns = [labels.get(c, c) for c in corr.columns]

fig_corr = px.imshow(
    corr,
    color_continuous_scale=[
        [0.0, "#7b5ea7"], [0.5, "#0a0e1a"], [1.0, "#00d4ff"]
    ],
    zmin=-1, zmax=1,
    text_auto=".2f",
)
fig_corr.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0"),
    height=400,
    margin=dict(l=10, r=10, t=20, b=10),
    coloraxis_colorbar=dict(
        tickfont=dict(color="#94a3b8"),
        title=dict(font=dict(color="#94a3b8")),
    ),
)
fig_corr.update_traces(textfont=dict(color="#e2e8f0"))
st.plotly_chart(fig_corr, use_container_width=True)

# ─── Summary stats table ───────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Summary Statistics</div>", unsafe_allow_html=True)
summary = df_sel[num_cols].describe().T
summary.index = [labels.get(c, c) for c in summary.index]


def _gradient_brand(s: pd.Series) -> list[str]:
    """Applies an elegant cyan background gradient without requiring matplotlib."""
    min_v, max_v = s.min(), s.max()
    if pd.isna(min_v) or pd.isna(max_v) or max_v == min_v:
        return ["" for _ in s]
    norm = (s - min_v) / (max_v - min_v)
    return [
        f"background-color: rgba(0, 212, 255, {0.06 + 0.30 * float(v):.2f}); color: #f8fafc;"
        for v in norm
    ]


st.dataframe(
    summary.style.format("{:.3f}").apply(_gradient_brand, subset=["mean", "max"]),
    use_container_width=True,
    height=260,
)
