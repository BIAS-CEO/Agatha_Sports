import streamlit as st
import time
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURACIÓN BASE DEL SISTEMA
# ==============================================================================
st.set_page_config(
    page_title="AGATHA OS | Command Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# INYECCIÓN CSS TÁCTICO AVANZADO (HUD V5 - ENTERPRISE)
# ==============================================================================
st.markdown("""
<style>
    .stApp {
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
            linear-gradient(90deg, rgba(255, 0, 0, 0.04), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.04));
        background-size: 100% 2px, 3px 100%;
        font-family: 'Share Tech Mono', monospace;
    }

    [data-testid="stHeader"] { display: none !important; }

    .header-container {
        border-bottom: 1px solid #30363D;
        padding-top: 1rem;
        padding-bottom: 10px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    
    .main-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        color: #ECEFF4;
        text-shadow: 0 0 15px rgba(236, 239, 244, 0.2);
        line-height: 0.8;
        letter-spacing: -2px;
        margin: 0;
    }
    
    .sub-title {
        font-family: 'Share Tech Mono', monospace;
        color: #88C0D0;
        font-size: 1rem;
        letter-spacing: 3px;
        margin-top: 10px;
    }

    .kpi-container {
        background: #0D1117;
        border: 1px solid #30363D;
        padding: 15px;
        text-align: center;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
    
    .kpi-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.5rem;
        font-weight: bold;
        color: #ECEFF4;
    }
    
    .kpi-label {
        font-size: 0.8rem;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .hud-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(13, 17, 23, 0.98) 100%);
        border: 1px solid #30363D;
        position: relative;
        padding: 20px;
        height: 100%;
        min-height: 240px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .border-cyan { border-top: 3px solid #88C0D0; }
    .border-purple { border-top: 3px solid #E040FB; }
    .border-yellow { border-top: 3px solid #EBCB8B; }
    .border-red { border-top: 3px solid #BF616A; }

    .hud-card:hover {
        transform: translateY(-2px);
        background: rgba(30, 35, 45, 1);
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }

    .card-header { 
        font-family: 'Rajdhani', sans-serif; 
        font-size: 1.5rem; 
        font-weight: 800; 
        color: #fff; 
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
    .card-body {
        font-family: 'Share Tech Mono', monospace;
        color: #8B949E;
        font-size: 0.85rem;
        line-height: 1.5;
        border-top: 1px solid #30363D;
        padding-top: 10px;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    div.stButton > button {
        background-color: transparent !important;
        border: 1px solid #4C566A !important;
        color: #ECEFF4 !important;
        font-family: 'Share Tech Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        width: 100%;
        border-radius: 0px !important;
    }
    
    div.stButton > button:hover {
        border-color: #88C0D0 !important;
        background-color: rgba(136, 192, 208, 0.1) !important;
        color: #88C0D0 !important;
    }

    .terminal-feed {
        background-color: #0D1117;
        border: 1px solid #30363D;
        padding: 15px;
        height: 200px;
        overflow-y: hidden;
        font-family: 'Share Tech Mono', monospace;
        color: #A3BE8C;
        font-size: 0.8rem;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }
    .live-indicator {
        color: #BF616A;
        animation: pulse 2s infinite;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# FUNCIONES AUXILIARES (SIMULACIÓN DE TELEMETRÍA)
# ==============================================================================
def create_gauge_chart(value, title, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'color': '#8B949E', 'size': 12}},
        number = {'font': {'color': '#ECEFF4', 'size': 20}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#30363D"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 1,
            'bordercolor': "#30363D",
        }
    ))
    fig.update_layout(
        height=150, 
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'family': "Share Tech Mono"}
    )
    return fig

# ==============================================================================
# RENDERIZADO DE INTERFAZ
# ==============================================================================
def main():
    # --- HEADER ---
    st.markdown("""
    <div class="header-container">
        <div>
            <h1 class="main-title">AGATHA OS <span style="font-size:1.5rem; color:#4C566A; vertical-align:middle;">ENTERPRISE EDITION</span></h1>
            <div class="sub-title">/// BEHAVIORAL SPORTS INTELLIGENCE PIPELINE</div>
        </div>
        <div style="text-align:right; font-family:'Share Tech Mono'; color:#5E81AC; font-size: 0.9rem;">
            <div>SYS_TIME: <span style="color:#ECEFF4;">{}</span></div>
            <div>STATUS: <span class="live-indicator">[REC] SECURE UPLINK</span></div>
            <div style="color:#A3BE8C;">DEFCON 5 / NORMAL OP</div>
        </div>
    </div>
    """.format(datetime.now().strftime('%H:%M:%S ZULU')), unsafe_allow_html=True)

    # --- GLOBAL MACRO-METRICS (KPI ROW) ---
    st.markdown("<p style='color:#8B949E; font-weight:bold; margin-bottom: 5px;'>[ SYSTEM TELEMETRY / GLOBAL OVERVIEW ]</p>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""
        <div class="kpi-container">
            <div class="kpi-value">2,104</div>
            <div class="kpi-label">NODOS ANALIZADOS (24H)</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown("""
        <div class="kpi-container">
            <div class="kpi-value" style="color:#EBCB8B;">14</div>
            <div class="kpi-label">VALUE BETS DETECTADAS (+EV)</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown("""
        <div class="kpi-container">
            <div class="kpi-value" style="color:#A3BE8C;">+4.2%</div>
            <div class="kpi-label">YIELD ACUMULADO (30D)</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown("""
        <div class="kpi-container">
            <div class="kpi-value" style="color:#E040FB;">89.4%</div>
            <div class="kpi-label">MERCADO EFICIENTE (CALIBRACIÓN)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- COMMAND GRID ---
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="hud-card border-cyan">
            <div class="card-header">[1] MOTOR PREDICTIVO</div>
            <div class="card-body">
                Modelado matemático, cálculo True Odds y ejecución protocolo Billy Walters. Extracción estructurada de API-Football.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(98, "CPU LOAD", "#88C0D0"), use_container_width=True, config={'displayModeBar': False})
        if st.button("INICIAR INFERENCIA", key="btn_pred"):
            st.switch_page("pages/1_Motor_Predictivo.py")

    with c2:
        st.markdown("""
        <div class="hud-card border-purple">
            <div class="card-header">[2] RADAR MERCADO</div>
            <div class="card-body">
                Detección asimétrica de cuotas. Rastreo de Sharp Money y algoritmo RandomForest de sesgo poblacional.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(100, "ODDS API SYNC", "#E040FB"), use_container_width=True, config={'displayModeBar': False})
        if st.button("ABRIR RADAR", key="btn_radar"):
            st.switch_page("pages/2_Radar_Mercado.py")

    with c3:
        st.markdown("""
        <div class="hud-card border-yellow">
            <div class="card-header">[3] MONITOR TÁCTICO</div>
            <div class="card-body">
                Ingesta en vivo de matriz de alineaciones, reportes de lesiones críticas e impacto de ecosistema.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(72, "DATA VOLATILITY", "#EBCB8B"), use_container_width=True, config={'displayModeBar': False})
        if st.button("VER MONITOR", key="btn_monitor"):
            st.switch_page("pages/3_Monitor_Tactico.py")

    with c4:
        st.markdown("""
        <div class="hud-card border-red">
            <div class="card-header">[4] AUDITORÍA & RIESGO</div>
            <div class="card-body">
                Control fraccional de Criterio de Kelly. Trazabilidad de operaciones, análisis de Drawdown y tesorería.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(15, "RISK EXPOSURE", "#BF616A"), use_container_width=True, config={'displayModeBar': False})
        if st.button("ACCESO AUDITORÍA", key="btn_audit"):
            st.switch_page("pages/4_Auditoria_Bankroll.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LIVE TERMINAL FEED ---
    st.markdown("<p style='color:#8B949E; font-weight:bold; margin-bottom: 5px;'>[ SYS.LOGS / ACTIVITY FEED ]</p>", unsafe_allow_html=True)
    
    current_t = datetime.now().strftime('%H:%M:%S')
    logs = [
        f"[{current_t}] [INFO] Predictive Engine v10.1 loaded. Memory mapping optimized.",
        f"[{current_t}] [NET] Uplink established to API_FOOTBALL cluster... Latency 24ms.",
        f"[{current_t}] [NET] Synchronizing with The Odds API global exchange...",
        f"[{current_t}] [SEC] Public Behavior Machine Learning model (RandomForest) initialized in background.",
        f"[{current_t}] [WARN] Anomalous odds drop detected in market: soccer_epl. Logging to DB.",
        f"[{current_t}] [SYS] Awaiting Operator Directive..."
    ]
    
    logs_html = "<div class='terminal-feed'>"
    for log in logs:
        if "[WARN]" in log:
            logs_html += f"<div style='color:#EBCB8B;'>> {log}</div>"
        elif "[SEC]" in log:
            logs_html += f"<div style='color:#E040FB;'>> {log}</div>"
        else:
            logs_html += f"<div>> {log}</div>"
    logs_html += "</div>"

    st.markdown(logs_html, unsafe_allow_html=True)

    # RECARGA FORZADA PARA EFECTO HUD
    if 'booted' not in st.session_state:
        st.session_state.booted = True
        time.sleep(0.5)
        st.rerun()

if __name__ == "__main__":
    main()
