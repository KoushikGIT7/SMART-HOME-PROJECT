"""
Module 8: Recommendation Engine
=================================
Generates ranked, actionable energy-saving recommendations with
estimated monthly rupee savings and CO₂ reduction per recommendation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class Recommendation:
    id: str
    title: str
    description: str
    category: str          # e.g. "HVAC", "Lighting", "Appliance", "Behaviour"
    icon: str
    estimated_monthly_saving_inr: float
    estimated_co2_saved_kg: float
    priority_score: float  # 0–100, higher = more impactful
    applicable: bool = True
    evidence: str = ""     # short string explaining why this was triggered


# ---------------------------------------------------------------------------
# Recommendation catalogue
# ---------------------------------------------------------------------------

CATALOGUE: list[dict] = [
    {
        "id": "hvac_schedule",
        "title": "Schedule HVAC Off-Peak Hours",
        "description": (
            "Your HVAC usage is high during peak tariff hours (6–10 PM). "
            "Pre-cool or pre-heat your home during off-peak hours (10 PM–6 AM) "
            "to cut bills without sacrificing comfort."
        ),
        "category": "HVAC",
        "icon": "❄️",
        "base_saving_inr": 480,
        "base_co2_kg": 18.0,
        "base_priority": 90,
        "trigger": "high_evening_usage",
    },
    {
        "id": "led_upgrade",
        "title": "Switch to LED Lighting",
        "description": (
            "Replacing all incandescent and CFL bulbs with LED equivalents "
            "reduces lighting energy consumption by up to 80%."
        ),
        "category": "Lighting",
        "icon": "💡",
        "base_saving_inr": 220,
        "base_co2_kg": 8.5,
        "base_priority": 75,
        "trigger": "always",
    },
    {
        "id": "standby_power",
        "title": "Eliminate Standby / Phantom Loads",
        "description": (
            "Your overnight baseline consumption is elevated, suggesting devices "
            "are drawing power on standby. Use smart power strips or unplug "
            "chargers and entertainment systems when not in use."
        ),
        "category": "Appliance",
        "icon": "🔌",
        "base_saving_inr": 150,
        "base_co2_kg": 5.8,
        "base_priority": 70,
        "trigger": "high_night_baseline",
    },
    {
        "id": "laundry_offpeak",
        "title": "Run Laundry During Off-Peak Hours",
        "description": (
            "Washing machines and dryers (Sub-meter 2) have high usage during "
            "peak evening hours. Shift laundry cycles to mornings or nights "
            "to save on time-of-use tariffs."
        ),
        "category": "Appliance",
        "icon": "🧺",
        "base_saving_inr": 190,
        "base_co2_kg": 7.3,
        "base_priority": 65,
        "trigger": "high_submeter2_evening",
    },
    {
        "id": "solar_panels",
        "title": "Install Rooftop Solar (3 kW)",
        "description": (
            "Based on your average daily consumption, a 3 kW rooftop solar "
            "system could offset 70–80% of your daytime electricity usage, "
            "with payback period of ~5 years."
        ),
        "category": "Renewable",
        "icon": "☀️",
        "base_saving_inr": 1200,
        "base_co2_kg": 46.0,
        "base_priority": 95,
        "trigger": "high_overall_usage",
    },
    {
        "id": "smart_thermostat",
        "title": "Install a Smart Thermostat",
        "description": (
            "A learning thermostat reduces HVAC runtime by 15–20% by adapting "
            "to your schedule and preferences automatically."
        ),
        "category": "HVAC",
        "icon": "🌡️",
        "base_saving_inr": 360,
        "base_co2_kg": 14.0,
        "base_priority": 80,
        "trigger": "hvac_always",
    },
    {
        "id": "water_heater_schedule",
        "title": "Timer-Control Your Water Heater",
        "description": (
            "Water heaters running continuously account for ~18% of home energy use. "
            "Set a timer to heat water only 30 min before peak shower times."
        ),
        "category": "Appliance",
        "icon": "🚿",
        "base_saving_inr": 270,
        "base_co2_kg": 10.4,
        "base_priority": 78,
        "trigger": "always",
    },
    {
        "id": "weekend_usage_audit",
        "title": "Weekend Energy Audit",
        "description": (
            "Your weekend consumption is significantly higher than weekdays. "
            "Identify high-draw weekend activities (gaming, cooking, guests) "
            "and optimise scheduling."
        ),
        "category": "Behaviour",
        "icon": "📅",
        "base_saving_inr": 130,
        "base_co2_kg": 5.0,
        "base_priority": 55,
        "trigger": "high_weekend_vs_weekday",
    },
    {
        "id": "fridge_maintenance",
        "title": "Clean Refrigerator Coils",
        "description": (
            "Dirty condenser coils force your refrigerator to run 15–30% harder. "
            "Clean them every 6 months to maintain efficiency."
        ),
        "category": "Appliance",
        "icon": "🧊",
        "base_saving_inr": 95,
        "base_co2_kg": 3.7,
        "base_priority": 45,
        "trigger": "always",
    },
    {
        "id": "peak_hour_shift",
        "title": "Shift High-Power Tasks Out of Peak Hours",
        "description": (
            "Dishwashers, EV chargers, and ovens used during 6–10 PM peak hours "
            "attract premium tariffs. Shift these to before 6 PM or after 10 PM."
        ),
        "category": "Behaviour",
        "icon": "⏰",
        "base_saving_inr": 200,
        "base_co2_kg": 7.7,
        "base_priority": 72,
        "trigger": "high_evening_usage",
    },
]


class RecommendationEngine:
    """
    Analyses consumption patterns and returns ranked, personalised recommendations.
    """

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        self.emission_factor: float = cfg["co2"]["emission_factor_kg_per_kwh"]
        self.currency: str = cfg["billing"]["currency"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, df: pd.DataFrame) -> list[Recommendation]:
        """
        Analyse the hourly consumption DataFrame and return a ranked list
        of Recommendation objects.

        Parameters
        ----------
        df : clean hourly DataFrame (must include 'Global_active_power')
        """
        signals = self._extract_signals(df)
        recs = []
        for item in CATALOGUE:
            rec = self._evaluate(item, signals)
            if rec.applicable:
                recs.append(rec)

        # Sort by priority descending
        recs.sort(key=lambda r: r.priority_score, reverse=True)
        return recs

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_signals(self, df: pd.DataFrame) -> dict:
        """Compute aggregate signals used to trigger recommendations."""
        gp = df["Global_active_power"]
        hourly_mean = gp.mean()

        by_hour = df.groupby(df.index.hour)["Global_active_power"].mean()
        evening_mean = by_hour.loc[by_hour.index.isin(range(18, 22))].mean()
        night_mean = by_hour.loc[by_hour.index.isin(range(0, 6))].mean()

        weekday_mean = df[df.index.dayofweek < 5]["Global_active_power"].mean()
        weekend_mean = df[df.index.dayofweek >= 5]["Global_active_power"].mean()

        sm2_evening = 0.0
        if "Sub_metering_2" in df.columns:
            sm2_evening = (
                df[df.index.hour.isin(range(18, 22))]["Sub_metering_2"].mean()
            )

        return {
            "hourly_mean": hourly_mean,
            "evening_mean": evening_mean,
            "night_mean": night_mean,
            "weekday_mean": weekday_mean,
            "weekend_mean": weekend_mean,
            "sm2_evening": sm2_evening,
            "high_overall_usage": hourly_mean > 1.0,
            "high_evening_usage": evening_mean > hourly_mean * 1.3,
            "high_night_baseline": night_mean > 0.4,
            "high_weekend_vs_weekday": weekend_mean > weekday_mean * 1.25,
            "high_submeter2_evening": sm2_evening > 50,
        }

    def _evaluate(self, item: dict, signals: dict) -> Recommendation:
        trigger = item["trigger"]
        applicable = True

        # Check trigger condition
        if trigger != "always" and trigger != "hvac_always":
            applicable = signals.get(trigger, False)

        # Scale saving by actual vs baseline usage
        scale = max(0.5, min(2.0, signals["hourly_mean"] / 1.0))
        saving = round(item["base_saving_inr"] * scale)
        co2 = round(item["base_co2_kg"] * scale, 1)
        priority = item["base_priority"] * (scale ** 0.5)

        evidence = self._build_evidence(trigger, signals)

        return Recommendation(
            id=item["id"],
            title=item["title"],
            description=item["description"],
            category=item["category"],
            icon=item["icon"],
            estimated_monthly_saving_inr=saving,
            estimated_co2_saved_kg=co2,
            priority_score=round(priority, 1),
            applicable=applicable,
            evidence=evidence,
        )

    @staticmethod
    def _build_evidence(trigger: str, signals: dict) -> str:
        evidence_map = {
            "high_evening_usage": f"Evening avg {signals.get('evening_mean', 0):.2f} kW vs overall {signals.get('hourly_mean', 0):.2f} kW",
            "high_night_baseline": f"Night baseline: {signals.get('night_mean', 0):.2f} kW",
            "high_weekend_vs_weekday": f"Weekend {signals.get('weekend_mean', 0):.2f} kW vs weekday {signals.get('weekday_mean', 0):.2f} kW",
            "high_submeter2_evening": f"Laundry evening avg: {signals.get('sm2_evening', 0):.1f} Wh",
            "high_overall_usage": f"Overall avg: {signals.get('hourly_mean', 0):.2f} kW",
        }
        return evidence_map.get(trigger, "")
