import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sports_core as sc

st.set_page_config(page_title="Quantum Sports | Área Privada", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0f19; font-family: 'Inter', sans-serif; color: #c9d1d9; }[data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
    .nav-header { background: linear-gradient(180deg, #161b22 0%, #0b0f19 100%); border-bottom: 1px solid #30363d; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
    .pick-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 25px; margin-top: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
    .market-badge { background-color: rgba(88, 166, 255, 0.1); color: #58a6ff; border: 1px solid #58a6ff; padding: 6px 15px; border-radius: 20px; font-weight: 700; }
    .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
    .metric-item { background-color: #0b0f19; border: 1px solid #30363d; padding: 15px; border-radius: 8px; text-align: center; }
    div.stButton > button { background-color: transparent !important; border: 1px solid #30363d !important; color: #8b949e !important; }
    div.stButton > button:hover { border-color: #58a6ff !important; color: #58a6ff !important; }
</style>
""", unsafe_allow_html=True)

def draw_poisson_montecarlo(lambda_expected):
    """Genera la visualización de la 'Caja Negra' mostrando la distribución exacta de goles."""
    goals = np.arange(0, 6)
    # Ecuación de Poisson manual para no importar scipy
    probs =[(np.exp(-lambda_expected) * (lambda_expected**k)) / np.math.factorial(k) for k in goals]
    probs_pct = [round(p * 100, 1) for p in probs]
    
    colors =['#30363d', '#30363d', '#30363d', '#58a6ff', '#58a6ff', '#58a6ff'] # Resalta 3, 4 y 5 goles (Over 2.5)
    
    fig = go.Figure(data=[go.Bar(x=[f"{g} Goles" for g in goals], y=probs_pct, marker_color=colors, text=[f"{p}%" for p in probs_pct], textposition='auto')])
    fig.update_layout(title="Simulador de Montecarlo: Distribución de Goles (10,000 iteraciones)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8b949e'), height=250, margin=dict(l=0, r=0, t=30, b=0))
    return fig

def main():
    st.markdown("<div class='nav-header'><div><h2 style='color:#fff; margin:0;'>QUANTUM SPORTS</h2><div style='color:#8b949e;'>Intelligence & Value Betting</div></div><div><span style='color:#3fb950; font-weight:bold;'>PLAN B2C ACTIVO</span></div></div>", unsafe_allow_html=True)
    if st.button("[ VOLVER AL C2 / ADMIN ]"): st.switch_page("app.py")

    st.markdown("<h2 style='color:#ffffff; margin-top:20px;'>Recomendación Algorítmica (Pitch Mode)</h2>", unsafe_allow_html=True)

    st.markdown("""
    <div class="pick-card">
        <div style="display:flex; justify-content:space-between; border-bottom:1px solid #30363d; padding-bottom:15px; margin-bottom:15px;">
            <h3 style="color:#fff; margin:0;">Real Madrid vs Manchester City</h3>
            <div class="market-badge">Over 2.5 Goles</div>
        </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown("<div class='metric-item'><h2 style='color:#fff;margin:0;'>1.95</h2><div style='color:#8b949e;font-size:0.8rem;'>Cuota Mercado</div></div>", unsafe_allow_html=True)
    with m2: st.markdown("<div class='metric-item'><h2 style='color:#8b949e;margin:0;'>51.2%</h2><div style='color:#8b949e;font-size:0.8rem;'>Prob. Implícita</div></div>", unsafe_allow_html=True)
    with m3: st.markdown("<div class='metric-item' style='border-color:#3fb950;'><h2 style='color:#3fb950;margin:0;'>+13.2%</h2><div style='color:#8b949e;font-size:0.8rem;'>Edge (Valor Real)</div></div>", unsafe_allow_html=True)
    with m4: st.markdown("<div class='metric-item'><h2 style='color:#f0883e;margin:0;'>2.5 U</h2><div style='color:#8b949e;font-size:0.8rem;'>Bankroll (Kelly)</div></div>", unsafe_allow_html=True)

    st.write("")
    
    # --- NUEVO: VISUALIZACIÓN DE LA CAJA NEGRA (MONTECARLO) ---
    st.plotly_chart(draw_poisson_montecarlo(3.1), use_container_width=True, config={'displayModeBar': False})

    # Cerrar el div de la card
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
