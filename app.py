import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.signal import butter, filtfilt

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Health Evaluator HUD",
        page_icon="🩺",
            layout="wide",
                initial_sidebar_state="expanded"
                )

                # --- CUSTOM CSS FOR MOBILE HUD STYLING ---
                st.markdown("""
                    <style>
                        .main { background-color: #0F172A; }
                            div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
                                .status-card {
                                        padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: center;
                                                font-weight: bold; font-size: 18px; color: white;
                                                    }
                                                        .optimal { background-color: #15803D; }
                                                            .warning { background-color: #A16207; }
                                                                .critical { background-color: #B91C1C; }
                                                                    </style>
                                                                    """, unsafe_allow_html=True)

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
                                                                    # Smoker adjustment for O2 threshold
                                                                    spo2_threshold = 92.0 if is_smoker else 95.0
                                                                    spo2_score = float(np.clip((spo2_val - 80) * 5, 0, 100))

                                                                    # Cardiovascular score relative to age max HR
                                                                    max_hr = 220 - age
                                                                    cardio_score = float(np.clip(100 - abs(hr_bpm - 70) * 1.5, 0, 100))

                                                                    # Simulated vascular blood flow perfusion index
                                                                    vascular_score = float(np.clip((spo2_val / 100.0) * (100 - abs(hr_bpm - 75)), 0, 100))

                                                                    # Composite Wellbeing Index
                                                                    weights = {'cardio': 0.25, 'o2': 0.25, 'flow': 0.20, 'bone': 0.15, 'skin': 0.15}
                                                                    overall_score = (
                                                                        cardio_score * weights['cardio'] +
                                                                            spo2_score * weights['o2'] +
                                                                                vascular_score * weights['flow'] +
                                                                                    bone_density * weights['bone'] +
                                                                                        skin_hydration * weights['skin']
                                                                                        )

                                                                                        def get_status_info(score):
                                                                                            if score >= 80:
                                                                                                    return "OPTIMAL", "#22C55E", "optimal"
                                                                                                        elif score >= 60:
                                                                                                                return "WARNING", "#EAB308", "warning"
                                                                                                                    else:
                                                                                                                            return "CRITICAL", "#EF4444", "critical"

                                                                                                                            # --- TOP ROW: OVERALL WELLBEING GAUGE & PROFILE ---
                                                                                                                            col_gauge, col_profile = st.columns([2, 1])

                                                                                                                            with col_gauge:
                                                                                                                                status_str, color_hex, css_class = get_status_info(overall_score)
                                                                                                                                    fig_gauge = go.Figure(go.Indicator(
                                                                                                                                            mode="gauge+number",
                                                                                                                                                    value=overall_score,
                                                                                                                                                            domain={'x': [0, 1], 'y': [0, 1]},
                                                                                                                                                                    title={'text': f"Overall Wellbeing Index — <b>{status_str}</b>", 'font': {'size': 20, 'color': "white"}},
                                                                                                                                                                            number={'suffix': "%", 'font': {'color': color_hex, 'size': 40}},
                                                                                                                                                                                    gauge={
                                                                                                                                                                                                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                                                                                                                                                                                                            'bar': {'color': color_hex, 'thickness': 0.3},
                                                                                                                                                                                                                        'bgcolor': "#1E293B",
                                                                                                                                                                                                                                    'steps': [
                                                                                                                                                                                                                                                    {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.2)'},
                                                                                                                                                                                                                                                                    {'range': [60, 80], 'color': 'rgba(234, 179, 8, 0.2)'},
                                                                                                                                                                                                                                                                                    {'range': [80, 100], 'color': 'rgba(34, 197, 94, 0.2)'}
                                                                                                                                                                                                                                                                                                ],
                                                                                                                                                                                                                                                                                                        }
                                                                                                                                                                                                                                                                                                            ))
                                                                                                                                                                                                                                                                                                                fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=280, margin=dict(l=20, r=20, t=40, b=20))
                                                                                                                                                                                                                                                                                                                    st.plotly_chart(fig_gauge, use_container_width=True)

                                                                                                                                                                                                                                                                                                                    with col_profile:
                                                                                                                                                                                                                                                                                                                        st.subheader(f"Profile: {user_name}")
                                                                                                                                                                                                                                                                                                                            st.write(f"**Age:** {age} yrs | **Max HR:** {max_hr} BPM")
                                                                                                                                                                                                                                                                                                                                st.write(f"**Respiratory Baseline:** {'Smoker' if is_smoker else 'Standard Non-Smoker'}")
                                                                                                                                                                                                                                                                                                                                    st.markdown(f'<div class="status-card {css_class}">Status: {status_str}</div>', unsafe_allow_html=True)

                                                                                                                                                                                                                                                                                                                                    st.markdown("---")

                                                                                                                                                                                                                                                                                                                                    # --- SECOND ROW: DOMAIN METRIC CARDS ---
                                                                                                                                                                                                                                                                                                                                    st.subheader("Subsystem Visual Status")
                                                                                                                                                                                                                                                                                                                                    m1, m2, m3, m4, m5 = st.columns(5)

                                                                                                                                                                                                                                                                                                                                    with m1:
                                                                                                                                                                                                                                                                                                                                        s_str, col, _ = get_status_info(cardio_score)
                                                                                                                                                                                                                                                                                                                                            st.metric("Cardiovascular", f"{hr_bpm} BPM", delta=s_str, delta_color="normal" if cardio_score>=80 else "inverse")

                                                                                                                                                                                                                                                                                                                                            with m2:
                                                                                                                                                                                                                                                                                                                                                s_str, col, _ = get_status_info(spo2_score)
                                                                                                                                                                                                                                                                                                                                                    st.metric("Blood O2 (SpO2)", f"{spo2_val}%", delta=s_str, delta_color="normal" if spo2_score>=80 else "inverse")

                                                                                                                                                                                                                                                                                                                                                    with m3:
                                                                                                                                                                                                                                                                                                                                                        s_str, col, _ = get_status_info(vascular_score)
                                                                                                                                                                                                                                                                                                                                                            st.metric("Vascular Flow", f"{vascular_score:.0f} PI", delta=s_str, delta_color="normal" if vascular_score>=80 else "inverse")

                                                                                                                                                                                                                                                                                                                                                            with m4:
                                                                                                                                                                                                                                                                                                                                                                s_str, col, _ = get_status_info(bone_density)
                                                                                                                                                                                                                                                                                                                                                                    st.metric("Bone Health", f"{bone_density}%", delta=s_str, delta_color="normal" if bone_density>=80 else "inverse")

                                                                                                                                                                                                                                                                                                                                                                    with m5:
                                                                                                                                                                                                                                                                                                                                                                        s_str, col, _ = get_status_info(skin_hydration)
                                                                                                                                                                                                                                                                                                                                                                            st.metric("Skin Hydration", f"{skin_hydration}%", delta=s_str, delta_color="normal" if skin_hydration>=80 else "inverse")

                                                                                                                                                                                                                                                                                                                                                                            # --- THIRD ROW: LIVE WAVEFORM SIGNAL GRAPH ---
                                                                                                                                                                                                                                                                                                                                                                            st.subheader("Live Photoplethysmography (PPG) Waveform")
                                                                                                                                                                                                                                                                                                                                                                            t = np.linspace(0, 4, 400)
                                                                                                                                                                                                                                                                                                                                                                            freq = hr_bpm / 60.0
                                                                                                                                                                                                                                                                                                                                                                            ppg_signal = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)

                                                                                                                                                                                                                                                                                                                                                                            fig_wave = go.Figure()
                                                                                                                                                                                                                                                                                                                                                                            fig_wave.add_trace(go.Scatter(x=t, y=ppg_signal, mode='lines', line=dict(color='#38BDF8', width=3)))
                                                                                                                                                                                                                                                                                                                                                                            fig_wave.update_layout(
                                                                                                                                                                                                                                                                                                                                                                                xaxis_title="Time (seconds)", yaxis_title="Optical Signal Voltage (mV)",
                                                                                                                                                                                                                                                                                                                                                                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#1E293B',
                                                                                                                                                                                                                                                                                                                                                                                        font={'color': "white"}, height=250, margin=dict(l=20, r=20, t=20, b=20)
                                                                                                                                                                                                                                                                                                                                                                                        )
                                                                                                                                                                                                                                                                                                                                                                                        st.plotly_chart(fig_wave, use_container_width=True)
                                                                                                                                                                                                                                                                                                                                                                                        