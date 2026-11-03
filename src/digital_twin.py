"""
Smart Home Digital Twin — 100% Software-Based Home & Appliance Simulation
========================================================================
Simulates real-time appliance states, room-by-room electrical and water
telemetry, dynamic fault injections, and automated self-healing mitigation.
Requires ZERO physical hardware or IoT devices.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ApplianceState:
    id: str
    name: str
    room: str
    icon: str
    category: str  # hvac, kitchen, utility, garage, solar
    is_on: bool
    rated_watts: float
    actual_watts: float = 0.0
    power_factor: float = 0.95
    is_deferrable: bool = False
    is_faulted: bool = False
    fault_type: Optional[str] = None
    fault_description: Optional[str] = None


class DigitalTwinEngine:
    """Pure software simulation of a connected smart home."""

    def __init__(self, config: Optional[dict] = None) -> None:
        self.config = config or {}
        self.tariff_rate = 6.50  # ₹/kWh default standard
        self.co2_factor = 0.82    # kg CO2/kWh
        self.appliances: Dict[str, ApplianceState] = self._init_appliances()
        self.active_faults: List[str] = []
        self.water_base_lph: float = 8.5  # litres per hour base
        self.water_leak_lph: float = 0.0

    def _init_appliances(self) -> Dict[str, ApplianceState]:
        return {
            # Living Room
            "living_ac": ApplianceState(
                id="living_ac",
                name="Inverter Split AC (1.5 Ton)",
                room="Living Room",
                icon="❄️",
                category="hvac",
                is_on=True,
                rated_watts=1400.0,
                power_factor=0.92,
                is_deferrable=False,
            ),
            "living_tv": ApplianceState(
                id="living_tv",
                name="65\" OLED TV & Soundbar",
                room="Living Room",
                icon="📺",
                category="entertainment",
                is_on=True,
                rated_watts=160.0,
                power_factor=0.97,
            ),
            "living_lights": ApplianceState(
                id="living_lights",
                name="Smart Ambient LED Array",
                room="Living Room",
                icon="💡",
                category="lighting",
                is_on=True,
                rated_watts=65.0,
                power_factor=0.98,
            ),
            # Kitchen
            "kitchen_fridge": ApplianceState(
                id="kitchen_fridge",
                name="Double-Door Refrigerator",
                room="Kitchen",
                icon="🧊",
                category="kitchen",
                is_on=True,
                rated_watts=220.0,
                power_factor=0.88,
            ),
            "kitchen_hob": ApplianceState(
                id="kitchen_hob",
                name="Induction Hob / Microwave",
                room="Kitchen",
                icon="🍳",
                category="kitchen",
                is_on=False,
                rated_watts=1800.0,
                power_factor=0.96,
            ),
            "kitchen_dishwasher": ApplianceState(
                id="kitchen_dishwasher",
                name="Smart Dishwasher",
                room="Kitchen",
                icon="🍽️",
                category="kitchen",
                is_on=False,
                rated_watts=1200.0,
                power_factor=0.91,
                is_deferrable=True,
            ),
            # Utility Room
            "utility_geyser": ApplianceState(
                id="utility_geyser",
                name="Instant Geyser / Water Heater",
                room="Utility Room",
                icon="🚿",
                category="utility",
                is_on=False,
                rated_watts=2400.0,
                power_factor=0.99,
                is_deferrable=True,
            ),
            "utility_washer": ApplianceState(
                id="utility_washer",
                name="Front-Load Washing Machine",
                room="Utility Room",
                icon="🧺",
                category="utility",
                is_on=False,
                rated_watts=950.0,
                power_factor=0.89,
                is_deferrable=True,
            ),
            # Garage / Microgrid
            "garage_ev": ApplianceState(
                id="garage_ev",
                name="Level-2 EV Smart Charger",
                room="Garage",
                icon="🚗",
                category="garage",
                is_on=False,
                rated_watts=3300.0,
                power_factor=0.99,
                is_deferrable=True,
            ),
            "solar_pv": ApplianceState(
                id="solar_pv",
                name="Rooftop Solar Array (4.5 kWp)",
                room="Rooftop",
                icon="☀️",
                category="solar",
                is_on=True,
                rated_watts=-2800.0,  # Negative power = generation
                power_factor=1.00,
            ),
            "bess_battery": ApplianceState(
                id="bess_battery",
                name="Home Battery Storage (10 kWh)",
                room="Garage",
                icon="🔋",
                category="battery",
                is_on=True,
                rated_watts=0.0,  # Charge/discharge determined dynamically
                power_factor=0.98,
            ),
        }

    def set_appliance_state(self, app_id: str, is_on: bool) -> None:
        if app_id in self.appliances:
            self.appliances[app_id].is_on = is_on

    def set_ac_setpoint(self, temp_c: float) -> None:
        """Higher setpoint consumes less power (approx 6% per degree)."""
        if "living_ac" in self.appliances:
            base = 1400.0
            # 24C is baseline. 18C is +36% draw, 26C is -12% draw.
            delta = 24.0 - temp_c
            scale = max(0.5, 1.0 + delta * 0.06)
            self.appliances["living_ac"].rated_watts = base * scale

    def inject_fault(self, fault_key: str) -> dict:
        """Software-injected fault simulation for live demonstration."""
        if fault_key == "ac_compressor_failure":
            ac = self.appliances["living_ac"]
            ac.is_on = True
            ac.is_faulted = True
            ac.fault_type = "Mechanical Seizure / Locked Rotor"
            ac.fault_description = "AC compressor motor locked rotor draw: 3,900W with severe reactive lag (PF 0.61)."
            ac.actual_watts = 3900.0
            ac.power_factor = 0.61
            if fault_key not in self.active_faults:
                self.active_faults.append(fault_key)
            return {
                "fault": fault_key,
                "title": "🚨 CRITICAL: AC Compressor Failure",
                "severity": "critical",
                "loss_rate": "₹25.35 / hr",
                "details": ac.fault_description,
                "action": "Trip virtual smart circuit breaker to prevent cable thermal damage.",
            }

        elif fault_key == "water_pipe_rupture":
            self.water_leak_lph = 145.0
            if fault_key not in self.active_faults:
                self.active_faults.append(fault_key)
            return {
                "fault": fault_key,
                "title": "🚨 CRITICAL: Main Water Pipe Burst",
                "severity": "critical",
                "loss_rate": "145 Litres / hr (₹0.87 / hr + Structural Risk)",
                "details": "High continuous water flow detected outside peak morning/evening demand windows.",
                "action": "Trigger solenoid auto-shutoff valve on main inlet line.",
            }

        elif fault_key == "vampire_load":
            if fault_key not in self.active_faults:
                self.active_faults.append(fault_key)
            return {
                "fault": fault_key,
                "title": "⚠️ WARNING: Phantom / Vampire Drain",
                "severity": "warning",
                "loss_rate": "480 W (₹3.12 / hr continuously)",
                "details": "Standby equipment and faulty power bricks drawing 480W unmonitored during sleep cycle.",
                "action": "Enable Night Eco Isolation on non-essential sockets.",
            }

        elif fault_key == "ev_grid_peak_violation":
            ev = self.appliances["garage_ev"]
            ev.is_on = True
            ev.rated_watts = 7200.0  # Full rapid Level-2 charge
            if fault_key not in self.active_faults:
                self.active_faults.append(fault_key)
            return {
                "fault": fault_key,
                "title": "⚠️ PEAK OVERLOAD: EV Fast Charge During Peak Tariff",
                "severity": "warning",
                "loss_rate": "₹68.40 / hr (Surcharge Tier)",
                "details": "High-current EV charging coinciding with peak evening grid tariff window (₹9.50/kWh).",
                "action": "Shift charging cycle to Off-Peak window (11:00 PM) via Smart Grid Scheduler.",
            }

        return {}

    def auto_mitigate_fault(self, fault_key: str) -> dict:
        """1-click self-healing smart mitigation."""
        if fault_key in self.active_faults:
            self.active_faults.remove(fault_key)

        if fault_key == "ac_compressor_failure":
            ac = self.appliances["living_ac"]
            ac.is_faulted = False
            ac.fault_type = None
            ac.fault_description = None
            ac.is_on = False  # Trip breaker
            ac.actual_watts = 0.0
            ac.power_factor = 0.92
            return {
                "status": "success",
                "title": "🛡️ Auto-Mitigation Successful: AC Breaker Tripped",
                "message": "Virtual smart relay successfully isolated the faulted AC circuit. Household load restored to normal operating safety band.",
                "saved_per_hr": "₹25.35/hr",
            }

        elif fault_key == "water_pipe_rupture":
            self.water_leak_lph = 0.0
            return {
                "status": "success",
                "title": "🛡️ Auto-Mitigation Successful: Main Valve Closed",
                "message": "Software-driven motorized ball valve actuated. Water leak halted instantly. Zero further wastage.",
                "saved_per_hr": "145 L/hr saved",
            }

        elif fault_key == "vampire_load":
            return {
                "status": "success",
                "title": "🛡️ Auto-Mitigation Successful: Standby Cutoff Engaged",
                "message": "Smart sub-meter isolated vampire loads on standby entertainment and peripheral circuits.",
                "saved_per_hr": "₹3.12/hr",
            }

        elif fault_key == "ev_grid_peak_violation":
            ev = self.appliances["garage_ev"]
            ev.is_on = False  # Deferred to 11 PM
            ev.rated_watts = 3300.0
            return {
                "status": "success",
                "title": "🛡️ Auto-Mitigation Successful: Load Shift Scheduled",
                "message": "EV charging paused and rescheduled for off-peak super-saver window (11:00 PM @ ₹3.50/kWh). Peak grid demand reduced by 7.2 kW.",
                "saved_per_hr": "₹43.20/charge cycle",
            }

        return {"status": "error", "message": "Unknown fault key."}

    def clear_all_faults(self) -> None:
        """Reset all active faults."""
        for fault in list(self.active_faults):
            self.auto_mitigate_fault(fault)
        self.active_faults = []

    def get_telemetry(self, solar_output_factor: float = 0.7) -> dict:
        """Calculate live multi-variable home telemetry."""
        gross_watts = 0.0
        reactive_vars = 0.0

        for app_id, app in self.appliances.items():
            if app_id in ["solar_pv", "bess_battery"]:
                continue

            if app.is_on:
                if app.is_faulted and app.actual_watts > 0:
                    w = app.actual_watts
                else:
                    # Minor micro-jitter (±1.5%) for realism
                    jitter = random.uniform(0.985, 1.015)
                    w = app.rated_watts * jitter

                gross_watts += w
                # Q = P * tan(acos(PF))
                pf = max(0.1, min(0.999, app.power_factor))
                q = w * math.tan(math.acos(pf))
                reactive_vars += q

        # Add vampire load if active
        if "vampire_load" in self.active_faults:
            gross_watts += 480.0
            reactive_vars += 220.0

        # Rooftop Solar Generation
        solar_app = self.appliances["solar_pv"]
        if solar_app.is_on:
            solar_generation_w = abs(solar_app.rated_watts) * solar_output_factor
        else:
            solar_generation_w = 0.0

        # Net Grid Active Power
        net_watts = gross_watts - solar_generation_w
        grid_active_kw = max(0.0, net_watts / 1000.0)
        grid_export_kw = max(0.0, -net_watts / 1000.0)

        # Net Power Factor
        apparent_va = math.sqrt((gross_watts ** 2) + (reactive_vars ** 2))
        composite_pf = (gross_watts / apparent_va) if apparent_va > 0 else 0.98

        # Simulated Grid Voltage (nominal 230V with slight dynamic sag on high load)
        voltage_drop = (gross_watts / 1000.0) * 0.8
        live_voltage = round(230.5 - voltage_drop + random.uniform(-0.4, 0.4), 1)

        # Current (Amps) = P / (V * PF)
        live_amps = round((gross_watts / (live_voltage * composite_pf)), 2) if live_voltage > 0 else 0.0

        # Cost & Carbon rates
        cost_per_hr = grid_active_kw * self.tariff_rate
        co2_g_per_min = (grid_active_kw * self.co2_factor * 1000.0) / 60.0

        # Water telemetry
        live_water_lph = self.water_base_lph + self.water_leak_lph + random.uniform(-0.5, 0.5)

        # Anomaly Status
        is_abnormal = (
            len(self.active_faults) > 0
            or gross_watts > 5000.0
            or composite_pf < 0.80
            or self.water_leak_lph > 10.0
        )

        return {
            "gross_kw": round(gross_watts / 1000.0, 3),
            "solar_kw": round(solar_generation_w / 1000.0, 3),
            "net_grid_kw": round(grid_active_kw, 3),
            "export_kw": round(grid_export_kw, 3),
            "reactive_kvar": round(reactive_vars / 1000.0, 3),
            "power_factor": round(composite_pf, 2),
            "voltage_v": live_voltage,
            "current_a": live_amps,
            "cost_inr_hr": round(cost_per_hr, 2),
            "co2_g_min": round(co2_g_per_min, 1),
            "water_lph": round(live_water_lph, 1),
            "is_water_leak": self.water_leak_lph > 10.0,
            "is_anomaly": is_abnormal,
            "active_faults": list(self.active_faults),
        }
