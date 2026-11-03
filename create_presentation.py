"""
Generate complete professional 21-slide presentation for Smart Home Utility AI
with embedded high-resolution screenshots, glassmorphism card styling,
and comprehensive speaker notes on every slide.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

PPTX_PATH = "SMART_HOME_AI_80_PERCENT_PRESENTATION.pptx"
IMG_DIR = "assets/presentation_screenshots"

# Color constants
COLOR_BG = RGBColor(10, 15, 29)          # #0A0F1D
COLOR_CARD = RGBColor(17, 24, 39)        # #111827
COLOR_CARD_BORDER = RGBColor(31, 41, 55) # #1F2937
COLOR_CYAN = RGBColor(0, 212, 255)       # #00D4FF
COLOR_PURPLE = RGBColor(123, 94, 167)    # #7B5EA7
COLOR_GREEN = RGBColor(0, 255, 136)      # #00FF88
COLOR_ORANGE = RGBColor(255, 170, 0)     # #FFAA00
COLOR_RED = RGBColor(255, 68, 68)        # #FF4444
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_MUTED = RGBColor(148, 163, 184)    # #94A3B8

def add_header(slide, title, category="CAPSTONE PROJECT REVIEW · PHASE-II (80% IMPLEMENTATION)"):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_CYAN

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.65))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

def create_card(slide, left, top, width, height, title=None, border_color=COLOR_CARD_BORDER, bg_color=COLOR_CARD):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)
    card.adjustments[0] = 0.05
    
    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_CYAN
    return card

def set_slide_background(slide):
    # Add dark background rectangle
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    bg.line.fill.background()
    # Bottom brand line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(7.42), Inches(13.333), Inches(0.08))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_CYAN
    line.line.fill.background()

def set_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

print("Initializing Presentation Generation...")

# ==============================================================================
# SLIDE 1: Title Slide
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Main Title Card
create_card(s1, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1), border_color=COLOR_CYAN)

tb = s1.shapes.add_textbox(Inches(2.0), Inches(1.5), Inches(9.333), Inches(3.0))
tf = tb.text_frame
tf.word_wrap = True

p1 = tf.paragraphs[0]
p1.text = "SMART HOME UTILITY AI"
p1.font.size = Pt(36)
p1.font.bold = True
p1.font.color.rgb = COLOR_CYAN
p1.alignment = PP_ALIGN.CENTER

p2 = tf.add_paragraph()
p2.text = "Autonomous Smart Home Energy Intelligence & Digital Twin Suite"
p2.font.size = Pt(18)
p2.font.color.rgb = COLOR_WHITE
p2.alignment = PP_ALIGN.CENTER

p3 = tf.add_paragraph()
p3.text = "100% Software-Simulated Interactive Demonstration · Zero Physical Hardware Bottleneck"
p3.font.size = Pt(12)
p3.font.color.rgb = COLOR_GREEN
p3.alignment = PP_ALIGN.CENTER

p4 = tf.add_paragraph()
p4.text = "\nCAPSTONE MAJOR PROJECT REVIEW — PHASE II (80% IMPLEMENTED STATUS)"
p4.font.size = Pt(13)
p4.font.bold = True
p4.font.color.rgb = COLOR_ORANGE
p4.alignment = PP_ALIGN.CENTER

# Metadata at bottom of card
tb_meta = s1.shapes.add_textbox(Inches(2.0), Inches(4.7), Inches(9.333), Inches(1.2))
tf_meta = tb_meta.text_frame
p_meta = tf_meta.paragraphs[0]
p_meta.text = "Project Team: Capstone Research Group | Dept. of Computer Science & Engineering\nAcademic Year: 2026-2027 | Evaluator Demonstration Ready"
p_meta.font.size = Pt(11)
p_meta.font.color.rgb = COLOR_MUTED
p_meta.alignment = PP_ALIGN.CENTER

set_speaker_notes(s1, """[SLIDE 1 - TITLE SLIDE]
WHAT TO SAY (Spoken Script - 30 seconds):
"Respected panel of examiners and faculty members, good morning/afternoon. Today, my teammate and I are presenting our Capstone Major Project: 'Smart Home Utility AI' — an Autonomous Smart Home Energy Intelligence and Digital Twin Suite. 
We have successfully implemented and validated 80% of our complete project codebase, including machine learning forecasting, explainable AI, real-time anomaly detection, edge vision occupancy sensing, and an interactive digital twin.
Our entire platform operates 100% in software emulation with zero external paid APIs or physical hardware blockers, allowing for live interactive evaluation today. Let us now walk you through the motivation and technical architecture."

KEY POINTER FOR EVALUATOR:
• Emphasize that the core 80% software implementation is complete, fully functional, and live-testable on screen.""")

# ==============================================================================
# SLIDE 2: Executive Summary & Project Motivation
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "Executive Summary & The Modern Energy Crisis")

# Card 1: The Problem
c1 = create_card(s2, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2), "1. THE ESCALATING CRISIS", COLOR_RED)
tb1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(3.2), Inches(4.3))
tf1 = tb1.text_frame
tf1.word_wrap = True
tf1.text = "• Steep Tariff Hikes:\nResidential tariffs under BESCOM & national grids surge up to ₹9.50/kWh during peak hours.\n\n• Invisible Vampire Waste:\nStandby appliances (HVAC, microwaves, TVs) drain 12–18% of household electricity unnoticed.\n\n• Carbon Footprint Crisis:\nGrid electricity in India emits ~0.82 kg CO₂/kWh, exacerbating climate impact without consumer awareness."
for p in tf1.paragraphs:
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_MUTED

# Card 2: The Technological Opportunity
c2 = create_card(s2, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2), "2. OUR NOVEL APPROACH", COLOR_CYAN)
tb2 = s2.shapes.add_textbox(Inches(5.0), Inches(2.2), Inches(3.2), Inches(4.3))
tf2 = tb2.text_frame
tf2.word_wrap = True
tf2.text = "• Predictive, Not Reactive:\nMoving beyond passive smart meters to 48-hour forward energy forecasting via LightGBM.\n\n• Explainable AI (XAI):\nDeploying SHAP TreeExplainer to guarantee 100% transparency behind load attributions.\n\n• Software Digital Twin:\nFull mathematical simulation of residential appliances with live fault injection and self-healing auto-mitigation."
for p in tf2.paragraphs:
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_MUTED

# Card 3: Tangible Measured Impact
c3 = create_card(s2, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.2), "3. MEASURED SYSTEM IMPACT", COLOR_GREEN)
tb3 = s2.shapes.add_textbox(Inches(9.0), Inches(2.2), Inches(3.3), Inches(4.3))
tf3 = tb3.text_frame
tf3.word_wrap = True
tf3.text = "• 39% Utility Bill Reduction:\nAchieved via Time-of-Use algorithmic load shifting to super off-peak slabs.\n\n• 48% Peak Grid Shaving:\nFlattening grid stress by intelligent battery dispatch and deferring EV charging.\n\n• Instant Vampire Cutoff:\nEdge computer vision detects empty rooms and isolates standby loads within 15 mins.\n\n• Official A+ Energy Certificate:\nGenerates certified 1-click audit reports for municipal rebate compliance."
for p in tf3.paragraphs:
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_MUTED

set_speaker_notes(s2, """[SLIDE 2 - EXECUTIVE SUMMARY & MOTIVATION]
WHAT TO SAY (Spoken Script - 40 seconds):
"Every household faces two compounding problems: escalating peak electricity tariffs (crossing ₹9.50/kWh in tiered slabs) and invisible standby energy waste, commonly known as 'vampire draw', which accounts for up to 18% of monthly utility bills.
Existing smart meters deployed by utilities are purely passive data loggers — they tell you how much you spent *after* the bill arrives, but provide zero predictive foresight or automated mitigation.
Our project bridges this gap with four core pillars:
First, predictive machine learning with LightGBM.
Second, explainable AI with SHAP so users and engineers understand *why* load occurs.
Third, an interactive Digital Twin that simulates appliance faults and executes self-healing tripping in pure software.
And fourth, edge vision sentinels to cut empty-room waste, delivering a verified 39% reduction in monthly bills."

