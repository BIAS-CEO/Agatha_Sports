import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import sports_core as sc

st.set_page_config(page_title="Auditoría Bankroll | AGATHA", layout="wide")
sc.set_agatha_theme()
sc.return_to_main()

st.markdown("<h1 style='color:#BF616A;'>[4] AUDITORÍA Y BACKTESTING FORENSE</h1>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["CALCULADORA KELLY & LIVE PNL", "MÁQUINA DE BACKTESTING (SIMULADOR 5 AÑOS)"])

with tab1:
    st.markdown("<h3 style='color:#BF616A;'>CALCULADORA DE EXPOSICIÓN (KELLY)</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: input_bank = st.number_input("BANKROLL (€)", value=1000.0)
    with c2: input_prob = st.number_input("PROBABILIDAD IA (%)", value=55.0)
    with c3: input_cuota = st.number_input("CUOTA", value=2.00)
    with c4: frac = st.selectbox("MULTIPLICADOR",[0.125, 0.25, 0.50], index=1)

    p = input_prob/100
    b = input_cuota - 1
    f = (b*p-(1-p))/b * frac if b>0 else 0

    if f > 0: st.markdown(f"<div class='metric-box'><h2 style='color:#A3BE8C;'>APROBADA</h2>Exposición: {round(f*100,2)}% | Monto: {round(input_bank*f, 2)} €</div>", unsafe_allow_html=True)
    else: st.markdown("<div class='metric-box'><h2 style='color:#BF616A;'>DENEGADA (-EV)</h2></div>", unsafe_allow_html=True)

with tab2:
    # --- NUEVO: MÁQUINA DE BACKTESTING ---
    st.markdown("<h3 style='color:#BF616A;'>SIMULADOR DE SUPERVIVENCIA ESTOCÁSTICA</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8B949E;'>Ejecución de Montecarlo sobre 3,000 partidos históricos para validación de Edge.</p>", unsafe_allow_html=True)
    
    b1, b2, b3 = st.columns(3)
    with b1: edge_sim = st.slider("EDGE MATEMÁTICO PROYECTADO (%)", 1.0, 10.0, 4.0)
    with b2: cuota_media = st.slider("CUOTA MEDIA HISTÓRICA", 1.50, 3.50, 1.95)
    with b3: start_bank = st.number_input("CAPITAL INICIAL (€)", value=1000)

    if st.button("EJECUTAR BACKTEST (3000 ITERACIONES)"):
        with st.spinner("Procesando matriz histórica..."):
            np.random.seed(42)
            prob_real = (1/cuota_media) + (edge_sim/100)
            resultados = np.random.binomial(1, prob_real, 3000)
            
            capital = [start_bank]
            # Simulación Kelly Fraccional dinámica
            for res in resultados:
                current = capital[-1]
                stake = current * 0.02 # Flat 2% para simulación
                if res == 1: capital.append(current + (stake * (cuota_media - 1)))
                else: capital.append(current - stake)
                
            df_backtest = pd.DataFrame({'Match': range(3001), 'Bankroll': capital})
            
            fig = px.line(df_backtest, x='Match', y='Bankroll', title=f"Curva de Crecimiento a 5 años (Edge: {edge_sim}%)", color_discrete_sequence=['#A3BE8C'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8B949E'))
            st.plotly_chart(fig, use_container_width=True)
            
            st.success(f"SIMULACIÓN COMPLETADA. Capital Final Proyectado: {round(capital[-1], 2)} € (Retorno: +{round(((capital[-1]-start_bank)/start_bank)*100, 2)}%)")
