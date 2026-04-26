import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Importación del núcleo analítico
import sports_core as sc

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
    div.stButton > button:hover { background-color: rgba(224, 64, 251, 0.3) !important; box-shadow: 0 0 10px #E040FB; }
    
    /* Modificación de tablas dataframe */
    [data-testid="stDataFrame"] { background-color: #0D1117; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CABECERA DE SISTEMA
# ==============================================================================
st.markdown("<h1>[2] RADAR DE MERCADO (+EV)</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// RASTREO MULTI-BOOKMAKER, CÁLCULO DE PROBABILIDAD IMPLÍCITA Y DETECCIÓN DE ANOMALÍAS</p>", unsafe_allow_html=True)
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
# MOTOR DE DETECCIÓN DE ANOMALÍAS MATEMÁTICAS
# ==============================================================================
if 'market_data' in st.session_state and not st.session_state['market_data'].empty:
    df = st.session_state['market_data']
    
    # Cálculos vectorizados para eficiencia de memoria
    # 1. Probabilidad Implícita = (1 / Cuota) * 100
    df['probabilidad_implicita_%'] = (1 / df['price']) * 100
    
    # 2. Agrupación por Partido, Mercado y Selección para encontrar ineficiencias
    df_agrupado = df.groupby(['match', 'market', 'selection']).agg(
        cuota_media=('price', 'mean'),
        cuota_maxima=('price', 'max'),
        bookmakers_activos=('bookmaker', 'count')
    ).reset_index()
    
    # 3. Cálculo de Varianza (Edge inicial crudo)
    # Si la cuota máxima es significativamente más alta que la media, indica un desajuste.
    df_agrupado['desviacion_pct'] = ((df_agrupado['cuota_maxima'] - df_agrupado['cuota_media']) / df_agrupado['cuota_media']) * 100
    
    # Filtrar solo anomalías positivas (Cuotas máximas por encima de la media del mercado)
    anomalias = df_agrupado[df_agrupado['desviacion_pct'] > 3.0].sort_values(by='desviacion_pct', ascending=False)
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown("### PANEL DE DETECCIÓN DE ANOMALÍAS (+EV POTENCIAL)")
        if not anomalias.empty:
            st.dataframe(
                anomalias[['match', 'selection', 'cuota_media', 'cuota_maxima', 'desviacion_pct']]
                .style.format({
                    'cuota_media': "{:.2f}",
                    'cuota_maxima': "{:.2f}",
                    'desviacion_pct': "{:.2f}%"
                }).background_gradient(subset=['desviacion_pct'], cmap='Purples'),
                use_container_width=True,
                height=400
            )
        else:
            st.info("Mercado eficiente. No se detectan anomalías de desviación > 3.0%.")
            
    with col_b:
        st.markdown("### DISPERSIÓN DE LÍNEAS (SHARP VS PUBLIC)")
        # Gráfico Plotly para visualizar las anomalías
        if not anomalias.empty:
            fig = px.scatter(
                anomalias,
                x='cuota_media',
                y='cuota_maxima',
                color='desviacion_pct',
                hover_name='match',
                hover_data=['selection'],
                color_continuous_scale='Purples',
                title="Vector de Discrepancia: Media vs Máxima"
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8B949E'),
                xaxis=dict(showgrid=True, gridcolor='#30363D'),
                yaxis=dict(showgrid=True, gridcolor='#30363D')
            )
            # Línea de mercado perfecto (Media = Máxima)
            max_val = anomalias['cuota_maxima'].max()
            fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="#BF616A", dash="dash"))
            
            st.plotly_chart(fig, use_container_width=True)
            
            del fig
        else:
            st.write("Datos insuficientes para renderizar la dispersión espacial.")

    # Visor Raw de datos interceptados
    with st.expander("VER MATRIZ DE CUOTAS CRUDA (RAW DATA)"):
        st.dataframe(df, use_container_width=True)

    # Liberación explícita de DataFrames para prevención OOM
    del df
    del df_agrupado
    del anomalias
    sc.release_memory()

else:
    st.info("Sistema a la espera de inyección de telemetría de cuotas.")