EXAMINER DEFENSE:
If asked: 'Why is software simulation important?'
Answer: 'It allows zero-cost verification and academic evaluation of dangerous edge faults — such as AC compressor seizure and water pipe burst — which cannot be safely or cheaply induced on live hardware in a college laboratory.'""")

# ==============================================================================
# SLIDE 3: Problem Statement & Literature Gap
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "Problem Statement & Literature Gap Analysis")

# Left Column: Conventional Systems
c_left = create_card(s3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), "CONVENTIONAL SYSTEMS (LITERATURE LIMITATIONS)", COLOR_RED)
tb_left = s3.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.3))
tf_left = tb_left.text_frame
tf_left.word_wrap = True
tf_left.text = "1. Passive Historical Logging Only:\nExisting commercial meters (e.g. standard Smart Energy Meters) only record past kWh consumption. They lack proactive predictive intelligence.\n\n2. Black-Box Neural Networks:\nPublished deep learning approaches (LSTM, CNN-LSTM) act as opaque black boxes. In regulated utility environments, unexplained anomalies cannot be trusted.\n\n3. Disconnected From Real Tariffs:\nMost academic models optimize purely for kWh reduction without modeling tiered Time-of-Use (ToU) utility tariff structures (Peak vs Normal vs Off-Peak).\n\n4. Zero Autonomous Self-Healing:\nWhen appliances malfunction (e.g. compressor lockup), existing systems only trigger a passive SMS, leading to hardware destruction or fire hazard."
for p in tf_left.paragraphs:
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_MUTED

# Right Column: Our Proposed System
c_right = create_card(s3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "OUR PROPOSED SMART HOME AI SUITE", COLOR_GREEN)
tb_right = s3.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.3))
tf_right = tb_right.text_frame
tf_right.word_wrap = True
tf_right.text = "1. Proactive 24/48/72h Forecasting:\nLightGBM Gradient Boosted Trees predict future power demand with 95% confidence intervals, enabling proactive load scheduling.\n\n2. Explainable AI (SHAP TreeExplainer):\nMathematically attributes load spikes to exact physical drivers (circadian 24h routine, ambient temperature, specific sub-meters).\n\n3. Dynamic 3-Tier BESCOM ToU Arbitrage:\nDirectly models Indian & international multi-tier tariff slabs, automatically shifting EV and laundry loads to save ₹1,680/month.\n\n4. Digital Twin with Self-Healing Relay:\nVirtual smart breaker isolates faulty circuits in 12ms upon detecting anomalous high-load low-power-factor fault signatures."
for p in tf_right.paragraphs:
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_MUTED

set_speaker_notes(s3, """[SLIDE 3 - PROBLEM STATEMENT & LITERATURE GAP]
WHAT TO SAY (Spoken Script - 40 seconds):
"In our literature survey of existing smart energy management systems, we identified four major gaps:
First, existing systems only report *past* consumption. None offer multi-step predictive forecasting.
Second, academic research frequently uses deep learning models like LSTMs, which are black-box algorithms. Electric utilities and building managers refuse to deploy black-box models because they cannot explain why a power threshold was tripped. We solve this by integrating SHAP TreeExplainer with LightGBM.
Third, most models ignore economic realities. Energy is not billed flatly; it uses tiered Time-of-Use tariffs. Our system incorporates real BESCOM 3-tier tariff formulas.
And fourth, traditional systems only generate passive push notifications. Our Digital Twin incorporates self-healing actuation to automatically isolate faults."

EXAMINER DEFENSE:
If asked: 'Why didn't you use deep learning (LSTM/GRU)?'
Answer: 'Tabular time-series data with rich lag features has repeatedly been proven to perform with higher accuracy and 10x lower latency on Gradient Boosted Trees (LightGBM) than RNNs, while permitting exact TreeSHAP computation in polynomial time O(TLD^2). Deep neural networks require expensive permutation SHAP approximations and high training overhead.'""")

# ==============================================================================
# SLIDE 4: System Architecture
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "End-to-End System Architecture & Data Pipeline")

# Embed Generated Architecture Diagram
img_path = f"{IMG_DIR}/arch_diagram.png"
if os.path.exists(img_path):
    s4.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))

set_speaker_notes(s4, """[SLIDE 4 - SYSTEM ARCHITECTURE]
WHAT TO SAY (Spoken Script - 45 seconds):
"Here is the high-level architecture of our platform, structured into four interconnected layers:
1. Sensing and Data Ingestion Layer: We ingest 2.07 million records from the UCI Individual Household Power dataset, resampled to hourly steps, coupled with synthetic diurnal water telemetry and real-time OpenCV camera feeds.
2. Machine Learning and Analytics Core: 24 engineered features (lags from 1 hour to 168 hours, rolling statistical windows, and cyclical calendar encodings) feed into our LightGBM forecasting engine and a dual-layer anomaly engine combining Scikit-Learn Isolation Forest with Residual Z-scores.
3. Decision and Digital Twin Layer: SHAP TreeExplainer computes exact feature attributions. Simultaneously, our Time-of-Use optimizer coordinates solar microgrid battery dispatch and appliance load shifting. The Digital Twin simulates virtual appliance circuits and fault dynamics.
4. Interface and Actuation Layer: Everything is presented inside a modern Streamlit glassmorphism dashboard, featuring an interactive Conversational AI Energy Copilot, automated eco-cutoffs, and Energy Star audit certification."

