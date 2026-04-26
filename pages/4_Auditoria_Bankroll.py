import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import sports_core as sc

st.set_page_config(page_title="Auditoría Bankroll | AGATHA", layout="wide")
sc.set_agatha_theme()
sc.return_to_main()

st.markdown("""<style>.backtest-box { background-color: #0D1117; border: 1px solid #30363D; border-left: 4px solid #A3BE8C; padding: 20px; margin-top: 15px; } div.stButton > button { border-color: #BF616A !important; color: #BF616A !important; } div.stButton > button:hover { background-color: rgba(191, 97, 106, 0.1) !important; }</style>""", unsafe_allow_html=True)
st.markdown("<h1 style='color:#BF616A;'>[4] AUDITORÍA Y BACKTESTING FORENSE</h1>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["CALCULADORA KELLY", "MÁQUINA DE BACKTESTING"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    with c1: input_bank = st.number_input("BANKROLL (€)", value=10000.0)
    with c2: input_prob = st.number_input("PROBABILIDAD IA (%)", value=55.0)
    with c3: input_cuota = st.number_input("CUOTA", value=2.00)
    with c4: frac = st.selectbox("MULTIPLICADOR",[0.125, 0.25, 0.50], index=1)

    p, b = input_prob/100, input_cuota - 1
    f = (b*p-(1-p))/b * frac if b>0 else 0
    if f > 0: st.markdown(f"<div class='metric-box'><h2 style='color:#A3BE8C;'>APROBADA (+EV)</h2>Exposición: {round(f*100,2)}% | Monto: {round(input_bank*f, 2)} €</div>", unsafe_allow_html=True)
    else: st.markdown("<div class='metric-box'><h2 style='color:#BF616A;'>DENEGADA (-EV)</h2></div>", unsafe_allow_html=True)

with tab2:
    b1, b2, b3 = st.columns(3)
    with b1: edge_sim = st.slider("EDGE PROYECTADO (%)", 1.0, 10.0, 4.0)
    with b2: cuota_media = st.slider("CUOTA MEDIA", 1.50, 3.50, 1.95)
    with b3: start_bank = st.number_input("CAPITAL INICIAL (€)", value=10000.0)

    if st.button("[>] EJECUTAR BACKTEST"):
        with st.spinner("Procesando matriz histórica..."):
            np.random.seed(42)
            prob_real = (1/cuota_media) + (edge_sim/100)
            res = np.random.binomial(1, prob_real, 3000)
            capital =[start_bank]
            for r in res:
                stake = capital[-1] * 0.02
                capital.append(capital[-1] + (stake * (cuota_media - 1)) if r == 1 else capital[-1] - stake)
                
            df_b = pd.DataFrame({'Match': range(3001), 'Bankroll': capital})
            fig = px.line(df_b, x='Match', y='Bankroll', title=f"Curva a 5 años (Edge: {edge_sim}%)", color_discrete_sequence=['#A3BE8C'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8B949E'))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"<div class='backtest-box'><h3 style='color:#A3BE8C; margin:0;'>COMPLETADA</h3>Final Proyectado: <strong>{round(capital[-1], 2):,} €</strong><br>Retorno Neto: <strong>+{round(((capital[-1]-start_bank)/start_bank)*100, 2)}%</strong></div>", unsafe_allow_html=True)
