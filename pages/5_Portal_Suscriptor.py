import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA (VISIÓN SUSCRIPTOR - CAPA 5)
# ==============================================================================
st.set_page_config(page_title="Quantum Sports | Área Privada", layout="wide")

# CSS CORPORATIVO B2C (SaaS Premium)
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
        color: #c9d1d9;
    }
    [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
    
    .nav-header {
        background: linear-gradient(180deg, #161b22 0%, #0b0f19 100%);
        border-bottom: 1px solid #30363d;
        padding: 20px 40px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-title { font-size: 2.2rem; font-weight: 800; color: #ffffff; letter-spacing: -1px; margin: 0; }
    .plan-badge { background-color: rgba(63, 185, 80, 0.1); color: #3fb950; border: 1px solid #3fb950; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; letter-spacing: 1px; }
    
    .user-stats-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-around;
    }
    .user-stat { text-align: center; border-right: 1px solid #30363d; padding-right: 40px; flex: 1; }
    .user-stat:last-child { border-right: none; padding-right: 0; }
    .stat-value { font-size: 2rem; font-weight: 700; color: #ffffff; }
    .stat-label { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    .stat-positive { color: #3fb950; }
    .stat-negative { color: #f85149; }

    .trust-banner {
        background-color: rgba(88, 166, 255, 0.05);
        border: 1px solid #1f6feb;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 30px;
        font-size: 0.9rem;
        color: #8b949e;
    }

    .pick-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    .pick-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #21262d;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    .match-title { font-size: 1.5rem; font-weight: 700; color: #ffffff; }
    .league-subtitle { font-size: 0.9rem; color: #8b949e; }
    .volume-indicator { font-size: 0.8rem; color: #f0883e; font-weight: bold; margin-top: 5px; }
    
    .market-badge {
        background-color: rgba(88, 166, 255, 0.1);
        color: #58a6ff;
        border: 1px solid #58a6ff;
        padding: 6px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    .metric-item {
        background-color: #0b0f19;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-item.highlight { border-color: #3fb950; background-color: rgba(63, 185, 80, 0.05); }
    
    .exp-container {
        background-color: #0b0f19;
        border-left: 4px solid #58a6ff;
        padding: 20px;
        border-radius: 0 8px 8px 0;
        margin-top: 15px;
    }
    .weight-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.9rem; color: #c9d1d9; }
    .weight-bar-bg { width: 100%; background-color: #21262d; border-radius: 4px; height: 6px; margin-bottom: 15px; }
    .weight-bar-fill { background-color: #58a6ff; height: 6px; border-radius: 4px; }
    
    div.stButton > button {
        background-color: transparent !important;
        border: 1px solid #30363d !important;
        color: #8b949e !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover { border-color: #58a6ff !important; color: #58a6ff !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATOS SINTÉTICOS PARA DEMOSTRACIÓN A INVERSORES (PITCH MODE)
# ==============================================================================
def get_investor_demo_picks():
    """Genera recomendaciones estructuradas según la directiva de valor diferencial."""
    return[
        {
            "id": "1/3",
            "partido": "Real Sociedad vs Athletic Club",
            "liga": "LaLiga (España)",
            "mercado": "Under 2.25 Goles",
            "cuota_ofrecida": 1.92,
            "prob_implicita": 52.08,
            "prob_agatha": 58.50,
            "edge": 6.42,
            "kelly_stake": "1.5 U",
            "explicabilidad_pesos":[
                {"factor": "Métrica xG Ajustada (Defensiva)", "peso": 45, "desc": "Ambos equipos permiten <0.8 xG por partido en sus últimos 6 encuentros."},
                {"factor": "Histórico H2H de Posesión", "peso": 35, "desc": "Patrón de anulación mutua en el mediocampo detectado en derbis recientes."},
                {"factor": "Movimiento de Línea (Sharp Money)", "peso": 20, "desc": "Caída del Over detectada en mercado asiático. Público apostando al Over, dinero profesional al Under."}
            ]
        },
        {
            "id": "2/3",
            "partido": "Bayer Leverkusen vs RB Leipzig",
            "liga": "Bundesliga (Alemania)",
            "mercado": "Ambos Marcan - SÍ",
            "cuota_ofrecida": 1.75,
            "prob_implicita": 57.14,
            "prob_agatha": 61.34,
            "edge": 4.20,
            "kelly_stake": "1.0 U",
            "explicabilidad_pesos":[
                {"factor": "Ausencia de Central Titular", "peso": 50, "desc": "Baja confirmada del ancla defensiva local, incrementando la probabilidad de transición rápida rival."},
                {"factor": "Forma Ofensiva (Últimos 6 partidos)", "peso": 30, "desc": "Ambos equipos promedian >2.1 goles generados. Eficiencia de finalización en el percentil 90."},
                {"factor": "Modelo de Poisson", "peso": 20, "desc": "Simulación de 10,000 escenarios arroja un 61% de probabilidad de marcador 1-1 o superior."}
            ]
        }
    ]

def draw_track_record_chart():
    """Renderiza el gráfico de 'Transparencia Radical' exigido por el modelo de negocio."""
    np.random.seed(42)
    fechas = pd.date_range(start=datetime.now() - timedelta(days=90), periods=90)
    # Simulación de crecimiento estable y conservador (Yield ~4-5%)
    crecimiento = np.random.normal(loc=0.15, scale=0.8, size=90)
    capital = 10000 + np.cumsum(crecimiento * 100)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fechas, y=capital, fill='tozeroy', mode='lines',
        line=dict(color='#58a6ff', width=2),
        fillcolor='rgba(88, 166, 255, 0.1)',
        name='Bankroll'
    ))
    fig.update_layout(
        height=200, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color='#8b949e'),
        yaxis=dict(showgrid=True, gridcolor='#30363d', color='#8b949e'),
        hovermode="x unified"
    )
    return fig

# ==============================================================================
# RENDERIZADO PRINCIPAL
# ==============================================================================
def main():
    st.markdown("""
    <div class="nav-header">
        <div>
            <div class="brand-title">QUANTUM SPORTS</div>
            <div style="color: #8b949e; font-size: 0.9rem;">Intelligence & Value Betting</div>
        </div>
        <div style="text-align: right;">
            <div class="plan-badge">PLAN MULTIDEPORTE - ACTIVO</div>
            <div style="color: #8b949e; font-size: 0.8rem; margin-top: 5px;">Usuario: INVERSOR_01</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_ret, _ = st.columns([0.2, 0.8])
    with col_ret:
        if st.button("[ VOLVER AL C2 / ADMIN ]"):
            st.switch_page("app.py")

    # --- DASHBOARD: TRANSPARENCIA RADICAL Y GESTIÓN DE BANKROLL ---
    st.markdown("""
    <div class="trust-banner">
        <strong>✓ TRANSPARENCIA RADICAL:</strong> Todas nuestras operaciones están auditadas por terceros independientes (Blogabet/Pyckio). Nuestro modelo no percibe ingresos por afiliación de casas de apuestas. Su rentabilidad es nuestro único modelo de negocio.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="user-stats-container">
        <div class="user-stat">
            <div class="stat-value">11,450 EUR</div>
            <div class="stat-label">Capital (Bankroll)</div>
        </div>
        <div class="user-stat">
            <div class="stat-value stat-positive">+4.2%</div>
            <div class="stat-label">Yield Histórico Auditable</div>
        </div>
        <div class="user-stat">
            <div class="stat-value stat-positive">+14.5%</div>
            <div class="stat-label">ROI Acumulado</div>
        </div>
        <div class="user-stat">
            <div class="stat-value stat-negative">-2.1%</div>
            <div class="stat-label">Max Drawdown</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Gráfico de Histórico
    with st.expander("VER HISTÓRICO DE RENDIMIENTO (ÚLTIMOS 90 DÍAS)", expanded=False):
        st.plotly_chart(draw_track_record_chart(), use_container_width=True, config={'displayModeBar': False})

    st.markdown("<h2 style='color:#ffffff; margin-bottom:5px; margin-top:20px;'>Recomendaciones Algorítmicas de Hoy</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; margin-bottom:30px;'><strong>Filtro Conservador:</strong> Volumen selectivo. Exigencia de Edge > 3.0%. Gestión de riesgo integrada (Kelly Fraccional).</p>", unsafe_allow_html=True)

    # --- RENDERIZADO DE PICKS (PITCH MODE) ---
    picks = get_investor_demo_picks()
    
    for pick in picks:
        st.markdown(f"""
        <div class="pick-card">
            <div class="pick-header">
                <div>
                    <div class="match-title">{pick['partido']}</div>
                    <div class="league-subtitle">{pick['liga']}</div>
                    <div class="volume-indicator">PICK {pick['id']} (Tope Diario Estricto)</div>
                </div>
                <div class="market-badge">{pick['mercado']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"<div class='metric-item'><div class='metric-value' style='color:#ffffff;'>{pick['cuota_ofrecida']}</div><div class='metric-label'>Cuota Mercado</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-item'><div class='metric-value' style='color:#8b949e;'>{pick['prob_implicita']}%</div><div class='metric-label'>Prob. Implícita</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-item highlight'><div class='metric-value' style='color:#3fb950;'>+{pick['edge']}%</div><div class='metric-label'>Edge (Valor Real)</div></div>", unsafe_allow_html=True)
        with m4: st.markdown(f"<div class='metric-item'><div class='metric-value' style='color:#f0883e;'>{pick['kelly_stake']}</div><div class='metric-label'>Bankroll (Kelly)</div></div>", unsafe_allow_html=True)
        
        st.write("")
        
        # --- EXPLICABILIDAD PONDERADA ---
        st.markdown("<div style='font-weight: 700; margin-bottom: 10px; color: #ffffff;'>Explicabilidad del Modelo (Factores Ponderados):</div>", unsafe_allow_html=True)
        
        exp_html = "<div class='exp-container'>"
        for peso in pick['explicabilidad_pesos']:
            # Renderizado de barras de peso
            exp_html += f"""
            <div class='weight-row'>
                <span>{peso['factor']}</span>
                <span style='color:#58a6ff; font-weight:bold;'>{peso['peso']}%</span>
            </div>
            <div class='weight-bar-bg'><div class='weight-bar-fill' style='width: {peso['peso']}%;'></div></div>
            <div class='exp-text'>- {peso['desc']}</div>
            <div style='margin-bottom:15px;'></div>
            """
        exp_html += "</div></div>"
        
        st.markdown(exp_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
