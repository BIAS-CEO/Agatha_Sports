import streamlit as st
import time
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN BASE DEL SISTEMA
# ==============================================================================
st.set_page_config(
    page_title="AGATHA OS | Sports Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# INYECCIÓN CSS TÁCTICO (HUD V4 DEPURADO)
# ==============================================================================
st.markdown("""
<style>
    /* FONDO GENERAL SCANLINE */
    .stApp {
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
            linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        background-size: 100% 2px, 3px 100%;
        font-family: 'Share Tech Mono', monospace;
    }

    /* OCULTAR ELEMENTOS NATIVOS */
    [data-testid="stHeader"] { display: none !important; }

    /* HEADER SYSTEM */
    .header-container {
        border-bottom: 2px solid #30363D;
        padding-top: 2rem;
        padding-bottom: 20px;
        margin-bottom: 40px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    
    .main-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        color: #ECEFF4;
        text-shadow: 0 0 20px rgba(236, 239, 244, 0.3);
        line-height: 0.8;
        letter-spacing: -2px;
        margin: 0;
    }
    
    .sub-title {
        font-family: 'Share Tech Mono', monospace;
        color: #88C0D0;
        font-size: 1.2rem;
        letter-spacing: 4px;
        margin-top: 5px;
    }

    /* TARJETAS HUD */
    .hud-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(13, 17, 23, 0.98) 100%);
        border: 1px solid #30363D;
        position: relative;
        padding: 25px;
        height: 100%;
        min-height: 220px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }
    
    .hud-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        border-width: 0 30px 30px 0;
        border-style: solid;
        border-color: #0d1117 rgba(0,0,0,0) rgba(0,0,0,0) #0d1117; 
        display: block;
        width: 0;
    }

    /* BORDES DE COLOR */
    .border-cyan { border-left: 4px solid #88C0D0; }
    .border-purple { border-left: 4px solid #E040FB; }
    .border-yellow { border-left: 4px solid #EBCB8B; }
    .border-red { border-left: 4px solid #BF616A; }

    /* HOVER EFFECTS */
    .hud-card:hover {
        transform: translateY(-5px);
        background: rgba(30, 35, 45, 1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .hud-card:hover.border-cyan { box-shadow: 0 0 20px rgba(136, 192, 208, 0.2); border-color: #88C0D0; }
    .hud-card:hover.border-purple { box-shadow: 0 0 20px rgba(224, 64, 251, 0.2); border-color: #E040FB; }
    .hud-card:hover.border-yellow { box-shadow: 0 0 20px rgba(235, 203, 139, 0.2); border-color: #EBCB8B; }
    .hud-card:hover.border-red { box-shadow: 0 0 20px rgba(191, 97, 106, 0.2); border-color: #BF616A; }

    .card-icon { 
        font-family: 'Share Tech Mono', monospace; 
        font-size: 1.5rem; 
        font-weight: bold;
        margin-bottom: 15px; 
        opacity: 0.8; 
    }
    
    .card-header { 
        font-family: 'Rajdhani', sans-serif; 
        font-size: 1.8rem; 
        font-weight: 800; 
        color: #fff; 
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    
    .card-body {
        font-family: 'Share Tech Mono', monospace;
        color: #8B949E;
        font-size: 0.9rem;
        line-height: 1.6;
        border-top: 1px solid #30363D;
        padding-top: 15px;
        margin-top: 10px;
    }

    /* BOTONES */
    div.stButton > button {
        background-color: transparent !important;
        border: 1px solid #4C566A !important;
        color: #88C0D0 !important;
        font-family: 'Share Tech Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
        width: 100%;
        border-radius: 0px !important;
    }
    div.stButton > button:hover {
        border-color: #88C0D0 !important;
        background-color: rgba(136, 192, 208, 0.1) !important;
        box-shadow: 0 0 10px rgba(136, 192, 208, 0.2);
    }

    /* TERMINAL LOGS */
    .kernel-log {
        font-family: 'Share Tech Mono', monospace;
        color: #4C566A;
        font-size: 0.8rem;
        margin-top: 50px;
        border-top: 1px dashed #30363D;
        padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# RENDERIZADO DE INTERFAZ
# ==============================================================================
def main():
    # --- HEADER ---
    st.markdown("""
    <div class="header-container">
        <div>
            <h1 class="main-title">AGATHA OS <span style="font-size:2rem; color:#4C566A; vertical-align:middle;">v10.1</span></h1>
            <div class="sub-title">/// BEHAVIORAL SPORTS INTELLIGENCE</div>
        </div>
        <div style="text-align:right; font-family:'Share Tech Mono'; color:#5E81AC;">
            <div>SYS_TIME: <span style="color:#ECEFF4;">{}</span></div>
            <div>LOC: <span style="color:#ECEFF4;">MAIN-NODE</span></div>
            <div style="color:#A3BE8C;">[+] ONLINE</div>
        </div>
    </div>
    """.format(datetime.now().strftime('%H:%M:%S ZULU')), unsafe_allow_html=True)

    # --- GRID OPERATIVO ---
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="hud-card border-cyan">
            <div class="card-icon" style="color:#88C0D0;">[ MODELO MATEMÁTICO ]</div>
            <div class="card-header">1. MOTOR PREDICTIVO</div>
            <div class="card-body">
                <span style="color:#88C0D0;">>> STATUS: ACTIVO</span><br><br>
                Procesamiento de estadística avanzada, cálculo de probabilidad real (True Odds) y modelado de escenarios.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("INICIAR INFERENCIA", key="btn_pred"):
            st.switch_page("pages/1_Motor_Predictivo.py")

    with c2:
        st.markdown("""
        <div class="hud-card border-purple">
            <div class="card-icon" style="color:#E040FB;">[ ESCÁNER EV ]</div>
            <div class="card-header">2. RADAR DE MERCADO</div>
            <div class="card-body">
                <span style="color:#E040FB;">>> STATUS: READY</span><br><br>
                Detección de discrepancias en cuotas (Value Bets), seguimiento de movimientos de líneas y dinero institucional.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("ABRIR RADAR DE VALOR", key="btn_radar"):
            st.switch_page("pages/2_Radar_Mercado.py")

    st.write("") 

    c3, c4 = st.columns(2)

    with c3:
        st.markdown("""
        <div class="hud-card border-yellow">
            <div class="card-icon" style="color:#EBCB8B;">[ TELEMETRÍA ]</div>
            <div class="card-header">3. MONITOR TÁCTICO</div>
            <div class="card-body">
                <span style="color:#EBCB8B;">>> STATUS: MONITORING</span><br><br>
                Ingesta de datos en tiempo real: alineaciones confirmadas, bajas críticas y variables meteorológicas operativas.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("VER MONITOR TÁCTICO", key="btn_monitor"):
            st.switch_page("pages/3_Monitor_Tactico.py")

    with c4:
        st.markdown("""
        <div class="hud-card border-red">
            <div class="card-icon" style="color:#BF616A;">[ CONTROL DE RIESGO ]</div>
            <div class="card-header">4. AUDITORÍA BANKROLL</div>
            <div class="card-body">
                <span style="color:#BF616A;">>> STATUS: SECURE</span><br><br>
                Gestión de capital mediante Criterio de Kelly. Análisis de Yield, ROI acumulado y calibración del algoritmo.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("ACCESO A AUDITORÍA", key="btn_audit"):
            st.switch_page("pages/4_Auditoria_Bankroll.py")

    # --- LOGS DE TERMINAL ---
    logs_html = "<div class='kernel-log'>"
    logs = [
        "[KERNEL] Predictive Engine v1.0 loaded in 14ms",
        "[NET] Uplink established to API_FOOTBALL cluster",
        "[NET] Uplink established to ODDS_API exchange",
        "[SYS] Waiting for operator directive..."
    ]
    for log in logs:
        logs_html += f"<div>> {log}</div>"
    logs_html += "</div>"

    st.markdown(logs_html, unsafe_allow_html=True)

    # RECARGA FORZADA
    if 'booted' not in st.session_state:
        st.session_state.booted = True
        time.sleep(0.5)
        st.rerun()

if __name__ == "__main__":
    main()
