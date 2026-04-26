import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import sports_core as sc

st.set_page_config(page_title="Auditoría Bankroll | AGATHA", layout="wide")
sc.set_agatha_theme()

st.markdown("""
<style>
    div.stButton > button { border-color: #BF616A !important; color: #BF616A !important; }
    div.stButton > button:hover { background-color: rgba(191, 97, 106, 0.1) !important; box-shadow: 0 0 10px #BF616A; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#BF616A;'>[4] AUDITORÍA DE BANKROLL Y RIESGO</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// CRITERIO DE KELLY, YIELD HISTÓRICO Y EVALUACIÓN DE DRAWDOWN</p>", unsafe_allow_html=True)
st.markdown("---")

def calcular_kelly(prob_real_pct: float, cuota_decimal: float, bankroll: float, fraction: float = 0.25) -> dict:
    p = prob_real_pct / 100.0
    q = 1.0 - p
    b = cuota_decimal - 1.0
    if b <= 0: return {"porcentaje": 0.0, "monto": 0.0, "estado": "CUOTA INVÁLIDA"}
    f_star = (b * p - q) / b
    if f_star <= 0: return {"porcentaje": 0.0, "monto": 0.0, "estado": "NO APOSTAR (-EV)"}
    kelly_f = f_star * fraction
    return {"porcentaje": round(kelly_f * 100, 2), "monto": round(bankroll * kelly_f, 2), "estado": "VALOR DETECTADO (+EV)"}

def generar_historico_simulado() -> pd.DataFrame:
    np.random.seed(42)
    fechas = [datetime.now() - timedelta(days=x) for x in range(30)][::-1]
    cuotas = np.random.uniform(1.80, 2.50, 30)
    stakes = np.random.uniform(10, 50, 30)
    resultados = np.random.binomial(1, 1 / cuotas + 0.04)
    profit = np.where(resultados == 1, stakes * (cuotas - 1), -stakes)
    return pd.DataFrame({'fecha': fechas, 'cuota': cuotas, 'stake': stakes, 'resultado': np.where(resultados == 1, 'ACIERTO', 'FALLO'), 'pnl': profit, 'bankroll': 1000 + np.cumsum(profit)})

st.markdown("<h3 style='color:#BF616A;'>CALCULADORA DE EXPOSICIÓN (KELLY)</h3>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: input_bank = st.number_input("BANKROLL TOTAL (€)", value=1000.0, step=10.0)
with c2: input_prob = st.number_input("PROBABILIDAD REAL IA (%)", value=55.0, step=0.1)
with c3: input_cuota = st.number_input("CUOTA OFRECIDA", value=2.00, step=0.01)
with c4: input_frac = st.selectbox("MULTIPLICADOR",[("Conservador", 0.125), ("Estándar", 0.25), ("Agresivo", 0.50)], index=1)

res = calcular_kelly(input_prob, input_cuota, input_bank, fraction=input_frac[1])

if res['monto'] > 0:
    st.markdown(f"<div class='metric-box'><span style='color:#8B949E'>DIRECTIVA: </span><span style='color:#A3BE8C; font-size:1.5rem; font-weight:bold;'>APROBADA</span><br>Exposición: <strong>{res['porcentaje']}%</strong> | Monto: <span style='color:#EBCB8B; font-size:1.5rem;'>{res['monto']} €</span></div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='metric-box'><span style='color:#8B949E'>DIRECTIVA: </span><span style='color:#BF616A; font-size:1.5rem; font-weight:bold;'>DENEGADA</span><br>Razón: {res['estado']}</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h3 style='color:#BF616A;'>RENDIMIENTO ACUMULADO</h3>", unsafe_allow_html=True)

df_hist = generar_historico_simulado()
y_pct = (df_hist['pnl'].sum() / df_hist['stake'].sum()) * 100
pnl = df_hist['pnl'].sum()
wr = (len(df_hist[df_hist['resultado'] == 'ACIERTO']) / len(df_hist)) * 100
dd = ((df_hist['bankroll'].max() - df_hist['bankroll'].iloc[-1]) / df_hist['bankroll'].max()) * 100

k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='metric-box'><h4>YIELD</h4><div class='{'metric-value-pos' if y_pct>0 else 'metric-value-neg'}'>{y_pct:.2f}%</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='metric-box'><h4>PROFIT</h4><div class='{'metric-value-pos' if pnl>0 else 'metric-value-neg'}'>{pnl:.2f} €</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='metric-box'><h4>WINRATE</h4><div style='color:#EBCB8B; font-size:1.5rem; font-weight:bold;'>{wr:.1f}%</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='metric-box'><h4>DRAWDOWN</h4><div class='metric-value-neg'>{dd:.2f}%</div></div>", unsafe_allow_html=True)

fig = px.area(df_hist, x='fecha', y='bankroll', title="Evolución de Capital", color_discrete_sequence=['#BF616A'])
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8B949E'))
st.plotly_chart(fig, use_container_width=True)

with st.expander("VER REGISTRO CRUDO"): st.dataframe(df_hist, use_container_width=True)
sc.release_memory()
