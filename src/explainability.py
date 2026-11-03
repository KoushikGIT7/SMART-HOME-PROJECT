"""
Module 7: Explainability (SHAP)
================================
Computes SHAP values using TreeExplainer for the LightGBM model,
generates Plotly-renderable SHAP summary data, and produces
natural-language explanations for predictions and anomalies.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from src.forecasting import ForecastingEngine

logger = logging.getLogger(__name__)

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not installed. Explainability features disabled.")


# ---------------------------------------------------------------------------
# Human-readable feature labels
# ---------------------------------------------------------------------------
FEATURE_LABELS: dict[str, str] = {
    "lag_1h": "1-hour ago usage",
    "lag_2h": "2-hours ago usage",
    "lag_3h": "3-hours ago usage",
    "lag_6h": "6-hours ago usage",
    "lag_12h": "12-hours ago usage",
    "lag_24h": "Yesterday (same hour)",
    "lag_48h": "2 days ago (same hour)",
    "lag_168h": "Last week (same hour)",
    "rolling_mean_3h": "3-hour rolling average",
    "rolling_mean_6h": "6-hour rolling average",
    "rolling_mean_24h": "24-hour rolling average",
    "rolling_mean_168h": "Weekly rolling average",
    "rolling_std_3h": "3-hour variability",
    "rolling_std_24h": "24-hour variability",
    "hour": "Hour of day",
    "dayofweek": "Day of week",
    "month": "Month",
    "is_weekend": "Weekend flag",
    "quarter": "Quarter of year",
    "hour_sin": "Hour (cyclical)",
    "hour_cos": "Hour (cyclical)",
    "Sub_metering_1_ratio": "Kitchen appliance ratio",
    "Sub_metering_2_ratio": "Laundry appliance ratio",
    "Sub_metering_3_ratio": "HVAC appliance ratio",
}


class ExplainabilityEngine:
    """
    Provides SHAP-based explanations for the LightGBM forecasting model.
    """

    def __init__(self):
        self.explainer = None
        self.feature_list: list[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def setup(self, engine: "ForecastingEngine") -> None:
        """Initialise TreeExplainer from a trained ForecastingEngine."""
        if not SHAP_AVAILABLE:
            return
        if engine.model is None:
            raise RuntimeError("Engine model not loaded.")
        self.explainer = shap.TreeExplainer(engine.model)
        self.feature_list = engine.feature_list
        logger.info("SHAP TreeExplainer initialised.")

    def compute_shap_values(
        self, df: pd.DataFrame, max_rows: int = 500
    ) -> tuple[np.ndarray, pd.DataFrame]:
        """
        Compute SHAP values for up to ``max_rows`` rows of ``df``.

        Returns
        -------
        shap_values : np.ndarray (n_rows × n_features)
        X_sample    : DataFrame of input features (same shape)
        """
        if not SHAP_AVAILABLE or self.explainer is None:
            raise RuntimeError("SHAP explainer not initialised.")

        sample = df[self.feature_list].dropna().tail(max_rows)
        sv = self.explainer.shap_values(sample.values)
        return sv, sample

    def global_importance_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Return a DataFrame of mean |SHAP| values per feature, sorted descending.
        Suitable for plotting as a bar chart.
        """
        sv, sample = self.compute_shap_values(df)
        mean_abs = np.abs(sv).mean(axis=0)
        imp_df = pd.DataFrame(
            {
                "feature": self.feature_list,
                "mean_abs_shap": mean_abs,
                "label": [FEATURE_LABELS.get(f, f) for f in self.feature_list],
            }
        ).sort_values("mean_abs_shap", ascending=False)
        return imp_df

    def explain_row(self, row: pd.Series, predicted: float) -> str:
        """
        Generate a natural-language explanation for a single prediction.

        Parameters
        ----------
        row       : Series with feature values (index = feature names)
        predicted : model's predicted value for this row

        Returns
        -------
        str : human-readable explanation paragraph
        """
        if not SHAP_AVAILABLE or self.explainer is None:
            return f"Predicted consumption: **{predicted:.2f} kW**."

        try:
            feat_vals = row[self.feature_list].values.reshape(1, -1)
            sv = self.explainer.shap_values(feat_vals)[0]

            top_idx = np.argsort(np.abs(sv))[::-1][:3]
            parts = []
            for i in top_idx:
                fname = self.feature_list[i]
                label = FEATURE_LABELS.get(fname, fname)
                val = feat_vals[0][i]
                shap_val = sv[i]
                direction = "increased" if shap_val > 0 else "decreased"
                parts.append(
                    f"**{label}** ({val:.2f}) {direction} the prediction "
                    f"by {abs(shap_val):.3f} kW"
                )

            explanation = (
                f"Predicted consumption: **{predicted:.2f} kW**.\n\n"
                "The top contributing factors are:\n\n"
                + "\n\n".join(f"- {p}" for p in parts)
            )
            return explanation
        except Exception as exc:
            logger.warning("SHAP explain_row failed: %s", exc)
            return f"Predicted consumption: **{predicted:.2f} kW**."

    def explain_anomaly(self, row: pd.Series, z_score: float, severity: str) -> str:
        """
        Generate a natural-language explanation for an anomaly event.
        """
        severity_text = {
            "critical": "🔴 **Critical anomaly** detected",
            "warning": "🟡 **Warning-level anomaly** detected",
            "info": "🔵 **Informational anomaly** noted",
        }.get(severity, "⚠️ Anomaly detected")

        base = (
            f"{severity_text} at **{row.name}**.\n\n"
            f"Consumption deviated by **{z_score:.1f}σ** from forecast.\n\n"
        )

        if not SHAP_AVAILABLE or self.explainer is None:
            return base

        try:
            feat_vals = row[self.feature_list].values.reshape(1, -1)
            sv = self.explainer.shap_values(feat_vals)[0]
            top_idx = np.argsort(np.abs(sv))[::-1][:2]
            causes = []
            for i in top_idx:
                fname = self.feature_list[i]
                label = FEATURE_LABELS.get(fname, fname)
                causes.append(f"**{label}**")
            base += "Likely driven by: " + " and ".join(causes) + "."
        except Exception:
            pass

        return base