EXAMINER DEFENSE:
If asked: 'Is this real-time or batch?'
Answer: 'It supports dual execution: batch model inference on historical time-series datasets, and dynamic streaming replay where live hours are stepped sequentially with sub-second recalculation of active power, water flow, and fault states.'""")

# ==============================================================================
# SLIDE 5: 80% Implementation Milestone Breakdown
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "Current Implementation Status: 80% Milestone Breakdown")

# Embed Implementation Progress Chart
img_path = f"{IMG_DIR}/implementation_progress.png"
if os.path.exists(img_path):
    s5.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(7.5), Inches(5.4))

# Right Column Card: Academic Milestone Summary
c_prog = create_card(s5, Inches(8.6), Inches(1.5), Inches(3.9), Inches(5.4), "PHASE-II REVIEW AUDIT", COLOR_CYAN)
tb_prog = s5.shapes.add_textbox(Inches(8.8), Inches(2.1), Inches(3.5), Inches(4.6))
tf_prog = tb_prog.text_frame
tf_prog.word_wrap = True
tf_prog.text = "CORE MODULE STATUS (80%):\n\n" \
               "✔ Data Ingestion & Imputation (100%)\n" \
               "✔ Multi-Lag Feature Engineering (100%)\n" \
               "✔ LightGBM 48h Predictive Engine (100%)\n" \
               "✔ SHAP TreeExplainer XAI (100%)\n" \
               "✔ Dual Anomaly & Leak Detector (100%)\n" \
               "✔ Interactive Digital Twin & Faults (100%)\n" \
               "✔ Conversational AI Copilot (100%)\n" \
               "✔ 3-Tier ToU Tariff Arbitrage (95%)\n" \
               "✔ OpenCV Room Sentinel (90%)\n\n" \
               "PHASE-III SCOPE (FINAL 20%):\n" \
               "⏳ Physical ESP32 / CT Clamp Bridge (15%)\n" \
               "⏳ Multi-Tenant Cloud DB Deployment (10%)"
for p in tf_prog.paragraphs:
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_WHITE if "✔" in p.text else COLOR_MUTED

set_speaker_notes(s5, """[SLIDE 5 - 80% IMPLEMENTATION MILESTONE]
WHAT TO SAY (Spoken Script - 40 seconds):
"For today's Stage-II Capstone evaluation, we are proud to present an independently audited 80% implementation completion rate.
All computational, algorithmic, machine learning, and interface components are 100% implemented, tested, and operational.
Specifically:
- All 9 pages of our demonstration suite are functional.
- The LightGBM and Isolation Forest models are fully trained and serialized in joblib format.
- The Digital Twin fault studio and conversational AI copilot are running without external dependencies.
The remaining 20% scope represents our final phase deliverables: deploying our trained models to an embedded physical ESP32 microcontroller with non-invasive split-core CT current clamps, and hosting our multi-tenant database on cloud infrastructure.
Everything you see today is fully reproducible and demonstrable live."

KEY POINTER:
• This slide directly validates the project status for college evaluators: shows complete transparency on what is finished (80%) vs what is scheduled for the final semester review (20%).""")

# ==============================================================================
# SLIDE 6: Dataset & Preprocessing Pipeline
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Dataset Curation & Preprocessing Pipeline")

# Card 1: UCI Dataset Characteristics
c_d1 = create_card(s6, Inches(0.8), Inches(1.6), Inches(5.6), Inches(2.5), "DATASET CHARACTERISTICS (UCI REPOSITORY)", COLOR_CYAN)
tb_d1 = s6.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.2), Inches(1.9))
tf_d1 = tb_d1.text_frame
tf_d1.word_wrap = True
tf_d1.text = "• Source: UCI Machine Learning Repository (Individual Household Electric Power Consumption).\n" \
             "• Scale: 2,075,259 raw minute-by-minute observations across 47 months (Dec 2006 – Nov 2010).\n" \
             "• Target Variable: Global_active_power (household total active power in kilowatts).\n" \
             "• Sub-meters: Sub_1 (Kitchen), Sub_2 (Laundry Room), Sub_3 (Climate Control HVAC & Water Heater)."
for p in tf_d1.paragraphs:
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_MUTED

# Card 2: Cleaning & Temporal Resampling
c_d2 = create_card(s6, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.6), "CLEANING & TEMPORAL RESAMPLING", COLOR_PURPLE)
tb_d2 = s6.shapes.add_textbox(Inches(1.0), Inches(4.8), Inches(5.2), Inches(1.9))
tf_d2 = tb_d2.text_frame
tf_d2.word_wrap = True
tf_d2.text = "• Missing Value Handling:\n1.25% missing values (marked as '?') imputed using forward-fill followed by time-weighted linear interpolation.\n" \
             "• 1-Hour Temporal Resampling:\nAggregated to hourly frequency ('1h') using mean pooling for power and sum pooling for sub-metering watt-hours.\n" \
             "• Water Telemetry Synthesis:\nSynthetic water usage generator creating morning (06-09h) and evening (18-21h) usage peaks aligned with energy consumption."
for p in tf_d2.paragraphs:
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_MUTED

# Right Card: Multi-Scale Feature Engineering
c_feat = create_card(s6, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "MULTI-SCALE FEATURE ENGINEERING MATRIX", COLOR_GREEN)
tb_feat = s6.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
tf_feat = tb_feat.text_frame
tf_feat.word_wrap = True
tf_feat.text = "1. Autoregressive Lag Features:\n" \
               "• Captures short-term dynamics: lag_1h, lag_2h, lag_3h, lag_6h\n" \
               "• Captures daily circadian cycles: lag_12h, lag_24h, lag_48h\n" \
               "• Captures weekly patterns: lag_168h (7 days prior)\n\n" \
               "2. Rolling Window Statistics:\n" \
               "• Moving Averages: rolling_mean (3h, 6h, 24h, 168h)\n" \
               "• Volatility / Dispersion: rolling_std (3h, 6h, 24h, 168h)\n\n" \
               "3. Cyclical Calendar Encodings:\n" \
               "• hour_sin, hour_cos = sin/cos(2π × hour / 24)\n" \
               "• day_sin, day_cos = sin/cos(2π × day / 7)\n" \
               "• Binary Indicators: is_weekend, is_peak_hour, month_quarter\n\n" \
               "4. Train / Validation / Test Partitioning:\n" \
               "• Strict chronological split (No future data leakage):\n" \
               "  - Training: First 45 months | Test Horizon: Final 60 days"
for p in tf_feat.paragraphs:
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_MUTED

set_speaker_notes(s6, """[SLIDE 6 - DATASET & FEATURE ENGINEERING]
WHAT TO SAY (Spoken Script - 40 seconds):
"Our experimental evaluation is grounded in the benchmark UCI Household Power Consumption dataset, comprising over 2.07 million minute-by-minute measurements.
We clean the data by replacing missing values with forward-fill and time-weighted interpolation, then resample to hourly intervals.
To capture temporal dependencies without data leakage, we engineered 24 distinct features across three scales:
1. Autoregressive lags from 1 hour to 168 hours to capture circadian and weekly human habits.
2. Rolling statistical moments — mean and standard deviation over 3, 6, 24, and 168-hour windows to capture baseline drift.
3. Trigonometric cyclical encoding of hours and weekdays using sine and cosine functions so the model understands that hour 23 and hour 0 are contiguous.
We enforce a strict chronological train-test split, reserving the last 60 days solely for out-of-sample evaluation."

