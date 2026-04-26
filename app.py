import streamlit as st
import time
from datetime import datetime
import plotly.graph_objects as go
import sports_core as sc

st.set_page_config(page_title="AGATHA OS | Command Center", layout="wide", initial_sidebar_state="collapsed")
sc.set_agatha_theme()

st.markdown("""
<style>
    .header-container { border-bottom: 1px solid #30363D; padding-top: 1rem; padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; }
    .main-title { font-size: 4rem; font-weight: 900; text-shadow: 0 0 15px rgba(236, 239, 244, 0.2); line-height: 0.8; letter-spacing: -2px; margin: 0; }
    .sub-title { color: #88C0D0; font-size: 1rem; letter-spacing: 3px; margin-top: 10px; }
    .kpi-container { background: #0D1117; border: 1px solid #30363D; padding: 15px; text-align: center; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); }
    .kpi-value { font-family: 'Rajdhani', sans-serif; font-size: 2.5rem; font-weight: bold; color: #ECEFF4; }
    .kpi-label { font-size: 0.8rem; color: #8B949E; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-saas { color: #58a6ff; }
    .hud-card { background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(13, 17, 23, 0.98) 100%); border: 1px solid #30363D; padding: 20px; height: 100%; min-height: 240px; transition: all 0.3s ease; }
    .hud-card:hover { transform: translateY(-2px); background: rgba(30, 35, 45, 1); box-shadow: 0 10px 20px rgba(0,0,0,0.4); }
    .card-header { font-family: 'Rajdhani', sans-serif; font-size: 1.5rem; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }
    .card-body { color: #8B949E; font-size: 0.85rem; line-height: 1.5; border-top: 1px solid #30363D; padding-top: 10px; margin-top: 10px; margin-bottom: 20px; }
    .terminal-feed { background-color: #0D1117; border: 1px solid #30363D; padding: 15px; height: 200px; overflow-y: hidden; color: #A3BE8C; font-size: 0.8rem; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    .live-indicator { color: #BF616A; animation: pulse 2s infinite; font-weight: bold; }
    .border-cyan { border-top: 3px solid #88C0D0; }
    .border-purple { border-top: 3px solid #E040FB; }
    .border-yellow { border-top: 3px solid #EBCB8B; }
    .border-red { border-top: 3px solid #BF616A; }
    .b2c-box { background-color: #0D1117; border: 1px solid #30363D; border-left: 4px solid #58a6ff; padding: 20px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

def create_gauge_chart(value, title, color):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, title={'text': title, 'font': {'color': '#8B949E', 'size': 12}}, number={'font': {'color': '#ECEFF4', 'size': 20}}, gauge={'axis': {'range':[None, 100], 'tickwidth': 1, 'tickcolor': "#30363D"}, 'bar': {'color': color}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 1, 'bordercolor': "#30363D"}))
    fig.update_layout(height=150, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'family': "Share Tech Mono"})
    return fig

def main():
    st.markdown("""
    <div class="header-container">
        <div>
            <h1 class="main-title">AGATHA OS <span style="font-size:1.5rem; color:#4C566A; vertical-align:middle;">ENTERPRISE EDITION</span></h1>
            <div class="sub-title">/// BEHAVIORAL SPORTS INTELLIGENCE PIPELINE</div>
        </div>
        <div style="text-align:right; font-size: 0.9rem; color:#5E81AC;">
            <div>SYS_TIME: <span style="color:#ECEFF4;">{}</span></div>
            <div>STATUS: <span class="live-indicator">[REC] SECURE UPLINK</span></div>
        </div>
    </div>
    """.format(datetime.now().strftime('%H:%M:%S ZULU')), unsafe_allow_html=True)

    st.markdown("<p style='color:#8B949E; font-weight:bold; margin-bottom: 5px;'>[ ECONOMÍA SAAS / B2B TELEMETRY ]</p>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.markdown("""<div class="kpi-container"><div class="kpi-value kpi-saas">12,450 €</div><div class="kpi-label">MRR (RECURRENTE MENSUAL)</div></div>""", unsafe_allow_html=True)
    with s2: st.markdown("""<div class="kpi-container"><div class="kpi-value kpi-saas">450 €</div><div class="kpi-label">LTV (LIFE TIME VALUE)</div></div>""", unsafe_allow_html=True)
    with s3: st.markdown("""<div class="kpi-container"><div class="kpi-value" style="color:#A3BE8C;">45 €</div><div class="kpi-label">CAC (COSTE ADQUISICIÓN)</div></div>""", unsafe_allow_html=True)
    with s4: st.markdown("""<div class="kpi-container"><div class="kpi-value" style="color:#A3BE8C;">1.2%</div><div class="kpi-label">CHURN RATE (BAJAS)</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<p style='color:#8B949E; font-weight:bold; margin-bottom: 5px;'>[ ADMINISTRACIÓN DE INFRAESTRUCTURA (C2) ]</p>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="hud-card border-cyan"><div class="card-header" style="color:#88C0D0;">[1] MOTOR PREDICTIVO</div><div class="card-body">Modelado matemático, cálculo True Odds y ejecución de alertas Push.</div></div>""", unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(98, "CPU LOAD", "#88C0D0"), use_container_width=True, config={'displayModeBar': False})
        if st.button("INICIAR INFERENCIA", key="btn_pred"): st.switch_page("pages/1_Motor_Predictivo.py")
    with c2:
        st.markdown("""<div class="hud-card border-purple"><div class="card-header" style="color:#E040FB;">[2] RADAR MERCADO</div><div class="card-body">Detección de Sharp Money y algoritmo RandomForest de sesgo poblacional.</div></div>""", unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(100, "ODDS API SYNC", "#E040FB"), use_container_width=True, config={'displayModeBar': False})
        if st.button("ABRIR RADAR", key="btn_radar"): st.switch_page("pages/2_Radar_Mercado.py")
    with c3:
        st.markdown("""<div class="hud-card border-yellow"><div class="card-header" style="color:#EBCB8B;">[3] MONITOR TÁCTICO</div><div class="card-body">Ingesta de matriz de alineaciones, reportes de lesiones críticas.</div></div>""", unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(72, "DATA VOLATILITY", "#EBCB8B"), use_container_width=True, config={'displayModeBar': False})
        if st.button("VER MONITOR", key="btn_monitor"): st.switch_page("pages/3_Monitor_Tactico.py")
    with c4:
        st.markdown("""<div class="hud-card border-red"><div class="card-header" style="color:#BF616A;">[4] AUDITORÍA & BACKTEST</div><div class="card-body">Simulador Forense de Montecarlo, Criterio Kelly y PnL histórico.</div></div>""", unsafe_allow_html=True)
        st.plotly_chart(create_gauge_chart(15, "RISK EXPOSURE", "#BF616A"), use_container_width=True, config={'displayModeBar': False})
        if st.button("ACCESO AUDITORÍA", key="btn_audit"): st.switch_page("pages/4_Auditoria_Bankroll.py")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<p style='color:#8B949E; font-weight:bold; margin-bottom: 5px;'>[ CAPA 5 / INTERFAZ DE SUSCRIPTOR (B2C) ]</p>", unsafe_allow_html=True)
    st.markdown("""<div class="b2c-box"><h3 style="color: #58a6ff; margin-top: 0; font-family: 'Rajdhani', sans-serif;">PORTAL DE ENTREGABLES (CLIENTE FINAL)</h3><p style="color: #8B949E; font-family: 'Share Tech Mono', monospace; font-size: 0.9rem;">Incluye simulador matemático interactivo para próximos encuentros.</p></div>""", unsafe_allow_html=True)
    col_btn, _ = st.columns([0.25, 0.75])
    with col_btn:
        st.markdown("""<style>div.stButton > button[kind="secondary"] { border-color: #58a6ff !important; color: #58a6ff !important; } div.stButton > button[kind="secondary"]:hover { background-color: rgba(88, 166, 255, 0.1) !important; box-shadow: 0 0 10px #58a6ff; }</style>""", unsafe_allow_html=True)
        if st.button("ABRIR VISTA DE SUSCRIPTOR (B2C)", key="btn_b2c"): st.switch_page("pages/5_Portal_Suscriptor.py")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8B949E; font-weight:bold; margin-bottom: 5px;'>[ SYS.LOGS / ACTIVITY FEED ]</p>", unsafe_allow_html=True)
    current_t = datetime.now().strftime('%H:%M:%S')
    logs_html = f"<div class='terminal-feed'><div>>[{current_t}] [INFO] Predictive Engine v10.1 loaded.</div><div style='color:#58a6ff;'>> [{current_t}] [SaaS] Stripe API sync completed. MRR updated.</div><div style='color:#EBCB8B;'>>[{current_t}] [WARN] Anomalous odds drop detected.</div><div>> [{current_t}][SYS] Awaiting Operator Directive...</div></div>"
    st.markdown(logs_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
