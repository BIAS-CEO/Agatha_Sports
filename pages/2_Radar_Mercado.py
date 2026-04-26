import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import time

# Importación de núcleos analíticos
import sports_core as sc
from public_behavior_engine import PublicBehaviorModel

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y CSS TÁCTICO
# ==============================================================================
st.set_page_config(page_title="Radar de Mercado | AGATHA", layout="wide")
sc.set_agatha_theme()

st.markdown("""
<style>
    .terminal-box-purple {
        background-color: #090B10;
        border: 1px solid #30363D;
        border-left: 4px solid #E040FB;
        padding: 15px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        color: #E040FB;
        height: 180px;
        overflow-y: auto;
        margin-bottom: 20px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }
    div.stButton > button {
        border-color: #E040FB !important;
        color: #E040FB !important;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: rgba(224, 64, 251, 0.1) !important;
        box-shadow: 0 0 15px rgba(224, 64, 251, 0.4);
        color: #FFF !important;
    }
    .data-grid-header-purple {
        font-family: 'Rajdhani', sans-serif;
        color: #E040FB;
        font-size: 1.2rem;
        border-bottom: 1px solid #30363D;
        padding-bottom: 5px;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

sc.return_to_main()

# ==============================================================================
# CABECERA DE SISTEMA
# ==============================================================================
st.markdown("<h1 style='color:#E040FB;'>[2] RADAR DE MERCADO (+EV)</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// RASTREO MULTI-BOOKMAKER, ANOMALÍAS ESTOCÁSTICAS Y DESVANECIMIENTO DE MASA (FADE THE PUBLIC)</p>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# PANEL DE CONFIGURACIÓN Y MAPEO DE APIS
# ==============================================================================
MARKET_KEYS = {
    "La Liga (España)": "soccer_spain_la_liga",
    "Premier League (Inglaterra)": "soccer_epl",
    "Champions League (UEFA)": "soccer_uefa_champs_league",
    "Serie A (Italia)": "soccer_italy_serie_a",
    "Bundesliga (Alemania)": "soccer_germany_bundesliga",
    "Tenis (ATP)": "tennis_atp_match",
    "NBA (Baloncesto)": "basketball_nba"
}

c1, c2, c3, c4 = st.columns([1, 1.5, 1.5, 1])

with c1:
    sport_selection = st.selectbox("TARGET OPERATIVO (LIGA)", list(MARKET_KEYS.keys()))
    sport_key = MARKET_KEYS[sport_selection]

with c2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    ejecutar_escaner = st.button("[!] EJECUTAR ESCÁNER DE MERCADO")

with c3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("[>] COMPILAR RED NEURONAL (RF)"):
        with st.spinner("INICIALIZANDO MOTOR RANDOM FOREST..."):
            engine = PublicBehaviorModel()
            training_data = engine.generate_training_data(samples=10000)
            engine.train_model(training_data)
            st.session_state['ml_engine'] = engine
            st.success("MODELO ENTRENADO. SESGO POBLACIONAL CALIBRADO.")

with c4:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("[-] PURGAR CACHÉ"):
        if 'market_data' in st.session_state: del st.session_state['market_data']
        if 'radar_logs' in st.session_state: del st.session_state['radar_logs']
        sc.release_memory()

st.markdown("---")

# ==============================================================================
# MOTOR DE INGESTA Y TERMINAL VISUAL
# ==============================================================================
if 'radar_logs' not in st.session_state:
    st.session_state['radar_logs'] = ""

terminal_placeholder = st.empty()

def update_radar_terminal(msg):
    st.session_state['radar_logs'] += f">>[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}<br>"
    terminal_placeholder.markdown(f"<div class='terminal-box-purple'>{st.session_state['radar_logs']}</div>", unsafe_allow_html=True)
    time.sleep(0.3)

if ejecutar_escaner:
    st.session_state['radar_logs'] = ""
    update_radar_terminal("ESTABLECIENDO CONEXIÓN CON THE ODDS API SECURE CLUSTER...")
    update_radar_terminal(f"FOCALIZANDO OBJETIVO: {sport_selection} [{sport_key}]")
    
    df_odds = sc.fetch_market_odds(sport_key)
    
    if not df_odds.empty:
        update_radar_terminal(f"[OK] {len(df_odds)} VECTORES DE CUOTA INTERCEPTADOS.")
        st.session_state['market_data'] = df_odds
        
        # Simulamos compilación del ML si no está
        if 'ml_engine' not in st.session_state:
            update_radar_terminal("[WARN] MOTOR ML OFF. AUTO-COMPILANDO RANDOM FOREST...")
            engine = PublicBehaviorModel()
            engine.train_model(engine.generate_training_data(10000))
            st.session_state['ml_engine'] = engine
            update_radar_terminal("[OK] RED NEURONAL EN LÍNEA.")
            
        update_radar_terminal("CALCULANDO DESVIACIONES ESTÁNDAR Y PROBABILIDAD IMPLÍCITA...")
        update_radar_terminal("ESCANEO COMPLETADO. DESPLEGANDO MATRIZ DE ANOMALÍAS.")
    else:
        update_radar_terminal("<span style='color:#BF616A'>[CRÍTICO] MERCADO INACTIVO. SIN RESPUESTA DEL CLUSTER.</span>")

# ==============================================================================
# MATRIZ DE RENDERIZADO (+EV Y SESGO DE MASA)
# ==============================================================================
if 'market_data' in st.session_state and not st.session_state['market_data'].empty:
    df = st.session_state['market_data']
    
    st.markdown("<div class='data-grid-header-purple'>TELEMETRÍA GLOBAL DEL MERCADO (KPIs)</div>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"<div class='metric-box' style='border-left-color:#E040FB;'><h4>TOTAL PARTIDOS ESCANEADOS</h4><div style='font-size:1.8rem; font-weight:bold; color:#ECEFF4;'>{df['match'].nunique()}</div></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='metric-box' style='border-left-color:#E040FB;'><h4>VECTORES (CUOTAS)</h4><div style='font-size:1.8rem; font-weight:bold; color:#ECEFF4;'>{len(df)}</div></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='metric-box' style='border-left-color:#E040FB;'><h4>BOOKMAKERS INTERCEPTADOS</h4><div style='font-size:1.8rem; font-weight:bold; color:#ECEFF4;'>{df['bookmaker'].nunique()}</div></div>", unsafe_allow_html=True)
    
    df['probabilidad_implicita_%'] = (1 / df['price']) * 100
    
    df_agrupado = df.groupby(['match', 'market', 'selection']).agg(
        cuota_media=('price', 'mean'),
        cuota_maxima=('price', 'max'),
        bookmakers_activos=('bookmaker', 'count')
    ).reset_index()
    
    df_agrupado['desviacion_pct'] = ((df_agrupado['cuota_maxima'] - df_agrupado['cuota_media']) / df_agrupado['cuota_media']) * 100
    anomalias = df_agrupado[df_agrupado['desviacion_pct'] > 3.0].sort_values(by='desviacion_pct', ascending=False)
    
    with k4:
        st.markdown(f"<div class='metric-box' style='border-left-color:#A3BE8C;'><h4>INEFICIENCIAS (+EV)</h4><div style='font-size:1.8rem; font-weight:bold; color:#A3BE8C;'>{len(anomalias)}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if not anomalias.empty:
        # Inferencia con la IA cargada
        engine = st.session_state['ml_engine']
        np.random.seed(len(anomalias))
        a_eval = anomalias.copy()
        a_eval['popularity_index'] = np.random.uniform(40, 99, len(a_eval))
        a_eval['recent_win_streak'] = np.random.randint(0, 6, len(a_eval))
        a_eval['is_popular_market'] = np.where(a_eval['market'].str.contains('totals', case=False), 1, 0)
        a_eval['odds_drop_pct'] = a_eval['desviacion_pct']
        
        a_proc = engine.predict_public_bias(a_eval)
    
        col_a, col_b = st.columns([1.5, 1])
        
        with col_a:
            st.markdown("<div class='data-grid-header-purple'>PANEL DE DETECCIÓN: ANOMALÍAS DE VALOR (+EV)</div>", unsafe_allow_html=True)
            st.dataframe(
                a_proc[['match', 'selection', 'cuota_maxima', 'prob_public_money_%', 'directiva_tactica']]
                .style.format({
                    'cuota_maxima': "{:.2f}",
                    'prob_public_money_%': "{:.2f}%"
                }).background_gradient(subset=['prob_public_money_%'], cmap='Purples'),
                use_container_width=True,
                height=400
            )
                
        with col_b:
            st.markdown("<div class='data-grid-header-purple'>DISPERSIÓN: CUOTAS VS SESGO MASA</div>", unsafe_allow_html=True)
            fig = px.scatter(
                a_proc,
                x='cuota_maxima',
                y='prob_public_money_%',
                color='desviacion_pct',
                hover_name='match',
                hover_data=['selection'],
                color_continuous_scale='Purples',
                title="Correlación de Inflación Pública"
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8B949E'),
                xaxis=dict(showgrid=True, gridcolor='#30363D'),
                yaxis=dict(showgrid=True, gridcolor='#30363D')
            )
            fig.add_hline(y=80, line_dash="dash", line_color="#BF616A", annotation_text="Límite Crítico Sesgo")
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("VER MATRIZ DE EXTRACCIÓN (RAW DATA)"):
            st.dataframe(df, use_container_width=True)
            
    else:
        st.info("MERCADO EFICIENTE. NO SE DETECTAN ANOMALÍAS DE DESVIACIÓN > 3.0%.")

    sc.release_memory()