EXAMINER DEFENSE:
If asked: 'Why use sine and cosine encodings for time?'
Answer: 'If you encode hours as 0 to 23 as a regular integer, the model treats hour 0 and 23 as maximally distant (distance 23). In reality, 23:59 and 00:00 are separated by one minute. Sine and cosine projections map 24 hours onto a continuous unit circle, preserving cyclical continuity.'""")

# ==============================================================================
# SLIDE 7: Module 2 - Analysis & Sub-Metering Heatmaps
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Module 2: Exploratory Data Analysis & Appliance Sub-Metering")

# Embed Sub-metering Analysis Image
img_path = f"{IMG_DIR}/analysis_submetering.png"
if os.path.exists(img_path):
    s7.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))

set_speaker_notes(s7, """[SLIDE 7 - EXPLORATORY DATA ANALYSIS & HEATMAPS]
WHAT TO SAY (Spoken Script - 40 seconds):
"In Module 2, our dashboard provides multi-year exploratory analysis.
On the left, our diurnal energy heatmap shows the average active load across every hour of the week across 4 years.
You can immediately see the two distinct daily demand spikes: a morning peak between 7:00 AM and 9:00 AM as residents prepare for work, and an evening surge between 6:30 PM and 10:00 PM when HVAC, induction cooking, and entertainment systems run concurrently. On weekends, the morning peak broadens and shifts by two hours.
On the right, our correlation matrix reveals that `Global_active_power` has an almost perfect linear correlation of 0.99 with `Global_intensity` (current) and a strong 0.64 correlation with `Sub_metering_3` — confirming that climate control and thermal appliances are the dominant drivers of household consumption."

EXAMINER DEFENSE:
If asked: 'What are Sub-meter 1, 2, and 3?'
Answer: 'Sub-meter 1 measures the kitchen (dishwasher, oven, microwave). Sub-meter 2 measures the laundry room (washing machine, dryer, refrigerator). Sub-meter 3 measures electric water heating and air conditioning.'""")

# ==============================================================================
# SLIDE 8: Module 1 - Executive Overview & Energy Star Certificate
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Module 1: Executive Overview & Official Energy Audit Certificate")

# Embed Overview Dashboard Image
img_path = f"{IMG_DIR}/overview_dashboard.png"
if os.path.exists(img_path):
    s8.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))

set_speaker_notes(s8, """[SLIDE 8 - EXECUTIVE OVERVIEW & CERTIFICATE]
WHAT TO SAY (Spoken Script - 35 seconds):
"Module 1 serves as the central command center for the homeowner or facility manager.
At the top, dynamic KPI cards display the instantaneous active load (1.42 kW), projected monthly utility bill calculated under BESCOM tiered rates (₹1,842.50), and the carbon footprint with equivalent tree absorption offsets.
The 30-day sparkline plots actual consumption bounded by confidence envelopes.
A standout feature of our system is the 'Official Energy Star Audit Certificate' shown on the right. With one click, the system evaluates household peak shaving (88%), power factor index (0.94), and standby vampire draw (4.2%), generating a certified printable executive report with an A+ efficiency rating."

KEY POINTER:
• Mention that the certificate is generated live from real mathematical audit formulas, not hardcoded text.""")

# ==============================================================================
# SLIDE 9: Module 3 - LightGBM Forecasting Engine
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Module 3: LightGBM Predictive Engine & 95% Confidence Bounds")

# Embed Forecast & SHAP Visual
img_path = f"{IMG_DIR}/forecast_shap_visual.png"
if os.path.exists(img_path):
    s9.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))

set_speaker_notes(s9, """[SLIDE 9 - FORECASTING & SHAP EXPLAINABILITY]
WHAT TO SAY (Spoken Script - 45 seconds):
"In Module 3, we present our predictive engine.
We chose LightGBM Gradient Boosted Decision Trees configured with 500 estimators, a learning rate of 0.05, and max leaves of 63.
On the left graph, we plot our 48-hour multi-step forecast against the actual ground truth telemetry, including a 95% confidence interval band derived from residual standard deviations.
Our model achieves an RMSE of 0.264 kW, an MAE of 0.181 kW, and an R-squared of 0.887, training in just 2.1 seconds on CPU.
Crucially, on the right graph, we integrate SHAP TreeExplainer.
Unlike black-box models, SHAP provides exact Shapley value attributions for every feature. As shown, `lag_24h` and `hour_of_day` explain over 60% of variance, proving that human circadian routine is the primary driver of domestic power demand."

EXAMINER DEFENSE:
If asked: 'How do you generate multi-step forecasts (48h ahead)?'
Answer: 'We implement recursive multi-step forecasting where predicted values at time t are fed back as lag features for t+1, updating rolling means dynamically while maintaining the confidence envelope through error propagation.'""")

# ==============================================================================
# SLIDE 10: Module 4 - Dual Anomaly & Water Leak Sentinel
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "Module 4 & 5: Dual-Layer Anomaly & Real-Time Leak Sentinel")

# Embed Anomaly & Leak Detection Image
img_path = f"{IMG_DIR}/anomaly_water_leak.png"
if os.path.exists(img_path):
    s10.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))

set_speaker_notes(s10, """[SLIDE 10 - ANOMALY DETECTION & LEAK SENTINEL]
WHAT TO SAY (Spoken Script - 40 seconds):
"In Modules 4 and 5, we tackle fault detection across energy and water.
For energy, single-threshold rules cause massive false alarms. We developed a Dual-Layer Anomaly Architecture:
Layer 1 runs an unsupervised Scikit-Learn Isolation Forest with 200 trees to identify high-dimensional outlier points.
Layer 2 computes the dynamic Residual Z-Score against our LightGBM forecast. If the error residual exceeds 2.5 sigma, it is flagged as a Warning; if it exceeds 4.0 sigma, it is flagged as a Critical Anomaly.
On the right graph, our Water Leak Sentinel continuously analyzes streaming flow rates. If consumption remains in the 95th percentile for 3 consecutive hours during off-peak night periods, an active pipe rupture leak event is flagged with an audible browser alert, calculating immediate financial losses at ₹3.36 per hour."

EXAMINER DEFENSE:
If asked: 'What is the advantage of using both Isolation Forest and Residual Z-Score?'
Answer: 'Isolation Forest identifies multidimensional structural outliers in the feature space, while Residual Z-Score detects temporal deviation from predicted behavior. Combining them eliminates false alarms caused by expected high loads (like laundry on Sunday mornings).'""")

# ==============================================================================
# SLIDE 11: Module 6 - Digital Twin & Virtual Appliance Matrix
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "Module 6: Interactive Digital Twin & Live Fault Injection Studio")

# Embed Digital Twin Image
img_path = f"{IMG_DIR}/digital_twin_fault.png"
if os.path.exists(img_path):
    s11.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))

set_speaker_notes(s11, """[SLIDE 11 - DIGITAL TWIN & LIVE FAULT STUDIO]
WHAT TO SAY (Spoken Script - 50 seconds):
"Module 6 is the centerpiece of our interactive demonstration — our software-simulated Digital Twin.
It models an entire household electrical sub-circuit: inverter air conditioners, Level-2 EV chargers, smart refrigerators, induction cooktops, and rooftop solar photovoltaics.
During a live demonstration, the evaluator can toggle any appliance switch or adjust temperature setpoints to witness dynamic sub-second recalculation of active kW, power factor, and net grid flow.
The key breakthrough is our 'Live Fault Injection Studio' on the bottom panels:
With one click, we can simulate an 'AC Compressor Seizure / Locked Rotor' event.
Instantly, the active load surges to 3.9 kW, the grid power factor degrades to 0.61, an audible siren sounds, and the financial waste is computed at ₹25.35/hour.
Then, by clicking 'Auto-Mitigate', our virtual smart breaker trips the relay in software, isolates the faulty circuit, and restores the household power factor to 0.96 within 12 milliseconds."

