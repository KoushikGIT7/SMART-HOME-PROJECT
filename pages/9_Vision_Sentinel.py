"""
Page 9: AI Vision Occupancy & Energy Waste Sentinel
===================================================
100% Software-based Computer Vision module using OpenCV.
Detects room occupants, correlates presence with active appliance load,
and flags ghost/vampire energy waste in unoccupied rooms with 1-click eco-cutoff.
Includes pre-built simulated surveillance feeds + optional webcam input.
"""

from __future__ import annotations

import sys
sys.path.insert(0, ".")

import cv2
import numpy as np
from PIL import Image
import streamlit as st

from app import (
    inject_global_css,
    load_config_cached,
    render_sidebar,
)
from src.vision_detector import VisionSentinelEngine

st.set_page_config(
    page_title="Vision Sentinel · Smart Home AI",
    page_icon="👁️",
    layout="wide",
)
inject_global_css()
render_sidebar()

cfg = load_config_cached()
sentinel = VisionSentinelEngine(cfg)

st.markdown(
    """
    <div class='page-title'>👁️ AI Vision Occupancy & Energy Waste Sentinel</div>
    <div class='page-subtitle'>
        100% Software-Based Edge Vision · Real-Time Occupancy Correlation & Vampire Waste Auto-Cutoff
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Mode Selector ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>🎥 Smart Camera Feed Selection</div>", unsafe_allow_html=True)
col_mode, col_load = st.columns([2, 1])

with col_mode:
    feed_mode = st.radio(
        "Surveillance Feed Source:",
        [
            "🖥️ Simulated Preset: Empty Room (HVAC & Lights Left ON)",
            "🖥️ Simulated Preset: Occupied Room (1 Person)",
            "🖥️ Simulated Preset: Occupied Room (Family 2 Persons)",
            "📷 Live Laptop Webcam Feed (Optional)",
        ],
        index=0,
        horizontal=False,
    )

with col_load:
    # State for virtual room load
    if "vision_room_load" not in st.session_state:
        st.session_state.vision_room_load = 1465.0

    room_load = st.number_input(
        "Active Room Load (Watts):",
        min_value=50.0,
        max_value=4000.0,
        value=float(st.session_state.vision_room_load),
        step=50.0,
        help="Simulated combined electrical draw of Living Room AC, TV, and lighting",
    )
    st.session_state.vision_room_load = room_load

# ─── Frame Acquisition & Processing ───────────────────────────────────────────
frame_rgb = None
scenario_key = None

if "Empty Room" in feed_mode:
    scenario_key = "empty_room"
    frame_rgb = sentinel.create_simulated_frame("empty_room")
elif "1 Person" in feed_mode:
    scenario_key = "occupied_single"
    frame_rgb = sentinel.create_simulated_frame("occupied_single")
elif "Family" in feed_mode:
    scenario_key = "occupied_family"
    frame_rgb = sentinel.create_simulated_frame("occupied_family")
elif "Live Laptop Webcam" in feed_mode:
    camera_pic = st.camera_input("Capture frame from your laptop webcam:")
    if camera_pic is not None:
        pil_img = Image.open(camera_pic)
        frame_rgb = np.array(pil_img)
    else:
        st.info("👆 Allow browser camera permission above or snap a frame to test with your actual webcam.")
        frame_rgb = sentinel.create_simulated_frame("empty_room")
        scenario_key = "empty_room"

annotated_img, occupant_count, detections = sentinel.process_frame(
    frame_rgb,
    scenario_preset=scenario_key,
)

# ─── Display Frame & Telemetry ─────────────────────────────────────────────────
col_cam, col_telemetry = st.columns([3, 2])

with col_cam:
    st.image(
        annotated_img,
        caption=f"AI Vision Analytics HUD · Detected Occupants: {occupant_count}",
        use_container_width=True,
    )

waste_eval = sentinel.evaluate_energy_waste(
    occupancy_count=occupant_count,
    active_room_watts=room_load,
    tariff_rate=6.50,
)

with col_telemetry:
    st.markdown("<div class='section-header'>Telemetry & Occupancy Correlation</div>", unsafe_allow_html=True)

    status_badge_class = "bad" if waste_eval["status"] == "waste_detected" else "good"
    status_label = "🚨 ZERO OCCUPANCY WASTE" if waste_eval["status"] == "waste_detected" else "✅ OPTIMAL CORRELATION"

    st.markdown(
        f"""
        <div class='kpi-card' style='border-color: {"#ff4444" if waste_eval["status"] == "waste_detected" else "#00ff88"};'>
            <div class='kpi-title'>Vision Status</div>
            <div class='kpi-value' style='font-size:1.6rem;'>{occupant_count} <span style='font-size:1rem; color:#94a3b8;'>Occupants</span></div>
            <div class='kpi-sub'>Room Active Load: {room_load:.0f} W</div>
            <div class='kpi-badge {status_badge_class}' style='margin-top:0.6rem;'>{status_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if waste_eval["status"] == "waste_detected":
        st.markdown(
            f"""
            <div style='background:rgba(255,68,68,0.1); border-left:4px solid #ff4444; padding:0.9rem; border-radius:8px; margin-bottom:1rem;'>
                <b style='color:#ff4444;'>Vampire Energy Drain:</b><br>
                <span style='color:#e2e8f0; font-size:0.85rem;'>
                    Room is completely empty but appliances are consuming <b>{waste_eval['wasted_kw']} kW</b>.<br>
                    • Continuous loss rate: <b>₹{waste_eval['cost_per_hr']}/hr</b><br>
                    • Carbon penalty: <b>{waste_eval['co2_per_hr']} kg CO₂/hr</b><br>
                    • Projected monthly waste: <b>₹{waste_eval['monthly_risk_inr']:,.0f}/month</b>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⚡ Execute AI Automated Eco-Cutoff", key="btn_eco_cutoff", use_container_width=True):
            st.session_state.vision_room_load = 65.0  # Cut down to idle standby
            st.success("🛡️ Eco-Cutoff Action Deployed! Powered down AC and active lighting. Power dropped to 65W idle.")
            st.rerun()
    else:
        st.markdown(
            """
            <div style='background:rgba(0,255,136,0.08); border-left:4px solid #00ff88; padding:0.9rem; border-radius:8px;'>
                <b style='color:#00ff88;'>Human Activity Verified:</b><br>
                <span style='color:#e2e8f0; font-size:0.85rem;'>
                    Vision sentinel confirms active presence in the zone. HVAC and lighting energy draw is justified by human occupancy.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.markdown(
    """
    <div style='font-size:0.82rem; color:#64748b;'>
        💡 <b>Viva Demonstration Note:</b> This module demonstrates multi-modal Edge AI (Computer Vision + Energy Analytics).
        It proves to examiners that the smart home doesn't just passively track electricity meters, but actively senses occupant context
        to eliminate ghost/vampire power waste autonomously. 100% software-emulated with zero external IoT hardware required.
    </div>
    """,
    unsafe_allow_html=True,
)
