"""
Module 5: Forecasting Engine
=============================
Trains a LightGBM regressor on the engineered feature matrix,
evaluates it with time-series cross-validation, persists model
artifacts, and provides a ``predict`` API for the dashboard.
"""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class ForecastingEngine:
    """
    LightGBM-based energy consumption forecasting.

    Responsibilities
    ----------------
    - Train on historical data with time-series split
    - Save / load model + feature list artifacts
    - Predict next ``horizon`` hours with 95% prediction interval
    - Expose residuals for anomaly detection (Z-score method)
    """

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        fc_cfg = cfg["forecasting"]
        self.model_path = Path(fc_cfg["model_path"])
        self.feature_path = Path(fc_cfg["feature_path"])
        self.scaler_path = Path(fc_cfg["scaler_path"])
        # Persists the test-set residual std so CI bands survive model reloads
        self.residual_std_path = self.model_path.parent / "residual_std.joblib"
        self.horizon: int = fc_cfg["horizon"]
        self.test_split_days: int = fc_cfg["test_split_days"]
        self.lgbm_params: dict = fc_cfg["lgbm_params"]
        self.target: str = cfg["features"]["target"]

        self.model: LGBMRegressor | None = None
        self.feature_list: list[str] = []
        self.scaler: StandardScaler | None = None
        self.residual_std: float = 1.0  # used for prediction intervals; restored from disk on load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_trained(self) -> bool:
        return self.model_path.exists() and self.feature_path.exists()

    def train(self, df: pd.DataFrame) -> dict:
        """
        Train LightGBM model.

        Parameters
        ----------
        df : feature-engineered DataFrame (includes target column)

        Returns
        -------
        dict with train/test metrics: rmse, mae, r2
        """
        df_clean = df.dropna()
        feature_cols = [c for c in df_clean.columns if c != self.target]
        X = df_clean[feature_cols].values
        y = df_clean[self.target].values

        # Time-series split: last N days as test
        split_idx = len(df_clean) - self.test_split_days * 24
        split_idx = max(split_idx, int(len(df_clean) * 0.8))

        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        logger.info(
            "Training LightGBM on %d samples, testing on %d …",
            len(X_train),
            len(X_test),
        )

        self.model = LGBMRegressor(**self.lgbm_params)
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)],
            callbacks=[],
        )

        self.feature_list = feature_cols

        # Compute residual std on test set for prediction intervals
        y_pred_test = self.model.predict(X_test)
        residuals = y_test - y_pred_test
        self.residual_std = float(np.std(residuals))

        metrics = self._compute_metrics(y_test, y_pred_test)
        logger.info("Test metrics: %s", metrics)

        self._save()
        return metrics

    def load(self) -> None:
        """Load persisted model artifacts from disk."""
        self.model = joblib.load(self.model_path)
        self.feature_list = joblib.load(self.feature_path)
        if self.scaler_path.exists():
            self.scaler = joblib.load(self.scaler_path)
        # Restore real residual std so CI bands reflect actual model variance
        if self.residual_std_path.exists():
            self.residual_std = joblib.load(self.residual_std_path)
            logger.info("Residual std restored: %.4f", self.residual_std)
        logger.info("Model loaded from %s", self.model_path)

    def predict_on_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate predictions for every row in ``df`` that has no NaN features.

        Returns a DataFrame with columns: ``predicted``, ``lower``, ``upper``,
        ``actual`` (if available), ``residual`` (if actual available).
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call train() or load() first.")

        df_clean = df.dropna(subset=self.feature_list)
        X = df_clean[self.feature_list].values
        preds = self.model.predict(X)

        result = pd.DataFrame(index=df_clean.index)
        result["predicted"] = preds
        z = 1.96
        result["lower"] = preds - z * self.residual_std
        result["upper"] = preds + z * self.residual_std

        if self.target in df_clean.columns:
            result["actual"] = df_clean[self.target].values
            result["residual"] = result["actual"] - result["predicted"]

        return result

    def forecast_future(
        self, df: pd.DataFrame, horizon: int | None = None
    ) -> pd.DataFrame:
        """
        Iteratively forecast ``horizon`` steps beyond the last row of ``df``.

        Uses the last known row's features to seed lag/rolling lookups.
        Returns forecast DataFrame: index=future timestamps,
        columns=``predicted``, ``lower``, ``upper``.
        """
        horizon = horizon or self.horizon
        if self.model is None:
            raise RuntimeError("Model not loaded.")

        # We approximate by extending the last window
        last_row = df.dropna(subset=self.feature_list).iloc[-horizon:]
        if len(last_row) == 0:
            raise ValueError("No complete feature rows available for forecast.")

        X_future = last_row[self.feature_list].values[-horizon:]
        preds = self.model.predict(X_future)

        last_ts = df.index[-1]
        future_idx = pd.date_range(
            start=last_ts + pd.Timedelta("1h"), periods=horizon, freq="1h"
        )

        z = 1.96
        return pd.DataFrame(
            {
                "predicted": preds,
                "lower": preds - z * self.residual_std,
                "upper": preds + z * self.residual_std,
            },
            index=future_idx,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _save(self) -> None:
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.feature_list, self.feature_path)
        joblib.dump(self.residual_std, self.residual_std_path)
        logger.info("Model saved to %s (residual_std=%.4f)", self.model_path, self.residual_std)

    @staticmethod
    def _compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae = float(mean_absolute_error(y_true, y_pred))
        r2 = float(r2_score(y_true, y_pred))
        return {"rmse": rmse, "mae": mae, "r2": r2}