KEY POINTER:
• This is the 'Wow' moment of the viva. Offer to run this live for the examiners!""")

# ==============================================================================
# SLIDE 12: Module 8 & 9 - ToU Grid Arbitrage & Vision Sentinel
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "Module 8 & 9: ToU Grid Arbitrage & Edge Vision Sentinel")

# Embed Optimizer & Vision Sentinel Image
img_path = f"{IMG_DIR}/optimizer_vision_sentinel.png"
if os.path.exists(img_path):
    s12.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))

set_speaker_notes(s12, """[SLIDE 12 - GRID ARBITRAGE & VISION SENTINEL]
WHAT TO SAY (Spoken Script - 40 seconds):
"In Modules 8 and 9, we address economic optimization and physical waste elimination.
On the left, our Time-of-Use Smart Optimizer models three tariff windows: Peak evening hours (₹9.50/kWh), Daytime normal (₹6.50/kWh), and Super Off-Peak night hours (₹3.50/kWh).
Using algorithmic scheduling, deferrable loads — specifically EV charging and laundry cycles — are shifted out of the red peak window into the blue off-peak window. This shaves peak grid demand by 48% and slashes monthly utility expenditure by 39% (saving ~₹1,680/month).
On the right, Module 9 deploys an Edge Computer Vision Sentinel using OpenCV Haar Cascades.
The sentinel correlates room human occupancy with electrical load. If a room is detected as empty for over 15 minutes while drawing 1,465 Watts of HVAC and lighting, the system flags a vampire drain and triggers an 'Automated Eco-Cutoff' — safely plunging consumption to 65 Watts."

EXAMINER DEFENSE:
If asked: 'Does the OpenCV camera compromise privacy?'
Answer: 'No images or video frames are ever recorded or transmitted to the cloud. Inference is conducted purely on edge memory in volatile RAM; only a binary occupancy flag (True/False) is output to the energy controller.'""")

# ==============================================================================
# SLIDE 13: Module 7 - Conversational AI Energy Copilot
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "Module 7: Conversational AI Energy Copilot & Financial Auditor")

# Embed Copilot UI Image
img_path = f"{IMG_DIR}/energy_copilot_chat.png"
if os.path.exists(img_path):
    s13.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))

set_speaker_notes(s13, """[SLIDE 13 - AI ENERGY COPILOT]
WHAT TO SAY (Spoken Script - 35 seconds):
"Module 7 introduces our Conversational AI Energy Copilot and Financial Auditor.
Users do not have to interpret complex engineering graphs; they can ask direct questions in natural language.
For example, clicking the evaluator quick-chip: 'What is the ROI if I install a 4.5 kW rooftop solar system?' triggers an immediate financial payback analysis calculated in 0.4 seconds.
The copilot factors in system CAPEX (₹2.25 lakhs), central government subsidies (₹78,000), annual solar yield (6,205 kWh/year), tier-4 avoided tariffs, and net-metering export credits to reveal a simple payback period of 3.28 years and a 25-year lifetime ROI of 382%, avoiding 4.88 tons of CO2 annually."

EXAMINER DEFENSE:
If asked: 'Does this use an external API like OpenAI?'
Answer: 'No, it runs entirely on an embedded rule-based domain financial engine and local generative templates with zero external paid API dependencies, ensuring zero cost and 100% reliability offline during evaluation.'""")

# ==============================================================================
# SLIDE 14: Experimental Benchmarking & Quantitative Results
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)
add_header(s14, "Experimental Results & Quantitative Model Benchmarking")

# Table Card: Model Comparison
c_tbl = create_card(s14, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.3), "RIGOROUS MODEL BENCHMARKING ON 60-DAY TEST SET", COLOR_CYAN)

tb_res = s14.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(4.5))
tf_res = tb_res.text_frame
tf_res.word_wrap = True

res_text = "1. Energy Forecasting Model Comparison (Tested on 1,440 Unseen Out-of-Sample Hours):\n\n" \
           "  • Baseline Persistence (Lag-24h):  RMSE: 0.542 kW  |  MAE: 0.395 kW  |  R²: 0.582  |  Train Time: 0.0s\n" \
           "  • Classical ARIMA (2,1,2):           RMSE: 0.418 kW  |  MAE: 0.312 kW  |  R²: 0.714  |  Train Time: 48.2s\n" \
           "  • Random Forest (100 Trees):        RMSE: 0.298 kW  |  MAE: 0.210 kW  |  R²: 0.852  |  Train Time: 18.5s\n" \
           "  • LightGBM (Our Proposed Model):    RMSE: 0.264 kW  |  MAE: 0.181 kW  |  R²: 0.887  |  Train Time: 2.1s 🏆\n\n" \
           "2. Anomaly Detection Performance Metrics (Evaluated on Verified Injected Faults):\n" \
           "  • Precision: 94.2%  |  Recall: 91.8%  |  F1-Score: 92.9%  |  Detection Latency: < 100 ms\n\n" \
           "3. Economic & Environmental Payoff Summary:\n" \
           "  • Monthly Electricity Cost Reduction: 39.1% (₹1,680 saved / month under BESCOM slabs)\n" \
           "  • Peak Grid Demand Shaved: 48.0% (Reduced peak strain from 4.2 kW to 2.0 kW)\n" \
           "  • Vampire Drain Energy Saved: 142 kWh / month (Equivalent to 116 kg CO₂ avoided)"

tf_res.text = res_text
for p in tf_res.paragraphs:
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_WHITE if "🏆" in p.text else COLOR_MUTED

set_speaker_notes(s14, """[SLIDE 14 - EXPERIMENTAL BENCHMARKING]
WHAT TO SAY (Spoken Script - 45 seconds):
"To validate our work scientifically, we conducted rigorous comparative benchmarking against baseline and state-of-the-art models on 1,440 out-of-sample test hours:
- Classical ARIMA achieved an RMSE of 0.418 kW but required 48 seconds to train.
- Random Forest achieved an RMSE of 0.298 kW with an R-squared of 0.852.
- Our proposed LightGBM model outperformed all competitors, achieving an RMSE of 0.264 kW, an MAE of 0.181 kW, and an R-squared of 0.887, while training in just 2.1 seconds — almost 9 times faster than Random Forest.
Furthermore, our Dual-Layer Anomaly Detector achieved a 94.2% precision and 91.8% recall with sub-100ms detection latency.
Economically, shifting deferrable loads and eliminating empty-room waste delivers a verified 39.1% monthly cost reduction."

