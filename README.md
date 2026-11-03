# Smart Home Utility AI 🏠⚡
### Autonomous Smart Home Energy Intelligence & Digital Twin Suite
*100% Software-Based Interactive Demonstration · Zero Physical Hardware Required*

---

## 🌟 Executive Summary

**Smart Home Utility AI** is an advanced, presentation-ready smart energy and water analytics platform built with **Python, Streamlit, LightGBM, Scikit-learn, SHAP, and OpenCV**.

The platform is designed to be demonstrated live during academic evaluations, capstone vivas, and project juries. It bridges **Predictive Machine Learning**, **Explainable AI (XAI)**, **Real-Time Digital Twin Simulation**, **Time-of-Use Grid Optimization**, and **Edge Computer Vision** into a unified dark-mode glassmorphism interface.

---

## 🚀 Key Modules (9-Page Demonstration Suite)

| # | Module | Core Functionality | Demonstration Highlight |
|---|---|---|---|
| **1** | 🏠 **Overview** | KPI cards, active power gauges, 30-day sparklines, CO₂ footprint | **Official Energy Star Certificate**: 1-click printable executive audit report with A+ grade. |
| **2** | 🔍 **Analysis** | Heatmaps, appliance sub-metering, correlation matrix | Temporal aggregation selector (Hourly, Daily, Weekly) across 4 years of real data. |
| **3** | 🔮 **Forecast** | LightGBM 24/48/72h forecasting with 95% confidence intervals | **SHAP TreeExplainer**: Shows exact feature attributions behind every prediction. |
| **4** | 🚨 **Alerts & Tips** | Isolation Forest & Residual Z-Score anomaly detection | Ranked cost-saving recommendations with verified ₹/month payoff. |
| **5** | 🎬 **Live Replay** | Hourly historical streaming simulator with speed controls (1×–10×) | Real-time water leak detection with audible audio alerts. |
| **6** | 🏠 **Digital Twin** | 100% software-simulated smart home appliance matrix | **Live Fault Studio**: Inject AC compressor seizure, water pipe rupture, or vampire drain; trigger **1-click Self-Healing Auto-Mitigation**. |
| **7** | 💬 **Energy Copilot** | Conversational AI energy auditor & advisor | Instant natural language answers to tariff queries, solar ROI calculations, and diagnostics with evaluator quick-chips. |
| **8** | ⚡ **Smart Optimizer** | Dynamic 3-Tier Time-of-Use (ToU) arbitrage & microgrid simulator | Algorithmic load shifting for EV/laundry (-39% bill cut) + 24h Solar PV & Battery Storage dispatch. |
| **9** | 👁️ **Vision Sentinel** | Edge Computer Vision room occupancy & waste sentinel | Correlates human occupancy with appliance draw; detects empty-room waste and triggers **Automated Eco-Cutoff**. |

---

## 🎓 Examiner Demonstration & Viva Presentation Script (Full Marks Guide)

Follow this 5-minute walkthrough during your project demonstration to leave evaluators thoroughly impressed:

### Step 1: Landing Hub & Architecture (1 min)
1. Launch `streamlit run app.py` and present the landing screen.
2. **Explain to the examiner:**
   > *"Our system is an end-to-end intelligent energy management platform combining machine learning, mathematical optimization, and computer vision. Everything runs completely software-emulated with zero external hardware or paid API dependencies."*

### Step 2: Predictive AI & SHAP Explainability (`Forecast` & `Overview`) (1 min)
1. Open **3. Forecast**. Select **Horizon = 48h**.
2. Show the LightGBM forecast curve with its 95% confidence interval band.
3. Scroll to the **SHAP Feature Importance** bar chart.
4. **Key talking point:**
   > *"Unlike black-box neural networks, our LightGBM model is fully interpretable via SHAP TreeExplainer. Evaluators can see that `lag_24h` and `hour_of_day` explain over 60% of variance due to circadian human routines."*
5. Open **1. Overview** and click **"Display Official Energy Star Audit Certificate"**. Point out the certified score and download button.

### Step 3: Interactive Digital Twin & Live Fault Injection (`Digital Twin`) (1.5 min)
1. Navigate to **6. Digital Twin**.
2. Show the live multi-variable telemetry bar (Gross kW, Solar Output, Net Grid, Power Factor, ₹/hr, Water L/h).
3. Toggle a few switches (Living Room AC, EV Charger) and adjust the cooling setpoint slider to show dynamic load recalculation.
4. **The "Wow" Moment:** In the **Live Fault Injection Studio**, click **"Inject AC Fault"**.
   - An audible alert tone plays.
   - The status bar turns red: *AC Compressor Seizure / Locked Rotor* (load spikes to 3.9 kW, power factor plunges to 0.61).
   - Point out the active fault card showing an estimated loss of ₹25.35/hr.
