import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Health Evaluator HUD", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("<style>.main { background-color: #0F172A; } div[data-testid='stMetricValue'] { font-size: 28px; font-weight: bold; } .status-card { padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: center; font-weight: bold; font-size: 18px; color: white; } .optimal { background-color: #15803D; } .warning { background-color: #A16207; } .critical { background-color: #B91C1C; }</style>", unsafe_allow_html=True)

st.title("🩺 Health Status & Telemetry HUD")

# --- SIDEBAR: USER INPUTS & PARAMETERS ---
st.sidebar.header("👤 User Profile & Live Sensors")

user_name = st.sidebar.text_input("User Name", "Alex Doe")
age = st.sidebar.slider("Age", 18, 90, 30)
is_smoker = st.sidebar.checkbox("Smoker / Respiratory Baseline Adjustment")

st.sidebar.markdown("---")
st.sidebar.header("📊 Live Telemetry Controls")
hr_bpm = st.sidebar.slider("Heart Rate (BPM)", 40, 140, 72)
spo2_val = st.sidebar.slider("Blood O2 Saturation (SpO2 %)", 80, 100, 98)
bone_density = st.sidebar.slider("Bone Density Score", 20, 100, 85)
skin_hydration = st.sidebar.slider("Skin Hydration Score", 20, 100, 78)

# --- CALCULATIONS & EVALUATIONS ---
spo2_threshold = 92.0 if is_smoker else 95.0
spo2_score = float(np.clip((spo2_val - 80) * 5, 0, 100))

max_hr = 220 - age
cardio_score = float(np.clip(100 - abs(hr_bpm - 70) * 1.5, 0, 100))

vascular_score = float(np.clip((spo2_val / 100.0) * (100 - abs(hr_bpm - 75)), 0, 100))

weights = {'cardio': 0.25, 'o2': 0.25, 'flow': 0.20, 'bone': 0.15, 'skin': 0.15}
overall_score = (cardio_score * weights['cardio'] + spo2_score * weights['o2'] + vascular_score * weights['flow'] + bone_density * weights['bone'] + skin_hydration * weights['skin'])

# Status evaluation inline (no function/indent needed)
status_str = "OPTIMAL" if overall_score >= 80 else ("WARNING" if overall_score >= 60 else "CRITICAL")
color_hex = "#22C55E" if overall_score >= 80 else ("#EAB308" if overall_score >= 60 else "#EF4444")
css_class = "optimal" if overall_score >= 80 else ("warning" if overall_score >= 60 else "critical")

# --- TOP ROW: OVERALL WELLBEING GAUGE & PROFILE ---
col_gauge, col_profile = st.columns([2, 1])

fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=overall_score, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': f"Overall Wellbeing Index — <b>{status_str}</b>", 'font': {'size': 20, 'color': "white"}}, number={'suffix': "%", 'font': {'color': color_hex, 'size': 40}}, gauge={'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"}, 'bar': {'color': color_hex, 'thickness': 0.3}, 'bgcolor': "#1E293B", 'steps': [{'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.2)'}, {'range': [60, 80], 'color': 'rgba(234, 179, 8, 0.2)'}, {'range': [80, 100], 'color': 'rgba(34, 197, 94, 0.2)'}]}))
fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=280, margin=dict(l=20, r=20, t=40, b=20))

col_gauge.plotly_chart(fig_gauge, use_container_width=True)

col_profile.subheader(f"Profile: {user_name}")
col_profile.write(f"**Age:** {age} yrs | **Max HR:** {max_hr} BPM")
col_profile.write(f"**Respiratory Baseline:** {'Smoker' if is_smoker else 'Standard Non-Smoker'}")
col_profile.markdown(f'<div class="status-card {css_class}">Status: {status_str}</div>', unsafe_allow_html=True)

st.markdown("---")

# --- SECOND ROW: DOMAIN METRIC CARDS ---
st.subheader("Subsystem Visual Status")
m1, m2, m3, m4, m5 = st.columns(5)

c_status = "OPTIMAL" if cardio_score >= 80 else ("WARNING" if cardio_score >= 60 else "CRITICAL")
o_status = "OPTIMAL" if spo2_score >= 80 else ("WARNING" if spo2_score >= 60 else "CRITICAL")
v_status = "OPTIMAL" if vascular_score >= 80 else ("WARNING" if vascular_score >= 60 else "CRITICAL")
b_status = "OPTIMAL" if bone_density >= 80 else ("WARNING" if bone_density >= 60 else "CRITICAL")
s_status = "OPTIMAL" if skin_hydration >= 80 else ("WARNING" if skin_hydration >= 60 else "CRITICAL")

m1.metric("Cardiovascular", f"{hr_bpm} BPM", delta=c_status, delta_color="normal" if cardio_score>=80 else "inverse")
m2.metric("Blood O2 (SpO2)", f"{spo2_val}%", delta=o_status, delta_color="normal" if spo2_score>=80 else "inverse")
m3.metric("Vascular Flow", f"{vascular_score:.0f} PI", delta=v_status, delta_color="normal" if vascular_score>=80 else "inverse")
m4.metric("Bone Health", f"{bone_density}%", delta=b_status, delta_color="normal" if bone_density>=80 else "inverse")
m5.metric("Skin Hydration", f"{skin_hydration}%", delta=s_status, delta_color="normal" if skin_hydration>=80 else "inverse")

# --- THIRD ROW: LIVE WAVEFORM SIGNAL GRAPH ---
st.subheader("Live Photoplethysmography (PPG) Waveform")
t = np.linspace(0, 4, 400)
freq = hr_bpm / 60.0
ppg_signal = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)

fig_wave = go.Figure()
fig_wave.add_trace(go.Scatter(x=t, y=ppg_signal, mode='lines', line=dict(color='#38BDF8', width=3)))
fig_wave.update_layout(xaxis_title="Time (seconds)", yaxis_title="Optical Signal Voltage (mV)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#1E293B', font={'color': "white"}, height=250, margin=dict(l=20, r=20, t=20, b=20))

st.plotly_chart(fig_wave, use_container_width=True)
