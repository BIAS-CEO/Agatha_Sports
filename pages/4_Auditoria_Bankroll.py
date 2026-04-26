import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Importación del núcleo analítico
import sports_core as sc

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y CSS TÁCTICO
# ==============================================================================
st.set_page_config(page_title="Auditoría Bankroll | AGATHA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #050505; font-family: 'Share Tech Mono', monospace; color: #ECEFF4; }
    h1, h2, h3, h4 { font-family: 'Rajdhani', sans-serif; color: #BF616A; text-transform: uppercase; }
    .metric-box {
        border-left: 4px solid #BF616A;
        background-color: #161B22;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value-pos { color: #A3BE8C; font-size: 1.5rem; font-weight: bold; }
    .metric-value-neg { color: #BF616A; font-size: 1.5rem; font-weight: bold; }
    div.stButton > button {
        border: 1px solid #BF616A !important;
        background-color: rgba(191, 97, 106, 0.1) !important;
        color: #BF616A !important;
        border-radius: 0px !important;
        width: 100%;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover { background-color: rgba(191, 97, 106, 0.3) !important; box-shadow: 0 0 10px #BF616A; }
    [data-testid="stDataFrame"] { background-color: #0D1117; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CABECERA DE SISTEMA
# ==============================================================================
st.markdown("<h1>[4] AUDITORÍA DE BANKROLL Y GESTIÓN DE RIESGO</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// CÁLCULO DE CRITERIO DE KELLY, YIELD HISTÓRICO Y EVALUACIÓN DE DRAWDOWN</p>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# FUNCIONES MATEMÁTICAS
# ==============================================================================
def calcular_kelly(prob_real_pct: float, cuota_decimal: float, bankroll_actual: float, fraction: float = 0.25) -> dict:
    """
    Calcula el Criterio de Kelly para determinar el tamaño óptimo de la inversión.
    Utiliza Kelly Fraccional (defecto 1/4) para reducir la volatilidad y el riesgo de ruina.
    """
    p = prob_real_pct / 100.0
    q = 1.0 - p
    b = cuota_decimal - 1.0
    
    if b <= 0:
        return {"porcentaje": 0.0, "monto": 0.0, "estado": "CUOTA INVÁLIDA"}
        
    f_star = (b * p - q) / b
    
    if f_star <= 0:
        return {"porcentaje": 0.0, "monto": 0.0, "estado": "NO APOSTAR (EV NEGATIVO)"}
        
    kelly_fraccional = f_star * fraction
    monto_recomendado = bankroll_actual * kelly_fraccional
    
    return {
        "porcentaje": round(kelly_fraccional * 100, 2),
        "monto": round(monto_recomendado, 2),
        "estado": "VALOR DETECTADO (+EV)"
    }

def generar_historico_simulado() -> pd.DataFrame:
    """
    Genera un registro vectorial simulado de 100 operaciones para la evaluación de la interfaz.
    En producción, este módulo se conectará a PostgreSQL.
    """
    np.random.seed(42)
    dias = 30
    fechas =[datetime.now() - timedelta(days=x) for x in range(dias)]
    fechas.reverse()
    
    # Parámetros del simulador (Yield objetivo ~4%)
    cuotas = np.random.uniform(1.80, 2.50, dias)
    stakes = np.random.uniform(10, 50, dias)
    win_prob = 1 / cuotas + 0.04  # Edge simulado
    resultados = np.random.binomial(1, win_prob)
    
    profit = np.where(resultados == 1, stakes * (cuotas - 1), -stakes)
    bankroll_inicial = 1000
    bankroll_evolucion = bankroll_inicial + np.cumsum(profit)
    
    df = pd.DataFrame({
        'fecha': fechas,
        'cuota': cuotas,
        'stake_eur': stakes,
        'resultado': np.where(resultados == 1, 'ACIERTO', 'FALLO'),
        'pnl': profit,
        'bankroll': bankroll_evolucion
    })
    return df

# ==============================================================================
# CALCULADORA TÁCTICA DE KELLY (INPUT DE OPERADOR)
# ==============================================================================
st.markdown("### CALCULADORA DE EXPOSICIÓN (KELLY FRACCIONAL)")

c1, c2, c3, c4 = st.columns(4)
with c1:
    input_bankroll = st.number_input("TESORERÍA (BANKROLL TOTAL €)", min_value=10.0, value=1000.0, step=10.0)
with c2:
    input_prob = st.number_input("PROBABILIDAD REAL IA (%)", min_value=1.0, max_value=99.0, value=55.0, step=0.1)
with c3:
    input_cuota = st.number_input("CUOTA OFRECIDA (DECIMAL)", min_value=1.01, value=2.00, step=0.01)
with c4:
    input_fraccion = st.selectbox("MULTIPLICADOR DE RIESGO",[("Conservador (1/8)", 0.125), ("Estándar (1/4)", 0.25), ("Agresivo (1/2)", 0.50)], index=1)

resultado_kelly = calcular_kelly(input_prob, input_cuota, input_bankroll, fraction=input_fraccion[1])

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
if resultado_kelly['monto'] > 0:
    st.markdown(f"""
    <div class='metric-box'>
        <span style='color:#8B949E; font-size:1.2rem;'>DIRECTIVA DE INVERSIÓN: </span>
        <span style='color:#A3BE8C; font-size:1.5rem; font-weight:bold;'>APROBADA</span><br>
        Unidad de exposición calculada: <strong>{resultado_kelly['porcentaje']}%</strong> del bankroll.<br>
        Monto exacto a comprometer: <span style='color:#EBCB8B; font-size:1.5rem;'>{resultado_kelly['monto']} €</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class='metric-box'>
        <span style='color:#8B949E; font-size:1.2rem;'>DIRECTIVA DE INVERSIÓN: </span>
        <span style='color:#BF616A; font-size:1.5rem; font-weight:bold;'>DENEGADA</span><br>
        Razón técnica: {resultado_kelly['estado']}. Esperanza matemática negativa o nula detectada.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# AUDITORÍA DE RENDIMIENTO (TELEMETRÍA HISTÓRICA)
# ==============================================================================
st.markdown("### PANEL DE RENDIMIENTO ACUMULADO (SIMULACIÓN DE MUESTRA)")

df_hist = generar_historico_simulado()

# Cálculos de KPI financieros
total_apostado = df_hist['stake_eur'].sum()
profit_total = df_hist['pnl'].sum()
yield_pct = (profit_total / total_apostado) * 100
winrate = (len(df_hist[df_hist['resultado'] == 'ACIERTO']) / len(df_hist)) * 100
drawdown = ((df_hist['bankroll'].max() - df_hist['bankroll'].iloc[-1]) / df_hist['bankroll'].max()) * 100

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.markdown("#### YIELD ACUMULADO")
    clase_yield = "metric-value-pos" if yield_pct > 0 else "metric-value-neg"
    st.markdown(f"<div class='{clase_yield}'>{yield_pct:.2f}%</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with k2:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.markdown("#### PROFIT NETO (PNL)")
    clase_pnl = "metric-value-pos" if profit_total > 0 else "metric-value-neg"
    st.markdown(f"<div class='{clase_pnl}'>{profit_total:.2f} €</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with k3:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.markdown("#### TASA DE ACIERTO (WINRATE)")
    st.markdown(f"<div style='color:#EBCB8B; font-size: 1.5rem; font-weight: bold;'>{winrate:.1f}%</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with k4:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.markdown("#### DRAWDOWN ACTUAL")
    st.markdown(f"<div class='metric-value-neg'>{drawdown:.2f}%</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Renderizado de gráfico Plotly
fig = px.area(
    df_hist, 
    x='fecha', 
    y='bankroll', 
    title="Evolución del Vector de Capital (Bankroll)",
    color_discrete_sequence=['#BF616A']
)
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#8B949E'),
    xaxis=dict(showgrid=True, gridcolor='#30363D'),
    yaxis=dict(showgrid=True, gridcolor='#30363D')
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("VER REGISTRO DE OPERACIONES CRUDAS (RAW LEDGER)"):
    st.dataframe(df_hist.style.format({
        'cuota': "{:.2f}",
        'stake_eur': "{:.2f} €",
        'pnl': "{:.2f} €",
        'bankroll': "{:.2f} €"
    }), use_container_width=True)

# Limpieza estricta
del df_hist
del fig
sc.release_memory()