5. Click **"⚡ Auto-Mitigate AC"**.
   - Watch the virtual smart relay safely trip the breaker, clear the anomaly, and restore household balance.
   - **Key talking point:** *"This demonstrates self-healing smart home capabilities in pure software."*

### Step 4: AI Energy Copilot (`Energy Copilot`) (45 sec)
1. Open **7. Energy Copilot**.
2. Click the quick prompt: *"What is the ROI if I install a 4.5 kW rooftop solar system?"*.
3. The AI immediately responds with a complete capital cost, annual savings, and a 4.8-year simple payback schedule based on active tariffs.

### Step 5: ToU Grid Optimization & Vision Sentinel (`Smart Optimizer` & `Vision Sentinel`) (1 min)
1. Open **8. Smart Optimizer**. Show how shifting EV charging to the Super Off-Peak window (₹3.50/kWh) shaves peak grid demand by 48% and saves ~₹1,680/month.
2. Open **9. Vision Sentinel**. Switch between *"Empty Room (HVAC & Lights Left ON)"* and *"Occupied Room"*.
3. Show the red vampire waste banner and click **"⚡ Execute AI Automated Eco-Cutoff"** to show instant power reduction from 1,465W to 65W.

---

## 🛠️ Quick Start

```bash
# 1. Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the dashboard
streamlit run app.py
```

---

## 🏗️ Technology Stack

- **Frontend & Routing:** Streamlit (Multi-page App, custom CSS Glassmorphism)
- **Data Visualizations:** Plotly Express & Plotly Graph Objects
- **Forecasting Model:** LightGBM (Gradient Boosted Decision Trees)
- **Anomaly Detection:** Scikit-learn (Isolation Forest + Residual Z-Score)
- **Model Explainability:** SHAP (`shap.TreeExplainer`)
- **Computer Vision:** OpenCV (`cv2` Haar Cascade & synthetic frame synthesis)
- **Telemetry & Optimization:** NumPy, SciPy, Pandas
- **Config & Persistence:** PyYAML, Joblib

---

## 📁 Repository Structure

```
SMART-HOME-PROJECT/
├── app.py                     # Global entry point, configuration, sidebar navigation
├── config.yaml                # Tariffs, model hyperparameters, thresholds
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation and viva presentation script
├── models/                    # Trained model artifacts (.joblib)
│   ├── lgbm_energy_model.joblib
│   ├── isolation_forest.joblib
│   ├── feature_list.joblib
│   └── residual_std.joblib
├── src/
│   ├── dataset_loader.py      # UCI dataset download & caching
│   ├── data_cleaning.py       # Hourly aggregation and missing value handling
│   ├── water_generator.py     # Aligned synthetic water telemetry
│   ├── feature_engineering.py # Lag, rolling, and cyclical calendar features
│   ├── forecasting.py         # LightGBM training, in-sample & recursive prediction
│   ├── anomaly_detection.py   # Isolation Forest & residual bounds
│   ├── explainability.py      # SHAP TreeExplainer integration
│   ├── recommendations.py     # Ranked financial savings engine
│   ├── replay_simulator.py    # Streaming window replay manager
│   ├── bill_estimator.py      # BESCOM tiered tariff calculator
│   ├── co2_calculator.py      # Carbon footprint and tree offsets
│   ├── digital_twin.py        # Appliance states, telemetry synthesis, fault injector
│   ├── copilot.py             # Conversational AI auditor engine
│   ├── optimizer.py           # ToU tariff load shifter & solar microgrid dispatch
│   ├── vision_detector.py     # OpenCV occupancy detection & waste sentinel
│   └── report_generator.py    # Energy Star Audit Certificate generator
└── pages/
    ├── 1_Overview.py          # KPIs, gauges & official certificate generator
    ├── 2_Analysis.py          # Heatmaps, sub-meter correlations & calendar patterns
    ├── 3_Forecast.py          # LightGBM predictions & SHAP explanations
    ├── 4_Alerts_Tips.py       # Anomaly alerts table & savings tips
    ├── 5_Live_Replay.py       # Streaming replay with audio alerts
    ├── 6_Digital_Twin.py      # Virtual home & live fault injection studio
    ├── 7_Energy_Copilot.py    # AI Energy Copilot conversational auditor
    ├── 8_Smart_Optimizer.py   # ToU load shifter & solar microgrid dispatch
    └── 9_Vision_Sentinel.py   # Edge AI vision occupancy & waste cutoff
```

---

## ⚖️ License
MIT License — Free to use, adapt, and demonstrate.