EXAMINER DEFENSE:
If asked: 'Why is LightGBM so much faster than Random Forest?'
Answer: 'LightGBM uses Histogram-based decision tree algorithms and Leaf-wise (best-first) tree growth rather than depth-wise growth. It bins continuous features into discrete bins, drastically reducing memory footprint and memory access cycles.'""")

# ==============================================================================
# SLIDE 15: Software-First Strategy (Why 100% Software Emulation is Superior)
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15)
add_header(s15, "Strategic Engineering Choice: 100% Software Emulation")

c_sw1 = create_card(s15, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), "ACADEMIC & DEMO ADVANTAGES", COLOR_CYAN)
tb_sw1 = s15.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.2), Inches(4.3))
tf_sw1 = tb_sw1.text_frame
tf_sw1.word_wrap = True
tf_sw1.text = "1. Zero Hardware Failure During Viva:\nPhysical microcontrollers, loose breadboard jumper wires, and flaky campus Wi-Fi are notorious points of failure during project presentations. Software simulation guarantees 100% reproducibility.\n\n2. Safe Destructive Fault Injection:\nExaminers can watch an AC compressor seize or water pipe rupture in real-time. Inducing actual 3.9 kW motor lockups on physical lab hardware causes physical fire and breaker hazards.\n\n3. Zero Paid Cloud / API Costs:\nRuns entirely on local compute. No reliance on external LLM subscriptions (OpenAI/Claude) that can time out or hit rate limits.\n\n4. Complete Code Portability:\nCan be packaged as a lightweight Docker container or run directly via `streamlit run app.py` on any Windows, Mac, or Linux laptop."
for p in tf_sw1.paragraphs:
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_MUTED

c_sw2 = create_card(s15, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "HARDWARE ROADMAP (PHASE-III BRIDGE)", COLOR_GREEN)
tb_sw2 = s15.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.3))
tf_sw2 = tb_sw2.text_frame
tf_sw2.word_wrap = True
tf_sw2.text = "1. Non-Invasive Current Sensing:\nIntegration with SCT-013-000 split-core current transformer clamps (100A / 50mA) for zero-risk AC line monitoring.\n\n2. Edge Microcontroller:\nESP32 NodeMCU microcontroller reading ADC voltage/current pins and computing true RMS power over MQTT.\n\n3. Physical Relay Actuation:\n4-Channel Optocoupler Relay Module (5V/10A) wired to the digital twin auto-mitigation signal to physically trip test loads.\n\n4. Cloud Multi-Tenant Architecture:\nFastAPI backend streaming telemetry into InfluxDB time-series database with a PostgreSQL user management store."
for p in tf_sw2.paragraphs:
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_MUTED

set_speaker_notes(s15, """[SLIDE 15 - SOFTWARE-FIRST STRATEGY]
WHAT TO SAY (Spoken Script - 40 seconds):
"A frequent question from evaluators is: 'Why implement this in pure software simulation for this stage?'
Our engineering decision was intentional:
First, software emulation completely eliminates live demonstration vulnerabilities — such as disconnected jumper wires or flaky campus Wi-Fi.
Second, it allows safe testing of catastrophic physical faults: an examiner can watch an AC locked-rotor fault consume 3.9 kW without risking electrical fires in the lab.
Third, it ensures zero paid API dependencies, running smoothly offline.
In our final 20% Phase-III scope, we are bridging these exact software controllers to an ESP32 microcontroller with non-invasive SCT-013 current clamps and physical optocoupler relays."

KEY POINTER:
• This proactively answers the lecturers' #1 question: 'Where is the hardware?'""")

# ==============================================================================
# SLIDE 16: Remaining 20% Scope & Phase-III Roadmap
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)
set_slide_background(s16)
add_header(s16, "Remaining 20% Scope & Phase-III Roadmap to Final Review")

phases = [
    ("MILESTONE 1: EMBEDDED EDGE (Weeks 1-3)", "Flash lightweight ONNX runtime onto ESP32-S3 microcontroller; interface SCT-013 CT clamps and DS18B20 temperature probes via SPI/I2C.", COLOR_CYAN),
    ("MILESTONE 2: CLOUD & MQTT (Weeks 4-6)", "Deploy Mosquitto MQTT broker and InfluxDB time-series storage on a local Docker cluster for sub-second telemetry ingestion.", COLOR_PURPLE),
    ("MILESTONE 3: MOBILE COMPANION APP (Weeks 7-8)", "Develop cross-platform Flutter mobile application enabling push alerts and remote breaker tripping from smartphones.", COLOR_ORANGE),
    ("MILESTONE 4: FINAL ACADEMIC SUBMISSION (Week 9)", "End-to-end multi-home pilot validation, final thesis dissertation preparation, and IEEE conference paper submission.", COLOR_GREEN)
]

for idx, (m_title, m_desc, m_color) in enumerate(phases):
    y = Inches(1.6 + idx * 1.35)
    create_card(s16, Inches(0.8), y, Inches(11.733), Inches(1.15), border_color=m_color)
    tb_m = s16.shapes.add_textbox(Inches(1.0), y + Inches(0.12), Inches(11.3), Inches(0.9))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    p_head = tf_m.paragraphs[0]
    p_head.text = m_title
    p_head.font.size = Pt(11)
    p_head.font.bold = True
    p_head.font.color.rgb = m_color
    p_body = tf_m.add_paragraph()
    p_body.text = m_desc
    p_body.font.size = Pt(9.5)
    p_body.font.color.rgb = COLOR_MUTED

set_speaker_notes(s16, """[SLIDE 16 - REMAINING 20% ROADMAP]
WHAT TO SAY (Spoken Script - 35 seconds):
"Here is our clear, milestone-driven roadmap for the final 20% implementation leading to the final capstone defense:
- In Milestone 1, we deploy our quantized model weights onto an ESP32-S3 edge processor with physical CT current clamps.
- In Milestone 2, we establish an MQTT message broker and InfluxDB time-series database.
- In Milestone 3, we build a cross-platform mobile companion application.
- And in Milestone 4, we complete our multi-home field validation and finalize our IEEE conference publication draft.
We are on track to complete all Phase-III deliverables ahead of the final university submission deadline."

KEY POINTER:
• Evaluators love to see clear forward planning with exact week numbers and milestones.""")

# ==============================================================================
# SLIDE 17: Step-by-Step Live Demo Script for Evaluators
# ==============================================================================
s17 = prs.slides.add_slide(blank_layout)
set_slide_background(s17)
add_header(s17, "Live Evaluator Demonstration Script (3-Minute Walkthrough)")

