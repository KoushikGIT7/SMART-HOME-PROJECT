"""
Smart Grid Time-of-Use (ToU) & Solar Microgrid Optimizer
========================================================
Pure software optimization algorithms for appliance load shifting,
peak demand shaving, dynamic 3-tier tariff arbitrage, and 24-hour
rooftop solar PV + battery storage (BESS) dispatch simulation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


@dataclass
class DeferrableTask:
    name: str
    duration_hours: int
    power_kw: float
    preferred_earliest_hour: int
    preferred_latest_hour: int


class SmartGridOptimizer:
    """Solves load-shifting and microgrid dispatch optimization."""

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}
        # 3-Tier Time-of-Use (ToU) Tariff (₹/kWh)
        # Peak: 18:00 - 22:00 (₹9.50/kWh)
        # Standard: 06:00 - 18:00 (₹6.50/kWh)
        # Off-Peak: 22:00 - 06:00 (₹3.50/kWh)
        self.hourly_tariffs = self._build_hourly_tariff_array()

    def _build_hourly_tariff_array(self) -> np.ndarray:
        tariffs = np.zeros(24)
        for h in range(24):
            if 18 <= h < 22:
                tariffs[h] = 9.50
            elif 6 <= h < 18:
                tariffs[h] = 6.50
            else:
                tariffs[h] = 3.50
        return tariffs

    def get_default_tasks(self) -> List[DeferrableTask]:
        return [
            DeferrableTask("EV Charging (Level 2)", duration_hours=4, power_kw=3.3, preferred_earliest_hour=18, preferred_latest_hour=7),
            DeferrableTask("Washing Machine + Dryer", duration_hours=2, power_kw=1.2, preferred_earliest_hour=19, preferred_latest_hour=23),
            DeferrableTask("Smart Dishwasher Cycle", duration_hours=2, power_kw=1.1, preferred_earliest_hour=20, preferred_latest_hour=24),
            DeferrableTask("Heat Pump Water Pre-heat", duration_hours=1, power_kw=2.2, preferred_earliest_hour=18, preferred_latest_hour=22),
        ]

    def optimize_appliance_schedule(
        self,
        tasks: List[DeferrableTask],
        base_load_profile: np.ndarray | None = None,
    ) -> dict:
        """Computes optimal start hour for each task to minimize total electricity cost."""
        if base_load_profile is None:
            # Typical household baseline profile (kW)
            base_load_profile = np.array([
                0.4, 0.35, 0.35, 0.35, 0.4, 0.6,
                1.2, 1.8, 1.4, 1.1, 0.9, 0.9,
                1.0, 0.9, 0.85, 0.9, 1.1, 1.5,
                2.4, 2.8, 2.6, 2.2, 1.4, 0.7
            ])

        # Baseline unmanaged: All tasks start around 18:00 - 20:00 (Peak time)
        unmanaged_load = base_load_profile.copy()
        unmanaged_cost = float(np.sum(unmanaged_load * self.hourly_tariffs))
        task_unmanaged_starts = {}

        # Default unmanaged start hours
        default_unmanaged = [19, 19, 20, 18]
        for idx, task in enumerate(tasks):
            start = default_unmanaged[idx % len(default_unmanaged)]
            task_unmanaged_starts[task.name] = start
            for h in range(start, start + task.duration_hours):
                unmanaged_load[h % 24] += task.power_kw

        unmanaged_total_cost = float(np.sum(unmanaged_load * self.hourly_tariffs))

        # Optimized schedule: Pick start hour in off-peak window (22:00 - 05:00) that minimizes cost and peak kW
        optimized_load = base_load_profile.copy()
        task_optimal_starts = {}

        for task in tasks:
            best_hour = 23
            lowest_cost = float("inf")
            # Search possible start hours
            search_hours = [22, 23, 0, 1, 2, 3, 4]
            for h in search_hours:
                # Calculate cost of running task starting at hour h
                hours_active = [(h + offset) % 24 for offset in range(task.duration_hours)]
                task_cost = sum(task.power_kw * self.hourly_tariffs[hr] for hr in hours_active)
                # Penalty for creating peak above 3.5 kW
                peak_penalty = max(0.0, np.max(optimized_load[hours_active] + task.power_kw) - 3.5) * 5.0
                total_eval = task_cost + peak_penalty

                if total_eval < lowest_cost:
                    lowest_cost = total_eval
                    best_hour = h

            task_optimal_starts[task.name] = best_hour
            for offset in range(task.duration_hours):
                optimized_load[(best_hour + offset) % 24] += task.power_kw

        optimized_total_cost = float(np.sum(optimized_load * self.hourly_tariffs))
        savings_day = unmanaged_total_cost - optimized_total_cost
        savings_month = savings_day * 30
        savings_pct = (savings_day / unmanaged_total_cost * 100) if unmanaged_total_cost > 0 else 0.0

        peak_kw_unmanaged = float(np.max(unmanaged_load))
        peak_kw_optimized = float(np.max(optimized_load))
        peak_reduction_pct = ((peak_kw_unmanaged - peak_kw_optimized) / peak_kw_unmanaged * 100) if peak_kw_unmanaged > 0 else 0.0

        return {
            "unmanaged_load": unmanaged_load,
            "optimized_load": optimized_load,
            "hourly_tariffs": self.hourly_tariffs,
            "unmanaged_cost_day": unmanaged_total_cost,
            "optimized_cost_day": optimized_total_cost,
            "savings_day": savings_day,
            "savings_month": savings_month,
            "savings_pct": savings_pct,
            "peak_kw_unmanaged": peak_kw_unmanaged,
            "peak_kw_optimized": peak_kw_optimized,
            "peak_reduction_pct": peak_reduction_pct,
            "task_unmanaged_starts": task_unmanaged_starts,
            "task_optimal_starts": task_optimal_starts,
        }

    def simulate_microgrid_24h(
        self,
        solar_pv_kwp: float = 4.5,
        battery_capacity_kwh: float = 10.0,
        battery_max_kw: float = 3.0,
        feed_in_tariff: float = 4.20,
    ) -> dict:
        """Simulates 24-hour solar generation, battery charging/discharging, and net-metering economics."""
        hours = np.arange(24)
        # Solar irradiance curve (peaks at 12:00)
        solar_profile = np.zeros(24)
        for h in range(24):
            if 6 <= h <= 18:
                solar_profile[h] = solar_pv_kwp * (math.sin(math.pi * (h - 6) / 12) ** 1.4)

        # Baseline home load profile
        load_profile = np.array([
            0.5, 0.4, 0.4, 0.4, 0.5, 0.7,
            1.4, 2.1, 1.8, 1.5, 1.3, 1.2,
            1.4, 1.3, 1.2, 1.3, 1.6, 2.2,
            3.4, 3.8, 3.5, 2.8, 1.6, 0.9
        ])

        # Battery dispatch simulation
        soc = 0.3 * battery_capacity_kwh  # Start at 30% state-of-charge
        soc_curve = np.zeros(24)
        battery_flow = np.zeros(24)  # Positive = charging, Negative = discharging
        grid_import = np.zeros(24)
        grid_export = np.zeros(24)

        for h in range(24):
            net_power = solar_profile[h] - load_profile[h]

            if net_power > 0:
                # Solar surplus: charge battery first, export remainder
                charge_space = battery_capacity_kwh - soc
                charge_kw = min(net_power, battery_max_kw, charge_space)
                soc += charge_kw * 0.94  # 94% charging efficiency
                battery_flow[h] = charge_kw
                export_kw = net_power - charge_kw
                grid_export[h] = max(0.0, export_kw)
                grid_import[h] = 0.0
            else:
                # Deficit: discharge battery during peak hours (especially evening)
                deficit = abs(net_power)
                available_discharge = soc - (0.10 * battery_capacity_kwh)  # 10% reserve
                if available_discharge > 0 and (h >= 17 or h <= 22):
                    discharge_kw = min(deficit, battery_max_kw, available_discharge)
                    soc -= discharge_kw / 0.94  # Efficiency penalty
                    battery_flow[h] = -discharge_kw
                    unmet = deficit - discharge_kw
                    grid_import[h] = max(0.0, unmet)
                else:
                    grid_import[h] = deficit

            soc_curve[h] = soc

        total_solar_kwh = float(np.sum(solar_profile))
        total_load_kwh = float(np.sum(load_profile))
        total_import_kwh = float(np.sum(grid_import))
        total_export_kwh = float(np.sum(grid_export))

        # Financials
        standard_grid_cost = float(np.sum(load_profile * self.hourly_tariffs))
        net_import_cost = float(np.sum(grid_import * self.hourly_tariffs))
        export_revenue = total_export_kwh * feed_in_tariff
        effective_daily_cost = net_import_cost - export_revenue

        daily_savings = standard_grid_cost - effective_daily_cost
        monthly_savings = daily_savings * 30
        self_sufficiency_pct = ((total_load_kwh - total_import_kwh) / total_load_kwh * 100) if total_load_kwh > 0 else 0.0
        co2_avoided_kg = (total_solar_kwh + np.sum(np.abs(battery_flow[battery_flow < 0]))) * 0.82

        return {
            "hours": hours,
            "solar_profile": solar_profile,
            "load_profile": load_profile,
            "soc_curve": soc_curve,
            "soc_pct_curve": (soc_curve / battery_capacity_kwh) * 100,
            "battery_flow": battery_flow,
            "grid_import": grid_import,
            "grid_export": grid_export,
            "total_solar_kwh": total_solar_kwh,
            "total_load_kwh": total_load_kwh,
            "total_import_kwh": total_import_kwh,
            "total_export_kwh": total_export_kwh,
            "standard_cost": standard_grid_cost,
            "net_cost": effective_daily_cost,
            "daily_savings": daily_savings,
            "monthly_savings": monthly_savings,
            "self_sufficiency_pct": self_sufficiency_pct,
            "co2_avoided_kg": co2_avoided_kg,
        }
