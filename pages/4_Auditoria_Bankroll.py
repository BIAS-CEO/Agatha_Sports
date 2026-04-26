import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import sports_core as sc

st.set_page_config(page_title="Auditoría Bankroll | AGATHA", layout="wide")
sc.set_agatha_theme()
sc.return_to_main()

st.markdown("""<style>div.stButton > button { border-color: #BF616A !important; color: #BF616A !important; } div.stButton > button:hover { background-color: rgba(191, 97, 106, 0.1) !important; }</style>""", unsafe_allow_html=True)
st.markdown("<h1 style='color:#BF616A;'>[4] AUDITORÍA Y RIESGO</h1>", unsafe_allow_html=True)
st.markdown("---")

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

st.markdown("---")
np.random.seed(42)
cuotas = np.random.uniform(1.8, 2.5, 30)
stakes = np.random.uniform(10, 50, 30)
res = np.random.binomial(1, 1/cuotas + 0.04)
df = pd.DataFrame({'fecha': [datetime.now() - timedelta(days=x) for x in range(30)][::-1], 'pnl': np.where(res==1, stakes*(cuotas-1), -stakes)})
df['bank'] = 1000 + df['pnl'].cumsum()

fig = px.area(df, x='fecha', y='bank', title="Evolución", color_discrete_sequence=['#BF616A'])
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8B949E'))
st.plotly_chart(fig, use_container_width=True)
