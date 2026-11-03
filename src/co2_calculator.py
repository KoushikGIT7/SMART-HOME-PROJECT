"""
Module 11: CO₂ Calculator
==========================
Converts energy consumption data to CO₂ equivalent emissions and
provides human-readable analogies (trees planted, car km saved).
"""

from __future__ import annotations

import logging

import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class CO2Calculator:
    """
    Computes CO₂ footprint from hourly energy consumption data.

    Uses the Indian grid average emission factor of 0.82 kg CO₂/kWh.
    """

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        co2 = cfg["co2"]
        self.emission_factor: float = co2["emission_factor_kg_per_kwh"]
        self.tree_absorption: float = co2["tree_absorption_kg_per_year"]
        self.car_km_per_kg: float = co2["car_km_per_kg_co2"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(self, df: pd.DataFrame) -> dict:
        """
        Compute CO₂ metrics from hourly active power data.

        Parameters
        ----------
        df : hourly DataFrame with 'Global_active_power' (kW)

        Returns
        -------
        dict with:
            total_co2_kg, monthly_co2_kg, daily_co2_kg,
            trees_equivalent, car_km_equivalent,
            yoy_trend_pct (None if < 2 years data)
        """
        # kW (mean per hour) × 1h = kWh
        hourly_kwh = df["Global_active_power"]
        total_kwh = float(hourly_kwh.sum())

        hours = len(df)
        hours_per_month = 30 * 24
        hours_per_year = 365 * 24

        total_co2 = total_kwh * self.emission_factor
        monthly_co2 = (total_kwh / hours * hours_per_month) * self.emission_factor
        daily_co2 = (total_kwh / hours * 24) * self.emission_factor
        annual_co2 = (total_kwh / hours * hours_per_year) * self.emission_factor

        trees_equiv = annual_co2 / self.tree_absorption
        car_km_equiv = total_co2 * self.car_km_per_kg

        # Year-over-year trend
        yoy_trend_pct = self._yoy_trend(df)

        # Monthly breakdown
        monthly_series = self._monthly_breakdown(df)

        return {
            "total_co2_kg": round(total_co2, 2),
            "monthly_co2_kg": round(monthly_co2, 2),
            "daily_co2_kg": round(daily_co2, 2),
            "annual_co2_kg": round(annual_co2, 2),
            "trees_equivalent": round(trees_equiv, 1),
            "car_km_equivalent": round(car_km_equiv, 0),
            "yoy_trend_pct": yoy_trend_pct,
            "monthly_breakdown": monthly_series,
            "emission_factor": self.emission_factor,
        }

    def kwh_to_co2(self, kwh: float) -> float:
        """Convert kWh to kg CO₂."""
        return round(kwh * self.emission_factor, 3)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _yoy_trend(self, df: pd.DataFrame) -> float | None:
        """
        Compute year-over-year change in annual consumption (%).
        Returns None if data spans fewer than 2 years.
        """
        years = df.index.year.unique()
        if len(years) < 2:
            return None

        year_kwh = df.groupby(df.index.year)["Global_active_power"].sum()
        if len(year_kwh) >= 2:
            prev_year = year_kwh.iloc[-2]
            curr_year = year_kwh.iloc[-1]
            if prev_year > 0:
                return round((curr_year - prev_year) / prev_year * 100, 1)
        return None

    def _monthly_breakdown(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return monthly CO₂ kg totals as a DataFrame."""
        monthly_kwh = df["Global_active_power"].resample("ME").sum()
        monthly_co2 = monthly_kwh * self.emission_factor
        return monthly_co2.rename("co2_kg").to_frame()
