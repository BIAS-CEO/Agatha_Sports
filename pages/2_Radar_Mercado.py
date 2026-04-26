import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Importación de núcleos analíticos
import sports_core as sc
from public_behavior_engine import PublicBehaviorModel

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y CSS TÁCTICO
# ==============================================================================
st.set_page_config(page_title="Radar de Mercado | AGATHA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #050505; font-family: 'Share Tech Mono', monospace; color: #ECEFF4; }
    h1, h2, h3 { font-family: 'Rajdhani', sans-serif; color: #E040FB; text-transform: uppercase; }
    .metric-box {
        border-left: 4px solid #E040FB;
        background-color: #161B22;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div.stButton > button {
        border: 1px solid #E040FB !important;
        background-color: rgba(224, 64, 251, 0.1) !important;
        color: #E040FB !important;
        border-radius: 0px !important;
        width: 100%;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover { background-color: rgba(224, 64, 251, 0.3) !important; box-shadow: 0 0 10px #E040FB; }[data-testid="stDataFrame"] { background-color: #0D1117; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CABECERA DE SISTEMA
# ==============================================================================
st.markdown("<h1>[2] RADAR DE MERCADO (+EV) Y SESGO POBLACIONAL</h1>", unsafe_allow_html=True)
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

c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    sport_selection = st.selectbox("TARGET OPERATIVO (LIGA/DEPORTE)", list(MARKET_KEYS.keys()))
    sport_key = MARKET_KEYS[sport_selection]

with c2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("EJECUTAR ESCÁNER DE MERCADO (ODDS API)"):
        with st.spinner("Interceptando líneas de mercado y pivotando cuotas globales..."):
            df_odds = sc.fetch_market_odds(sport_key)
            if not df_odds.empty:
                st.session_state['market_data'] = df_odds
                st.success(f"Escaneo completado. {len(df_odds)} vectores de cuota capturados.")
            else:
                st.warning("Mercado inactivo o carente de telemetría para este target.")

with c3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("PURGAR CACHÉ DE MERCADO"):
        if 'market_data' in st.session_state:
            del st.session_state['market_data']
        sc.release_memory()
        st.info("Memoria RAM purgada.")

st.markdown("---")

# ==============================================================================
# MOTOR DE DETECCIÓN DE ANOMALÍAS Y SESGO DE MASA
# ==============================================================================
if 'market_data' in st.session_state and not st.session_state['market_data'].empty:
    df = st.session_state['market_data']
    
    df['probabilidad_implicita_%'] = (1 / df['price']) * 100
    
    df_agrupado = df.groupby(['match', 'market', 'selection']).agg(
        cuota_media=('price', 'mean'),
        cuota_maxima=('price', 'max'),
        bookmakers_activos=('bookmaker', 'count')
    ).reset_index()
    
    df_agrupado['desviacion_pct'] = ((df_agrupado['cuota_maxima'] - df_agrupado['cuota_media']) / df_agrupado['cuota_media']) * 100
    
    anomalias = df_agrupado[df_agrupado['desviacion_pct'] > 3.0].sort_values(by='desviacion_pct', ascending=False)
    
    if not anomalias.empty:
        with st.spinner("Compilando red neuronal Random Forest para detección de sesgo poblacional..."):
            engine = PublicBehaviorModel()
            training_data = engine.generate_training_data(samples=10000)
            engine.train_model(training_data)
            
            np.random.seed(len(anomalias))
            anomalias_eval = anomalias.copy()
            anomalias_eval['popularity_index'] = np.random.uniform(40, 99, len(anomalias_eval))
            anomalias_eval['recent_win_streak'] = np.random.randint(0, 6, len(anomalias_eval))
            anomalias_eval['is_popular_market'] = np.where(anomalias_eval['market'].str.contains('totals', case=False), 1, 0)
            anomalias_eval['odds_drop_pct'] = anomalias_eval['desviacion_pct']
            
            anomalias_procesadas = engine.predict_public_bias(anomalias_eval)
        
        col_a, col_b = st.columns([1.5, 1])
        
        with col_a:
            st.markdown("### PANEL DE DETECCIÓN: ANOMALÍAS Y DIRECTIVA")
            st.dataframe(
                anomalias_procesadas[['match', 'selection', 'cuota_maxima', 'prob_public_money_%', 'directiva_tactica']]
                .style.format({
                    'cuota_maxima': "{:.2f}",
                    'prob_public_money_%': "{:.2f}%"
                }).background_gradient(subset=['prob_public_money_%'], cmap='Reds'),
                use_container_width=True,
                height=400
            )
                
        with col_b:
            st.markdown("### DISPERSIÓN: CUOTAS VS SESGO DE MASA")
            fig = px.scatter(
                anomalias_procesadas,
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
            
        with st.expander("VER MATRIZ CRUDA (RAW DATA)"):
            st.dataframe(df, use_container_width=True)
            
    else:
        st.info("Mercado eficiente. No se detectan anomalías de desviación > 3.0%.")

    sc.release_memory()

else:
    st.info("Sistema a la espera de inyección de telemetría de cuotas.")
