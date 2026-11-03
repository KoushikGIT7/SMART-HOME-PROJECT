"""
Module 4: Feature Engineering
==============================
Constructs the full feature matrix for LightGBM training and inference.

Features
--------
- Lag features: 1h, 2h, 3h, 6h, 12h, 24h, 48h, 168h (1 week)
- Rolling statistics: 3h, 6h, 24h, 168h mean & std
- Calendar: hour, dayofweek, month, quarter, is_weekend
- Sub-meter ratios relative to total active power
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class FeatureEngineer:
    """Builds lag, rolling, and calendar features for the forecasting model."""

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        fc = cfg["features"]
        self.target: str = fc["target"]
        self.lag_hours: list[int] = fc["lag_hours"]
        self.rolling_windows: list[int] = fc["rolling_windows"]
        self.sub_meters: list[str] = fc["sub_meters"]
        self.calendar_feats: list[str] = fc["calendar"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all features to ``df`` in-place and return the enriched frame.

        NaN rows introduced by lagging are *not* dropped here; the caller
        should decide whether to drop them (training) or forward-fill (inference).
        """
        df = df.copy()
        df = self._add_lag_features(df)
        df = self._add_rolling_features(df)
        df = self._add_calendar_features(df)
        df = self._add_submeter_ratios(df)
        return df

    def get_feature_names(self, df: pd.DataFrame) -> list[str]:
        """Return the list of feature column names (excludes target)."""
        return [c for c in df.columns if c != self.target]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        for lag in self.lag_hours:
            df[f"lag_{lag}h"] = df[self.target].shift(lag)
        return df

    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        for window in self.rolling_windows:
            roll = df[self.target].rolling(window=window, min_periods=1)
            df[f"rolling_mean_{window}h"] = roll.mean()
            df[f"rolling_std_{window}h"] = roll.std().fillna(0)
        return df

    def _add_calendar_features(self, df: pd.DataFrame) -> pd.DataFrame:
        idx = df.index
        df["hour"] = idx.hour
        df["dayofweek"] = idx.dayofweek          # 0=Monday, 6=Sunday
        df["month"] = idx.month
        df["quarter"] = idx.quarter
        df["is_weekend"] = (idx.dayofweek >= 5).astype(int)
        df["hour_sin"] = np.sin(2 * np.pi * idx.hour / 24)
        df["hour_cos"] = np.cos(2 * np.pi * idx.hour / 24)
        df["dow_sin"] = np.sin(2 * np.pi * idx.dayofweek / 7)
        df["dow_cos"] = np.cos(2 * np.pi * idx.dayofweek / 7)
        return df

    def _add_submeter_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        total = df[self.target].replace(0, np.nan)
        for sm in self.sub_meters:
            if sm in df.columns:
                df[f"{sm}_ratio"] = (df[sm] / total).fillna(0)
        return df