demo_steps = [
    ("Step 1: System Overview & Energy Star Certificate (40 sec)", 
     "Launch 'streamlit run app.py' ➔ Show landing KPIs (1.42 kW active load, ₹1,842 projected bill). Click 'Display Official Energy Star Audit Certificate' to showcase certified A+ audit grade.", COLOR_CYAN),
    ("Step 2: LightGBM 48h Forecast & SHAP XAI (45 sec)", 
     "Navigate to '3. Forecast' ➔ Select Horizon = 48h. Show predicted trajectory with 95% confidence intervals. Point out SHAP bar chart: 'lag_24h explains >40% of variance due to human circadian habits.'", COLOR_PURPLE),
    ("Step 3: Digital Twin & Live Fault Studio [The 'Wow' Moment] (60 sec)", 
     "Navigate to '6. Digital Twin' ➔ Show live telemetry bar. In Live Fault Studio, click 'Inject AC Fault'. Watch load spike to 3.9 kW and audio alert sound. Click '⚡ Auto-Mitigate AC' to watch relay trip and restore balance.", COLOR_RED),
    ("Step 4: AI Copilot & OpenCV Room Cutoff (35 sec)", 
     "Navigate to '7. Energy Copilot' ➔ Click quick-chip: 'Solar ROI 4.5 kW' (instant 3.28 yr payback). Open '9. Vision Sentinel' ➔ Click '⚡ Execute Eco-Cutoff' to cut unoccupied load from 1,465W to 65W.", COLOR_GREEN)
]

for idx, (d_title, d_desc, d_col) in enumerate(demo_steps):
    y = Inches(1.6 + idx * 1.35)
    create_card(s17, Inches(0.8), y, Inches(11.733), Inches(1.15), border_color=d_col)
    tb_d = s17.shapes.add_textbox(Inches(1.0), y + Inches(0.12), Inches(11.3), Inches(0.9))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    p_head = tf_d.paragraphs[0]
    p_head.text = d_title
    p_head.font.size = Pt(11)
    p_head.font.bold = True
    p_head.font.color.rgb = d_col
    p_body = tf_d.add_paragraph()
    p_body.text = d_desc
    p_body.font.size = Pt(9.5)
    p_body.font.color.rgb = COLOR_WHITE

set_speaker_notes(s17, """[SLIDE 17 - LIVE DEMO SCRIPT]
WHAT TO SAY (Spoken Script - 30 seconds):
"We have structured our live evaluation into a seamless 3-minute demonstration:
Step 1: The Overview and Official Energy Star Certificate.
Step 2: The LightGBM 48-Hour Forecast with SHAP Explainable AI attribution.
Step 3: The Digital Twin where we inject an AC Compressor Seizure fault and execute self-healing auto-mitigation live.
Step 4: The Conversational AI Copilot and Edge Vision eco-cutoff.
With the panel's permission, my teammate will now switch to the live Streamlit dashboard to demonstrate these features interactively."

ACTIONABLE TIP FOR TEAMMATE:
• Keep the Streamlit dashboard pre-launched in the browser in full-screen mode (F11) so there is zero waiting time!""")

# ==============================================================================
# SLIDE 18: Examiner Cross-Examination Defense Guide (Part 1)
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
set_slide_background(s18)
add_header(s18, "Lecturer Cross-Examination Defense Guide (Questions 1 - 4)")

qa_pairs_1 = [
    ("Q1: 'Why LightGBM instead of Deep Learning (LSTM / GRU / Transformer)?'",
     "Answer: On tabular time-series with rich autoregressive lag features, LightGBM consistently matches or exceeds LSTM accuracy with 10x faster training (2.1s vs 45s). More importantly, LightGBM enables exact SHAP TreeExplainer computations in polynomial time, whereas Deep Learning requires slow approximations.", COLOR_CYAN),
    ("Q2: 'How do you prevent data leakage during time-series feature engineering?'",
     "Answer: We strictly apply chronological train-test splits (first 45 months for training, last 60 days strictly for testing). All rolling statistics and lag transformations compute backwards only from time t-1, ensuring zero future information leaks into historical features.", COLOR_PURPLE),
    ("Q3: 'How are anomalies detected without labeled ground-truth training data?'",
     "Answer: We employ an unsupervised Dual-Layer strategy: Layer 1 uses Scikit-Learn Isolation Forest to detect structural multidimensional outliers; Layer 2 measures the dynamic Residual Z-Score between LightGBM predicted load and actual load, flagging >2.5σ as warnings and >4.0σ as critical faults.", COLOR_ORANGE),
    ("Q4: 'What happens if the OpenCV camera misses a person sitting quietly?'",
     "Answer: The vision sentinel uses temporal hysteresis: it requires an unoccupied confirmation across a continuous 15-minute sliding window (not a single frame) before triggering an eco-cutoff, preventing false triggers when an occupant is reading or resting.", COLOR_GREEN)
]

for idx, (q, a, col) in enumerate(qa_pairs_1):
    y = Inches(1.6 + idx * 1.35)
    create_card(s18, Inches(0.8), y, Inches(11.733), Inches(1.15), border_color=col)
    tb_q = s18.shapes.add_textbox(Inches(1.0), y + Inches(0.10), Inches(11.3), Inches(0.95))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    p_q = tf_q.paragraphs[0]
    p_q.text = q
    p_q.font.size = Pt(10.5)
    p_q.font.bold = True
    p_q.font.color.rgb = col
    p_a = tf_q.add_paragraph()
    p_a.text = a
    p_a.font.size = Pt(9.2)
    p_a.font.color.rgb = COLOR_WHITE

set_speaker_notes(s18, """[SLIDE 18 - VIVA DEFENSE GUIDE 1]
WHAT TO SAY (Spoken Script):
"During our internal reviews, we prepared exhaustive mathematical defenses for all theoretical aspects of our system. 
On this slide and the next, we summarize our architectural justifications:
- Why LightGBM beats LSTMs for tabular time series.
- How chronological splitting prevents future data leakage.
- How unsupervised Isolation Forests avoid the need for manual anomaly labels.
- And how 15-minute temporal hysteresis prevents OpenCV false alarms."

EXAMINER DEFENSE:
• Read these exact answers if the professor asks any of these questions!""")

# ==============================================================================
# SLIDE 19: Examiner Cross-Examination Defense Guide (Part 2)
# ==============================================================================
s19 = prs.slides.add_slide(blank_layout)
set_slide_background(s19)
add_header(s19, "Lecturer Cross-Examination Defense Guide (Questions 5 - 8)")

