import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sports_core as sc
from public_behavior_engine import PublicBehaviorModel

st.set_page_config(page_title="Radar de Mercado | AGATHA", layout="wide")
sc.set_agatha_theme()
sc.return_to_main()

st.markdown("""<style>div.stButton > button { border-color: #E040FB !important; color: #E040FB !important; } div.stButton > button:hover { background-color: rgba(224, 64, 251, 0.1) !important; box-shadow: 0 0 10px #E040FB; }</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#E040FB;'>[2] RADAR DE MERCADO (+EV)</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// RASTREO MULTI-BOOKMAKER Y SESGO POBLACIONAL</p>", unsafe_allow_html=True)
st.markdown("---")

MARKET_KEYS = {"La Liga": "soccer_spain_la_liga", "Premier": "soccer_epl", "Champions": "soccer_uefa_champs_league", "Serie A": "soccer_italy_serie_a", "Bundesliga": "soccer_germany_bundesliga"}

c1, c2, c3 = st.columns([1, 2, 1])
with c1: sport_key = MARKET_KEYS[st.selectbox("LIGA", list(MARKET_KEYS.keys()))]
with c2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("EJECUTAR ESCÁNER DE MERCADO"):
        with st.spinner("Interceptando líneas..."):
            df = sc.fetch_market_odds(sport_key)
            if not df.empty:
                st.session_state['market_data'] = df
                st.success("Escaneo completado.")
            else: st.warning("Mercado inactivo.")
with c3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("PURGAR CACHÉ"):
        if 'market_data' in st.session_state: del st.session_state['market_data']

st.markdown("---")
if 'market_data' in st.session_state and not st.session_state['market_data'].empty:
    df = st.session_state['market_data']
    df['prob'] = (1 / df['price']) * 100
    df_agrupado = df.groupby(['match', 'market', 'selection']).agg(c_med=('price', 'mean'), c_max=('price', 'max')).reset_index()
    df_agrupado['desv'] = ((df_agrupado['c_max'] - df_agrupado['c_med']) / df_agrupado['c_med']) * 100
    anomalias = df_agrupado[df_agrupado['desv'] > 3.0]
    
    if not anomalias.empty:
        with st.spinner("Compilando sesgo poblacional..."):
            engine = PublicBehaviorModel()
            engine.train_model(engine.generate_training_data(10000))
            a_eval = anomalias.copy()
            a_eval['popularity_index'] = np.random.uniform(40, 99, len(a_eval))
            a_eval['recent_win_streak'] = np.random.randint(0, 6, len(a_eval))
            a_eval['is_popular_market'] = np.where(a_eval['market'].str.contains('totals', case=False), 1, 0)
            a_eval['odds_drop_pct'] = a_eval['desv']
            a_proc = engine.predict_public_bias(a_eval)
        
        ca, cb = st.columns([1.5, 1])
        with ca:
            st.markdown("<h3 style='color:#E040FB;'>PANEL DE DETECCIÓN</h3>", unsafe_allow_html=True)
            st.dataframe(a_proc[['match', 'selection', 'c_max', 'prob_public_money_%', 'directiva_tactica']].style.background_gradient(subset=['prob_public_money_%'], cmap='Reds'), use_container_width=True)
        with cb:
            fig = px.scatter(a_proc, x='c_max', y='prob_public_money_%', color='desv', hover_name='match')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8B949E'))
            st.plotly_chart(fig, use_container_width=True)
    else: st.info("Mercado eficiente.")
    sc.release_memory()
