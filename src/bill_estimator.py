"""
Module 10: Bill Estimator
==========================
Calculates electricity and water bills using tiered tariff slabs
(Indian BESCOM-style), with monthly/weekly/daily breakdowns and
per-sub-meter attribution.
"""

from __future__ import annotations

import logging

import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class BillEstimator:
    """
    Estimates electricity bills using configurable tiered tariff slabs.

    The slab structure mirrors the Indian BESCOM domestic tariff:
    - 0–30 kWh/month:  ₹3.15/kWh
    - 31–100 kWh/month: ₹5.50/kWh
    - 101–200 kWh/month: ₹6.30/kWh
    - 201–500 kWh/month: ₹7.10/kWh
    - 500+ kWh/month:   ₹8.00/kWh
    """

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        bc = cfg["billing"]
        self.slabs: list[dict] = bc["electricity_slabs"]
        self.fixed_charge: float = bc["fixed_charges_per_month"]
        self.water_rate: float = bc["water_rate_per_litre"]
        self.currency: str = bc["currency"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def estimate(self, df: pd.DataFrame, water_df: pd.DataFrame | None = None) -> dict:
        """
        Compute a comprehensive bill estimate from hourly data.

        Parameters
        ----------
        df       : hourly energy DataFrame (Global_active_power in kW)
        water_df : hourly water DataFrame (water_usage_litres)

        Returns
        -------
        dict with keys:
            total_kwh, monthly_kwh, monthly_bill_inr,
            weekly_bill_inr, daily_bill_inr,
            water_monthly_bill_inr (if water_df provided),
            submeter_breakdown (dict), grand_total_inr
        """
        # Convert kW (mean per hour) → kWh
        hourly_kwh = df["Global_active_power"].copy()
        # kW × 1h = kWh
        total_kwh = float(hourly_kwh.sum())

        # Project to monthly
        hours_in_data = len(df)
        hours_per_month = 30 * 24
        monthly_kwh = total_kwh / hours_in_data * hours_per_month

        monthly_bill = self._tiered_bill(monthly_kwh) + self.fixed_charge
        weekly_bill = monthly_bill / 4.33
        daily_bill = monthly_bill / 30

        # Sub-meter breakdown
        submeter_breakdown = self._submeter_attribution(df, monthly_kwh)

        # Water bill
        water_bill = 0.0
        if water_df is not None and "water_usage_litres" in water_df.columns:
            total_litres = float(water_df["water_usage_litres"].sum())
            monthly_litres = total_litres / hours_in_data * hours_per_month
            water_bill = monthly_litres * self.water_rate

        grand_total = monthly_bill + water_bill

        return {
            "total_kwh": round(total_kwh, 2),
            "monthly_kwh": round(monthly_kwh, 2),
            "monthly_bill_inr": round(monthly_bill, 2),
            "weekly_bill_inr": round(weekly_bill, 2),
            "daily_bill_inr": round(daily_bill, 2),
            "water_monthly_bill_inr": round(water_bill, 2),
            "submeter_breakdown": submeter_breakdown,
            "grand_total_inr": round(grand_total, 2),
            "currency": self.currency,
        }

    def estimate_monthly_from_kwh(self, monthly_kwh: float) -> float:
        """Return total monthly bill (incl. fixed charge) for given kWh."""
        return round(self._tiered_bill(monthly_kwh) + self.fixed_charge, 2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _tiered_bill(self, kwh: float) -> float:
        """Apply tiered slab billing to a monthly kWh value."""
        bill = 0.0
        remaining = kwh
        prev_limit = 0.0

        for slab in self.slabs:
            slab_limit = slab["upto"]
            rate = slab["rate"]
            slab_size = slab_limit - prev_limit

            if remaining <= 0:
                break

            consumed_in_slab = min(remaining, slab_size)
            bill += consumed_in_slab * rate
            remaining -= consumed_in_slab
            prev_limit = slab_limit

        return bill

    def _submeter_attribution(self, df: pd.DataFrame, monthly_kwh: float) -> dict:
        """Attribute fraction of monthly kWh to each sub-meter."""
        result = {}
        sub_meters = ["Sub_metering_1", "Sub_metering_2", "Sub_metering_3"]
        labels = {
            "Sub_metering_1": "Kitchen",
            "Sub_metering_2": "Laundry",
            "Sub_metering_3": "HVAC / Water Heater",
        }

        total_sm = 0.0
        sm_kwh: dict[str, float] = {}
        for sm in sub_meters:
            if sm in df.columns:
                # Sub-metering is in Wh → convert to kWh
                wh_sum = float(df[sm].sum())
                kwh = wh_sum / 1000.0
                sm_kwh[sm] = kwh
                total_sm += kwh

        other_kwh = max(0.0, monthly_kwh - total_sm)
        for sm, kwh in sm_kwh.items():
            fraction = kwh / monthly_kwh if monthly_kwh > 0 else 0
            result[labels[sm]] = {
                "monthly_kwh": round(kwh, 2),
                "fraction": round(fraction, 3),
                "monthly_bill_inr": round(self._tiered_bill(kwh * (monthly_kwh / max(total_sm, 1))), 2),
            }

        result["Other"] = {
            "monthly_kwh": round(other_kwh, 2),
            "fraction": round(other_kwh / monthly_kwh if monthly_kwh > 0 else 0, 3),
            "monthly_bill_inr": round(self._tiered_bill(other_kwh), 2),
        }

        return result
