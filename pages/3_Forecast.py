"""
Page 3: Forecast
=================
LightGBM 24/48/72h forecast with confidence band, SHAP importance
bar chart, natural-language explanation, and model performance metrics.
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
    load_config_cached,
    load_features,
    load_forecast_engine,
    load_explainer,
    get_forecast_results,
    render_sidebar,
)

st.set_page_config(page_title="Forecast · Smart Home AI", page_icon="🔮", layout="wide")
inject_global_css()
render_sidebar()

cfg = load_config_cached()
df = load_and_clean_data()
feat_df = load_features()

st.markdown(
    "<div class='page-title'>🔮 AI Energy Forecast</div>"
    "<div class='page-subtitle'>LightGBM predictions with 95% confidence interval and SHAP explainability</div>",
    unsafe_allow_html=True,
)

# ─── Controls ──────────────────────────────────────────────────────────────────
col_h, col_hist, col_metric = st.columns([1, 2, 2])

with col_h:
    horizon = st.selectbox("Forecast Horizon", [24, 48, 72], index=0, key="fc_horizon")

with col_hist:
    hist_days = st.slider("Historical context (days)", 7, 60, 14, key="fc_hist_days")

with col_metric:
    show_metrics = st.toggle("Show model metrics", value=True, key="fc_show_metrics")

# ─── Load forecast data ────────────────────────────────────────────────────────
with st.spinner("Loading forecast…"):
    engine = load_forecast_engine()
    in_sample, _ = get_forecast_results()
    future_fc = engine.forecast_future(feat_df, horizon=horizon)

# Show last N days of in-sample + future forecast
cutoff = df.index[-1] - pd.Timedelta(days=hist_days)
hist_slice = in_sample[in_sample.index >= cutoff].copy()

# ─── Main forecast chart ───────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Forecast Chart</div>", unsafe_allow_html=True)

fig = go.Figure()

# Actual historical
fig.add_trace(go.Scatter(
    x=hist_slice.index, y=hist_slice["actual"],
    mode="lines",
    line=dict(color="#00d4ff", width=2),
    name="Actual",
    hovertemplate="<b>%{x}</b><br>Actual: %{y:.3f} kW<extra></extra>",
))

# In-sample prediction
fig.add_trace(go.Scatter(
    x=hist_slice.index, y=hist_slice["predicted"],
    mode="lines",
    line=dict(color="#7b5ea7", width=1.5, dash="dot"),
    name="In-sample Prediction",
    hovertemplate="<b>%{x}</b><br>Predicted: %{y:.3f} kW<extra></extra>",
))

# Future forecast confidence band
fig.add_trace(go.Scatter(
    x=list(future_fc.index) + list(future_fc.index[::-1]),
    y=list(future_fc["upper"]) + list(future_fc["lower"][::-1]),
    fill="toself",
    fillcolor="rgba(123,94,167,0.12)",
    line=dict(color="rgba(0,0,0,0)"),
    showlegend=True,
    name="95% Confidence",
    hoverinfo="skip",
))

# Future forecast line
fig.add_trace(go.Scatter(
    x=future_fc.index, y=future_fc["predicted"],
    mode="lines",
    line=dict(color="#ff9944", width=2.5),
    name=f"Forecast (+{horizon}h)",
    hovertemplate="<b>%{x}</b><br>Forecast: %{y:.3f} kW<extra></extra>",
))

# Vertical "now" line
now = df.index[-1]
fig.add_vline(
    x=now, line_color="rgba(0,255,136,0.4)", line_dash="dash",
    annotation_text="Now", annotation_font_color="#00ff88",
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="kW"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    height=380, margin=dict(l=10, r=10, t=40, b=10), font=dict(color="#e2e8f0"),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# ─── Model metrics ─────────────────────────────────────────────────────────────
if show_metrics and "residual" in in_sample.columns and "actual" in in_sample.columns:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    y_true = in_sample["actual"].dropna()
    y_pred = in_sample["predicted"].reindex(y_true.index)
    valid = y_true.notna() & y_pred.notna()
    y_t, y_p = y_true[valid].values, y_pred[valid].values

    rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
    mae = float(mean_absolute_error(y_t, y_p))
    r2 = float(r2_score(y_t, y_p))
    mape = float(np.mean(np.abs((y_t - y_p) / np.where(y_t == 0, 1, y_t))) * 100)

    st.markdown("<div class='section-header'>Model Performance</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("RMSE", f"{rmse:.4f} kW")
    m2.metric("MAE", f"{mae:.4f} kW")
    m3.metric("R²", f"{r2:.4f}")
    m4.metric("MAPE", f"{mape:.2f}%")

# ─── SHAP Importance ───────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>SHAP Feature Importance</div>", unsafe_allow_html=True)

try:
    explainer = load_explainer()
    imp_df = explainer.global_importance_df(feat_df.dropna())
    top_n = 15
    imp_top = imp_df.head(top_n)

    fig_shap = go.Figure(go.Bar(
        x=imp_top["mean_abs_shap"].values[::-1],
        y=imp_top["label"].values[::-1],
        orientation="h",
        marker=dict(
            color=imp_top["mean_abs_shap"].values[::-1],
            colorscale=[[0, "#7b5ea7"], [0.5, "#00d4ff"], [1, "#00ff88"]],
            showscale=False,
        ),
        hovertemplate="<b>%{y}</b><br>Mean |SHAP|: %{x:.4f}<extra></extra>",
    ))
    fig_shap.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#475569", title="Mean |SHAP value| (impact on prediction)"),
        yaxis=dict(color="#e2e8f0"),
        height=420, margin=dict(l=10, r=10, t=20, b=10), font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig_shap, use_container_width=True)

    # ─── Per-prediction NL explanation ─────────────────────────────────────────
    st.markdown("<div class='section-header'>Natural Language Explanation</div>", unsafe_allow_html=True)

    col_ts, col_nl = st.columns([1, 2])
    with col_ts:
        # Let user pick a timestamp
        valid_idx = feat_df.dropna().index
        ts_options = valid_idx[-48:].tolist()
        selected_ts = st.selectbox(
            "Select timestamp to explain",
            options=ts_options,
            index=len(ts_options) - 1,
            format_func=lambda t: t.strftime("%Y-%m-%d %H:%M"),
            key="fc_explain_ts",
        )

    with col_nl:
        if selected_ts in feat_df.index:
            row = feat_df.loc[selected_ts]
            pred_val = in_sample["predicted"].get(selected_ts, float(row.get(cfg["features"]["target"], 0)))
            explanation = explainer.explain_row(row, float(pred_val))
            st.markdown(
                f"<div class='kpi-card'>{explanation}</div>",
                unsafe_allow_html=True,
            )

except Exception as exc:
    st.info(f"SHAP explanations unavailable: {exc}")

# ─── Forecast summary table ─────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Forecast Detail Table</div>", unsafe_allow_html=True)
display_df = future_fc.copy()
display_df.index = display_df.index.strftime("%Y-%m-%d %H:%M")
display_df.columns = ["Predicted (kW)", "Lower CI", "Upper CI"]
display_df = display_df.round(4)
st.dataframe(display_df.style.format("{:.4f}"), use_container_width=True, height=300)
