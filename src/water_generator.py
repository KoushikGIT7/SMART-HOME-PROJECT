"""
Module 3: Water Data Generator
===============================
Generates realistic synthetic hourly water-usage data correlated with
time-of-day patterns. Injects random "leak" events for anomaly testing.
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


class WaterDataGenerator:
    """
    Generates synthetic hourly water consumption data.

    The generator uses:
    - A base daily volume split across 24 hours
    - Morning and evening peak multipliers
    - Gaussian noise
    - Random "leak" events (sustained high flow over multiple hours)
    """

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        wc = cfg["water"]
        self.daily_mean: float = wc["daily_mean_litres"]
        self.daily_std: float = wc["daily_std_litres"]
        self.peak_morning: list[int] = wc["peak_hours_morning"]
        self.peak_evening: list[int] = wc["peak_hours_evening"]
        self.leak_prob: float = wc["leak_probability"]
        self.leak_mult: float = wc["leak_multiplier"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self, index: pd.DatetimeIndex, seed: int = 42
    ) -> pd.DataFrame:
        """
        Generate synthetic water-usage DataFrame aligned to ``index``.

        Parameters
        ----------
        index : DatetimeIndex (hourly)
        seed  : random seed for reproducibility

        Returns
        -------
        pd.DataFrame with columns:
            - water_usage_litres   : hourly consumption
            - water_leak_flag      : boolean leak indicator
        """
        rng = np.random.default_rng(seed)

        n = len(index)
        hours = index.hour.values

        # --- Build hourly weight profile ---
        weights = self._hour_weights(hours)

        # --- Scale weights so daily sum ≈ daily_mean ---
        # Daily mean spread across 24 hours
        daily_volume = rng.normal(
            self.daily_mean, self.daily_std, size=n // 24 + 2
        ).clip(min=20)

        # Assign each hour a fraction of its day's volume
        water = np.zeros(n)
        for i, ts in enumerate(index):
            day_idx = (ts - index[0]).days
            day_idx = min(day_idx, len(daily_volume) - 1)
            water[i] = weights[i] * daily_volume[day_idx]

        # Add hourly noise
        water += rng.normal(0, self.daily_mean * 0.04, size=n)
        water = water.clip(min=0)

        # --- Inject leak events ---
        leak_flags = np.zeros(n, dtype=bool)
        i = 0
        while i < n:
            if rng.random() < self.leak_prob:
                duration = int(rng.integers(3, 12))
                end = min(i + duration, n)
                water[i:end] *= self.leak_mult
                leak_flags[i:end] = True
                i = end
            else:
                i += 1

        return pd.DataFrame(
            {
                "water_usage_litres": water,
                "water_leak_flag": leak_flags,
            },
            index=index,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _hour_weights(self, hours: np.ndarray) -> np.ndarray:
        """
        Return per-hour consumption weights summing to 1 per day.
        Morning and evening peaks get higher weights.
        """
        base = np.ones(24) * (1.0 / 24)
        for h in self.peak_morning:
            if 0 <= h < 24:
                base[h] *= 2.8
        for h in self.peak_evening:
            if 0 <= h < 24:
                base[h] *= 2.5
        # Normalise
        base /= base.sum()
        # Map per-row
        return base[hours]
