streamlit run app.py
pip install streamlit numpy plotly
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AstroHealth & Environmental HUD", 
    page_icon="🚀", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main { background-color: #0F172A; }
    div[data-testid='stMetricValue'] { font-size: 24px; font-weight: bold; }
    .status-card { padding: 12px; border-radius: 10px; margin-bottom: 10px; text-align: center; font-weight: bold; font-size: 16px; color: white; }
    .optimal { background-color: #15803D; }
    .warning { background-color: #A16207; }
    .critical { background-color: #B91C1C; }
    .gas-bar-container { background-color: #1E293B; border-radius: 8px; padding: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Astronaut Health & Cabin Gas Telemetry HUD")
st.markdown("*Monitoring microgravity adaptation, physiological stress, and wireless Arduino-linked environmental gas sensors.*")

# --- SIDEBAR: WIRELESS HARDWARE CONFIGURATION ---
st.sidebar.header("📡 Hardware & Wireless Link")
use_wireless = st.sidebar.checkbox("Connect to Wireless Arduino (Wi-Fi)", value=False)
arduino_ip = st.sidebar.text_input("Arduino/ESP32 IP Endpoint", "http://192.168.1.150/sensors")

# Fetch live hardware data if wireless mode is enabled
live_ch4, live_h2 = None, None
if use_wireless:
    try:
        response = requests.get(arduino_ip, timeout=2)
        if response.status_code == 200:
            hw_data = response.json()
            live_ch4 = hw_data.get("ch4_ppm")
            live_h2 = hw_data.get("h2_ppm")
            st.sidebar.success("🟢 Wireless Hardware Connected")
        else:
            st.sidebar.warning("⚠️ Hardware Unreachable. Using Fallback.")
    except Exception as e:
        st.sidebar.error(f"❌ Connection Failed")

# --- SIDEBAR: USER INPUTS & PARAMETERS ---
st.sidebar.markdown("---")
st.sidebar.header("👨‍🚀 Astronaut Profile & Sensors")

astronaut_name = st.sidebar.text_input("Astronaut Name", "Commander Alex Doe")
mission_day = st.sidebar.slider("Mission Elapsed Day (MED)", 1, 365, 45)

st.sidebar.markdown("---")
st.sidebar.header("📊 Physiological Telemetry")
hr_bpm = st.sidebar.slider("Heart Rate (BPM)", 40, 160, 75)
spo2_val = st.sidebar.slider("Blood O2 Saturation (SpO2 %)", 75, 100, 97)

st.sidebar.markdown("---")
st.sidebar.header("🌌 Space Complication Metrics")
icp_mmhg = st.sidebar.slider("Intracranial Pressure (mmHg)", 5.0, 25.0, 12.5)
radiation_msv = st.sidebar.slider("Cumulative Radiation (mSv)", 0.0, 500.0, 42.3)
muscle_mass_pct = st.sidebar.slider("Muscle Mass Retention Score (%)", 40.0, 100.0, 88.5)
bone_density = st.sidebar.slider("Bone Density T-Score Index", 20.0, 100.0, 82.0)

st.sidebar.markdown("---")
st.sidebar.header("🧪 Cabin Gas Sensors (Arduino Link)")
default_ch4 = live_ch4 if live_ch4 is not None else 350.0  # PPM
default_h2 = live_h2 if live_h2 is not None else 120.0   # PPM
ch4_ppm = st.sidebar.slider("Methane (CH4) Density (PPM)", 0.0, 5000.0, float(default_ch4))
h2_ppm = st.sidebar.slider("Hydrogen (H2) Density (PPM)", 0.0, 2000.0, float(default_h2))

# --- CALCULATIONS & EVALUATIONS ---
cardio_score = float(np.clip(100 - abs(hr_bpm - 72) * 1.5, 0, 100))
spo2_score = float(np.clip((spo2_val - 80) * 5, 0, 100))
icp_score = float(np.clip(100 - max(0, (icp_mmhg - 15.0) * 10), 0, 100))
rad_score = float(np.clip(100 - (radiation_msv / 500.0) * 100, 0, 100))
muscle_score = float(np.clip(muscle_mass_pct, 0, 100))

# Gas safety scores (CH4 safe < 1000 ppm, H2 safe < 400 ppm)
ch4_score = float(np.clip(100 - (ch4_ppm / 5000.0) * 100, 0, 100))
h2_score = float(np.clip(100 - (h2_ppm / 2000.0) * 100, 0, 100))

weights = {
    'cardio': 0.18, 'o2': 0.18, 'icp': 0.14, 
    'radiation': 0.14, 'muscle': 0.14, 'bone': 0.12, 'gas': 0.10
}
gas_composite = (ch4_score + h2_score) / 2.0
overall_score = (
    cardio_score * weights['cardio'] + 
    spo2_score * weights['o2'] + 
    icp_score * weights['icp'] + 
    rad_score * weights['radiation'] + 
    muscle_score * weights['muscle'] + 
    bone_density * weights['bone'] +
    gas_composite * weights['gas']
)

status_str = "OPTIMAL" if overall_score >= 80 else ("WARNING" if overall_score >= 60 else "CRITICAL")
color_hex = "#22C55E" if overall_score >= 80 else ("#EAB308" if overall_score >= 60 else "#EF4444")
css_class = "optimal" if overall_score >= 80 else ("warning" if overall_score >= 60 else "critical")

# --- TOP ROW: GAUGE & PROFILE ---
col_gauge, col_profile = st.columns([2, 1])

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number", 
    value=overall_score, 
    domain={'x': [0, 1], 'y': [0, 1]}, 
    title={'text': f"Flight Readiness & Environment Index — <b>{status_str}</b>", 'font': {'size': 18, 'color': "white"}}, 
    number={'suffix': "%", 'font': {'color': color_hex, 'size': 36}}, 
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"}, 
        'bar': {'color': color_hex, 'thickness': 0.3}, 
        'bgcolor': "#1E293B", 
        'steps': [
            {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.2)'}, 
            {'range': [60, 80], 'color': 'rgba(234, 179, 8, 0.2)'}, 
            {'range': [80, 100], 'color': 'rgba(34, 197, 94, 0.2)'}
        ]
    }
))
fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=260, margin=dict(l=20, r=20, t=30, b=20))

col_gauge.plotly_chart(fig_gauge, use_container_width=True)

col_profile.subheader(f"Profile: {astronaut_name}")
col_profile.write(f"**Mission Day:** MED-{mission_day}")
col_profile.write(f"**Hardware Link:** {'Active Wi-Fi 🟢' if use_wireless else 'Simulation Mode ⚙️'}")
col_profile.markdown(f'<div class="status-card {css_class}">System Health: {status_str}</div>', unsafe_allow_html=True)

st.markdown("---")

# --- SECOND ROW: SUBSYSTEM METRIC CARDS ---
st.subheader("Subsystem Telemetry: Space Complications")
m1, m2, m3, m4, m5, m6 = st.columns(6)

c_status = "OPTIMAL" if cardio_score >= 80 else ("WARNING" if cardio_score >= 60 else "CRITICAL")
o_status = "OPTIMAL" if spo2_score >= 80 else ("WARNING" if spo2_score >= 60 else "CRITICAL")
i_status = "OPTIMAL" if icp_score >= 80 else ("WARNING" if icp_score >= 60 else "CRITICAL")
r_status = "OPTIMAL" if rad_score >= 80 else ("WARNING" if rad_score >= 60 else "CRITICAL")
mu_status = "OPTIMAL" if muscle_score >= 80 else ("WARNING" if muscle_score >= 60 else "CRITICAL")
b_status = "OPTIMAL" if bone_density >= 80 else ("WARNING" if bone_density >= 60 else "CRITICAL")

m1.metric("Cardiovascular", f"{hr_bpm} BPM", delta=c_status, delta_color="normal" if cardio_score>=80 else "inverse")
m2.metric("Blood O2", f"{spo2_val}%", delta=o_status, delta_color="normal" if spo2_score>=80 else "inverse")
m3.metric("Fluid Shift", f"{icp_mmhg} mmHg", delta=i_status, delta_color="normal" if icp_score>=80 else "inverse")
m4.metric("Radiation", f"{radiation_msv:.1f} mSv", delta=r_status, delta_color="normal" if rad_score>=80 else "inverse")
m5.metric("Muscle Retention", f"{muscle_mass_pct}%", delta=mu_status, delta_color="normal" if muscle_score>=80 else "inverse")
m6.metric("Bone Density", f"{bone_density}%", delta=b_status, delta_color="normal" if bone_density>=80 else "inverse")

st.markdown("---")

# --- THIRD ROW: COLOR-GRADED GAS INTENSITY BARS (CH4 & H2) ---
st.subheader("🧪 Arduino Sensor Array: Cabin Gas Density & Intensity")

col_gas1, col_gas2 = st.columns(2)

# Color Grading logic for Methane (Safe < 1000, Warning < 3000, Critical >= 3000)
ch4_color = "#15803D" if ch4_ppm < 1000 else ("#A16207" if ch4_ppm < 3000 else "#B91C1C")
ch4_pct = min(100.0, (ch4_ppm / 5000.0) * 100.0)

with col_gas1:
    st.markdown("**Methane ($CH_4$) Concentration**")
    st.markdown(f"""
        <div class="gas-bar-container">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;">
                <span>{ch4_ppm} PPM</span>
                <span style="color: {ch4_color};">{'SAFE' if ch4_ppm < 1000 else ('ELEVATED' if ch4_ppm < 3000 else 'CRITICAL HAZARD')}</span>
            </div>
            <div style="background-color: #334155; border-radius: 4px; overflow: hidden; height: 16px; width: 100%;">
                <div style="background-color: {ch4_color}; width: {ch4_pct}%; height: 100%; transition: width 0.4s ease;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Color Grading logic for Hydrogen (Safe < 400, Warning < 1000, Critical >= 1000)
h2_color = "#15803D" if h2_ppm < 400 else ("#A16207" if h2_ppm < 1000 else "#B91C1C")
h2_pct = min(100.0, (h2_ppm / 2000.0) * 100.0)

with col_gas2:
    st.markdown("**Hydrogen ($H_2$) Concentration**")
    st.markdown(f"""
        <div class="gas-bar-container">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;">
                <span>{h2_ppm} PPM</span>
                <span style="color: {h2_color};">{'SAFE' if h2_ppm < 400 else ('ELEVATED' if h2_ppm < 1000 else 'CRITICAL HAZARD')}</span>
            </div>
            <div style="background-color: #334155; border-radius: 4px; overflow: hidden; height: 16px; width: 100%;">
                <div style="background-color: {h2_color}; width: {h2_pct}%; height: 100%; transition: width 0.4s ease;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- FOURTH ROW: LIVE WAVEFORM SIGNAL GRAPH ---
st.subheader("Live Photoplethysmography (PPG) Waveform")
t = np.linspace(0, 4, 400)
freq = hr_bpm / 60.0
ppg_signal = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)

fig_wave = go.Figure()
fig_wave.add_trace(go.Scatter(x=t, y=ppg_signal, mode='lines', line=dict(color='#38BDF8', width=3)))
fig_wave.update_layout(
    xaxis_title="Time (seconds)", 
    yaxis_title="Optical Signal Voltage (mV)", 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='#1E293B', 
    font={'color': "white"}, 
    height=240, 
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_wave, use_container_width=True)