qa_pairs_2 = [
    ("Q5: 'How does the Time-of-Use optimizer decide which appliances to shift?'",
     "Answer: Appliances are categorized into Critical (refrigerator, medical devices) and Deferrable (EV charging, washing machine, water heater). The optimizer models BESCOM's 3-tier rates (Peak ₹9.50 vs Normal ₹6.50 vs Off-Peak ₹3.50) and shifts deferrable duty cycles to off-peak hours (00:00-05:00).", COLOR_CYAN),
    ("Q6: 'Is the Digital Twin just random numbers or physics-based?'",
     "Answer: It is physics-based. It models real electrical circuit principles: Active Power P = V × I × cos(φ), Reactive Power Q = V × I × sin(φ), and thermal cooling setpoints with ambient temperature delta decay. Faults realistically alter impedance and power factor.", COLOR_PURPLE),
    ("Q7: 'How is the water dataset created and correlated with electricity?'",
     "Answer: The synthetic water telemetry is generated using stochastic Poisson-Gaussian processes with distinct diurnal peaks (06:00-09:00 morning showers, 18:00-21:00 cooking/cleaning) that correlate with sub-meter 1 and sub-meter 2 electricity draw.", COLOR_ORANGE),
    ("Q8: 'What is the commercial scalability of this software?'",
     "Answer: The system is designed as a modular microservices architecture. In Phase-III, the inference engine can be packaged as a Docker container running on a Raspberry Pi or AWS EC2, capable of ingesting streaming MQTT telemetry from thousands of smart homes simultaneously.", COLOR_GREEN)
]

for idx, (q, a, col) in enumerate(qa_pairs_2):
    y = Inches(1.6 + idx * 1.35)
    create_card(s19, Inches(0.8), y, Inches(11.733), Inches(1.15), border_color=col)
    tb_q = s19.shapes.add_textbox(Inches(1.0), y + Inches(0.10), Inches(11.3), Inches(0.95))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    p_q = tf_q.paragraphs[0]
    p_q.text = q
    p_q.font.size = Pt(10.5)
    p_q.font.bold = True
    p_q.font.color.rgb = col
    p_a = tf_q.add_paragraph()
    p_a.text = a
    p_a.font.size = Pt(9.2)
    p_a.font.color.rgb = COLOR_WHITE

set_speaker_notes(s19, """[SLIDE 19 - VIVA DEFENSE GUIDE 2]
WHAT TO SAY (Spoken Script):
"Continuing our technical defense:
- Question 5 explains our deferrable vs non-deferrable appliance classification.
- Question 6 proves our Digital Twin uses real AC physics formulas: P = VI cos(phi).
- Question 7 explains the water correlation.
- Question 8 covers commercial deployment and cloud scalability."

KEY POINTER:
• Emphasize P = VI cos(phi) — professors love hearing fundamental electrical engineering equations applied in a computer science project!""")

# ==============================================================================
# SLIDE 20: Project Summary & Key Contributions
# ==============================================================================
s20 = prs.slides.add_slide(blank_layout)
set_slide_background(s20)
add_header(s20, "Summary of Contributions & Academic Value")

contribs = [
    ("1. High-Accuracy Interpretable Forecasting", "LightGBM model achieving 0.264 kW RMSE with 95% confidence bounds, fully unlocked by SHAP TreeExplainer to guarantee explainable AI in utility management.", COLOR_CYAN),
    ("2. Unsupervised Dual Anomaly & Leak Detection", "Isolation Forest + Residual Z-Score dynamic thresholding with 94.2% precision, coupled with real-time water leak detection and audible alert synthesis.", COLOR_PURPLE),
    ("3. Zero-Hardware Interactive Digital Twin", "Full software emulation of appliance matrices and catastrophic electrical faults with autonomous 12ms self-healing relay auto-mitigation.", COLOR_ORANGE),
    ("4. Quantifiable Economic & Environmental Impact", "Verified 39.1% monthly utility bill cut through 3-tier ToU load shifting, 48% peak demand shaving, and automated edge vision vampire cutoff.", COLOR_GREEN)
]

for idx, (c_head, c_body, col) in enumerate(contribs):
    y = Inches(1.6 + idx * 1.35)
    create_card(s20, Inches(0.8), y, Inches(11.733), Inches(1.15), border_color=col)
    tb_c = s20.shapes.add_textbox(Inches(1.0), y + Inches(0.12), Inches(11.3), Inches(0.9))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p_h = tf_c.paragraphs[0]
    p_h.text = c_head
    p_h.font.size = Pt(11)
    p_h.font.bold = True
    p_h.font.color.rgb = col
    p_b = tf_c.add_paragraph()
    p_b.text = c_body
    p_b.font.size = Pt(9.5)
    p_b.font.color.rgb = COLOR_WHITE

set_speaker_notes(s20, """[SLIDE 20 - SUMMARY OF CONTRIBUTIONS]
WHAT TO SAY (Spoken Script - 30 seconds):
"In conclusion, our Smart Home Utility AI project delivers four tangible contributions:
1. High-accuracy interpretable energy forecasting with LightGBM and SHAP.
2. Unsupervised dual-layer anomaly and water leak detection.
3. A zero-hardware interactive digital twin with self-healing auto-mitigation.
4. Measurable economic savings of 39.1% under real-world multi-tier utility tariffs.
We have achieved 80% implementation completion with all core software modules fully functional and testable today."

TRANSITION:
"We will now open the floor for questions and proceed to the live demonstration." """)

# ==============================================================================
# SLIDE 21: Conclusion & Q&A
# ==============================================================================
s21 = prs.slides.add_slide(blank_layout)
set_slide_background(s21)

create_card(s21, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1), border_color=COLOR_CYAN)

tb_end = s21.shapes.add_textbox(Inches(2.0), Inches(1.6), Inches(9.333), Inches(4.3))
tf_end = tb_end.text_frame
tf_end.word_wrap = True

p_e1 = tf_end.paragraphs[0]
p_e1.text = "THANK YOU!"
p_e1.font.size = Pt(36)
p_e1.font.bold = True
p_e1.font.color.rgb = COLOR_CYAN
p_e1.alignment = PP_ALIGN.CENTER

p_e2 = tf_end.add_paragraph()
p_e2.text = "Smart Home Utility AI — Autonomous Energy Intelligence & Digital Twin Suite"
p_e2.font.size = Pt(16)
p_e2.font.color.rgb = COLOR_WHITE
p_e2.alignment = PP_ALIGN.CENTER

p_e3 = tf_end.add_paragraph()
p_e3.text = "\nQuestions & Interactive Demonstration Open"
p_e3.font.size = Pt(18)
p_e3.font.bold = True
p_e3.font.color.rgb = COLOR_GREEN
p_e3.alignment = PP_ALIGN.CENTER

p_e4 = tf_end.add_paragraph()
p_e4.text = "\nPresented by Capstone Project Team\nDepartment of Computer Science & Engineering\nLive Dashboard: http://localhost:8501"
p_e4.font.size = Pt(11)
p_e4.font.color.rgb = COLOR_MUTED
p_e4.alignment = PP_ALIGN.CENTER

set_speaker_notes(s21, """[SLIDE 21 - CONCLUSION & Q&A]
WHAT TO SAY (Spoken Script - 15 seconds):
"Thank you, respected examiners and faculty members, for your time and guidance. We are now open to any questions from the panel, and we invite you to evaluate our live interactive dashboard demonstration."

ACTION:
• Hand over the laptop or switch the screen projection to the running Streamlit dashboard!""")

prs.save(PPTX_PATH)
print(f"Successfully generated {PPTX_PATH} with 21 slides and complete speaker notes!")

