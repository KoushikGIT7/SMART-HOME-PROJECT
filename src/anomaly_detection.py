"""
Module 6: Anomaly Detection Engine
=====================================
Combines three complementary detection strategies:

1. Isolation Forest    — unsupervised anomaly score on feature matrix
2. Residual Z-score    — |actual − forecast| / rolling_std > threshold
3. Water Leak Rule     — sustained flow > P95 for ≥ N consecutive hours

Results are merged into a unified severity column: critical / warning / info.
"""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class AnomalyDetectionEngine:
    """
    Multi-signal anomaly detection for smart home energy and water data.
    """

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        ac = cfg["anomaly"]
        self.iso_params: dict = {
            k: v
            for k, v in ac["isolation_forest"].items()
            if k != "model_path"
        }
        self.iso_model_path = Path(ac["isolation_forest"]["model_path"])
        self.zscore_threshold: float = ac["residual_zscore_threshold"]
        self.water_pct: int = ac["water_leak_percentile"]
        self.water_consecutive: int = ac["water_leak_consecutive_hours"]
        self.critical_z: float = ac["severity_thresholds"]["critical_zscore"]
        self.warning_z: float = ac["severity_thresholds"]["warning_zscore"]

        self.iso_model: IsolationForest | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_trained(self) -> bool:
        return self.iso_model_path.exists()

    def train_isolation_forest(self, feature_df: pd.DataFrame) -> None:
        """Fit IsolationForest on the clean feature matrix and persist."""
        X = feature_df.dropna().values
        logger.info("Training IsolationForest on %d samples …", len(X))
        self.iso_model = IsolationForest(**self.iso_params)
        self.iso_model.fit(X)
        self.iso_model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.iso_model, self.iso_model_path)
        logger.info("IsolationForest saved to %s", self.iso_model_path)

    def load(self) -> None:
        self.iso_model = joblib.load(self.iso_model_path)
        logger.info("IsolationForest loaded from %s", self.iso_model_path)

    def detect(
        self,
        feature_df: pd.DataFrame,
        forecast_df: pd.DataFrame | None = None,
        water_df: pd.DataFrame | None = None,
    ) -> pd.DataFrame:
        """
        Run all detectors and return a unified anomaly DataFrame.

        Parameters
        ----------
        feature_df   : DataFrame with engineered features (includes target)
        forecast_df  : output of ForecastingEngine.predict_on_df (optional)
        water_df     : DataFrame with 'water_usage_litres' column (optional)

        Returns
        -------
        pd.DataFrame
            index = timestamps, columns = [
                iso_score, iso_anomaly,
                z_score, z_anomaly,
                water_anomaly,          # if water_df provided
                is_anomaly, severity,
                actual, predicted       # if forecast_df provided
            ]
        """
        result = pd.DataFrame(index=feature_df.dropna().index)

        # ---- 1. Isolation Forest ----
        result = self._run_isolation_forest(result, feature_df)

        # ---- 2. Residual Z-score ----
        if forecast_df is not None and "residual" in forecast_df.columns:
            result = self._run_zscore(result, forecast_df)

        # ---- 3. Water Leak Rule ----
        if water_df is not None:
            result = self._run_water_rule(result, water_df)

        # ---- Merge severity ----
        result = self._assign_severity(result)

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_isolation_forest(
        self, result: pd.DataFrame, feature_df: pd.DataFrame
    ) -> pd.DataFrame:
        clean = feature_df.dropna()
        if self.iso_model is None:
            result["iso_score"] = np.nan
            result["iso_anomaly"] = False
            return result

        X = clean.values
        scores = self.iso_model.decision_function(X)   # higher = more normal
        preds = self.iso_model.predict(X)              # -1 = anomaly, 1 = normal

        aligned_scores = pd.Series(scores, index=clean.index).reindex(result.index)
        aligned_preds = pd.Series(preds, index=clean.index).reindex(result.index)

        result["iso_score"] = aligned_scores
        result["iso_anomaly"] = aligned_preds == -1
        return result

    def _run_zscore(
        self, result: pd.DataFrame, forecast_df: pd.DataFrame
    ) -> pd.DataFrame:
        residuals = forecast_df["residual"].reindex(result.index)
        roll_std = residuals.rolling(window=24, min_periods=6).std().fillna(
            residuals.std()
        )
        z = (residuals.abs() / roll_std.replace(0, 1)).fillna(0)

        result["z_score"] = z
        result["z_anomaly"] = z > self.zscore_threshold

        if "actual" in forecast_df.columns:
            result["actual"] = forecast_df["actual"].reindex(result.index)
        if "predicted" in forecast_df.columns:
            result["predicted"] = forecast_df["predicted"].reindex(result.index)

        return result

    def _run_water_rule(
        self, result: pd.DataFrame, water_df: pd.DataFrame
    ) -> pd.DataFrame:
        usage = water_df["water_usage_litres"].reindex(result.index)
        threshold = float(np.nanpercentile(usage.dropna().values, self.water_pct))

        above = (usage > threshold).astype(int)
        # Rolling sum: flag if ≥ N consecutive hours above threshold
        consec = above.rolling(window=self.water_consecutive, min_periods=self.water_consecutive).sum()
        result["water_anomaly"] = consec >= self.water_consecutive
        result["water_usage"] = usage
        return result

    def _assign_severity(self, result: pd.DataFrame) -> pd.DataFrame:
        """Combine signals into is_anomaly + severity."""
        iso_anom = result.get("iso_anomaly", pd.Series(False, index=result.index))
        z_anom = result.get("z_anomaly", pd.Series(False, index=result.index))
        water_anom = result.get("water_anomaly", pd.Series(False, index=result.index))

        result["is_anomaly"] = iso_anom | z_anom | water_anom

        # Severity logic
        z_score = result.get("z_score", pd.Series(0.0, index=result.index)).fillna(0)

        def _severity(row_idx):
            if water_anom.get(row_idx, False):
                return "critical"
            z = z_score.get(row_idx, 0)
            if z >= self.critical_z or iso_anom.get(row_idx, False):
                return "critical"
            if z >= self.warning_z or z_anom.get(row_idx, False):
                return "warning"
            return "info"

        result["severity"] = [
            _severity(idx) if result.loc[idx, "is_anomaly"] else "normal"
            for idx in result.index
        ]
        return result
