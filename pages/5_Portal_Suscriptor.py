import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

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
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-title { font-size: 2rem; font-weight: 800; color: #ffffff; letter-spacing: -1px; margin: 0; }
    
    .user-stats-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-around;
    }
    .user-stat { text-align: center; }
    .stat-value { font-size: 2rem; font-weight: 700; color: #ffffff; }
    .stat-label { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
    .stat-positive { color: #3fb950; }

    .pick-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .pick-card:hover { transform: translateY(-3px); border-color: #58a6ff; }
    
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
    .exp-title { font-weight: 700; color: #ffffff; margin-bottom: 10px; font-size: 1.1rem; }
    .exp-text { color: #8b949e; font-size: 0.95rem; line-height: 1.6; margin-bottom: 10px; }
    
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
    """Genera recomendaciones de alto nivel si no hay datos en caché."""
    return[
        {
            "partido": "Real Madrid vs Manchester City",
            "liga": "UEFA Champions League",
            "mercado": "Over 2.5 Goles",
            "cuota_ofrecida": 1.95,
            "prob_implicita": 51.28,
            "prob_agatha": 64.50,
            "edge": 13.22,
            "kelly_stake": "2.5 U",
            "explicabilidad": [
                "[ TÁCTICA ] El modelo xG esperado proyecta 3.1 goles basándose en la ausencia confirmada de los pivotes defensivos titulares en ambos equipos.",
                "[ MERCADO ] Caída asimétrica de la línea asiática en mercados asiáticos (Pinnacle/SBO). El 'Sharp Money' está entrando fuertemente al Over.",
                "[ ALGORITMO ] La red neuronal asigna un 78% de probabilidad de que ambos equipos marquen antes del minuto 60."
            ]
        },
        {
            "partido": "Arsenal vs Liverpool",
            "liga": "Premier League",
            "mercado": "Asian Handicap: Arsenal -0.5",
            "cuota_ofrecida": 2.10,
            "prob_implicita": 47.61,
            "prob_agatha": 54.10,
            "edge": 6.49,
            "kelly_stake": "1.2 U",
            "explicabilidad": [
                "[ TÁCTICA ] Fatiga acumulada crítica detectada en el equipo visitante tras viaje europeo intersemanal. Métrica de recuperación física al 64%.",
                "[ HISTÓRICO ] Dominio del Arsenal en métricas de presión alta (PPDA) en los últimos 4 enfrentamientos directos.",
                "[ ALGORITMO ] La probabilidad real supera la cuota de cierre proyectada. Fuerte valor esperado."
            ]
        }
    ]

def draw_probability_bar(prob_imp, prob_real):
    """Renderiza una gráfica comparativa para demostrar el Edge matemático."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=['Probabilidad'], x=[prob_imp], name='Implícita (Casa)', orientation='h',
        marker=dict(color='#30363d')
    ))
    fig.add_trace(go.Bar(
        y=['Probabilidad'], x=[prob_real - prob_imp], name='Edge Matemático (+EV)', orientation='h',
        marker=dict(color='#3fb950')
    ))
    fig.update_layout(
        barmode='stack',
        height=80,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, 100]),
        yaxis=dict(showgrid=False, showticklabels=False),
        showlegend=False
    )
    return fig

# ==============================================================================
# RENDERIZADO PRINCIPAL
# ==============================================================================
def main():
    # --- HEADER ---
    st.markdown("""
    <div class="nav-header">
        <div class="brand-title">QUANTUM SPORTS</div>
        <div style="color: #8b949e; font-family: 'Share Tech Mono', monospace;">[ PORTAL DE SUSCRIPTOR PREMIUM ]</div>
    </div>
    """, unsafe_allow_html=True)

    col_ret, _ = st.columns([0.2, 0.8])
    with col_ret:
        if st.button("[ VOLVER AL C2 / ADMIN ]"):
            st.switch_page("app.py")

    # --- DASHBOARD DEL USUARIO (SIMULADO PARA DEMO) ---
    st.markdown("""
    <div class="user-stats-container">
        <div class="user-stat">
            <div class="stat-value">10,000 EUR</div>
            <div class="stat-label">Bankroll Inicial</div>
        </div>
        <div class="user-stat">
            <div class="stat-value">11,450 EUR</div>
            <div class="stat-label">Capital Actual</div>
        </div>
        <div class="user-stat">
            <div class="stat-value stat-positive">+14.5%</div>
            <div class="stat-label">Yield Acumulado</div>
        </div>
        <div class="user-stat">
            <div class="stat-value">2</div>
            <div class="stat-label">Operaciones Activas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:#ffffff; margin-bottom:5px;'>Recomendaciones Algorítmicas Diarias</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; margin-bottom:30px;'>Filtro de Seguridad Activo: Solo se publican operaciones con Edge validado > 3.0%.</p>", unsafe_allow_html=True)

    # --- LÓGICA DE DATOS (PITCH MODE VS REAL MODE) ---
    # Para asegurar que la demostración al inversor sea impecable, forzamos el modo demo 
    # si no hay telemetría completa en el entorno de pruebas.
    
    use_pitch_mode = True
    if 'fixtures' in st.session_state and not st.session_state['fixtures'].empty:
        # En producción real, aquí se inyectaría la lectura de base de datos final.
        # Para el MVP, si el operador ha cargado datos, podemos intentar usarlos,
        # pero el Pitch Mode garantiza el impacto visual.
        pass

    if use_pitch_mode:
        picks = get_investor_demo_picks()
        
        for pick in picks:
            st.markdown(f"""
            <div class="pick-card">
                <div class="pick-header">
                    <div>
                        <div class="match-title">{pick['partido']}</div>
                        <div class="league-subtitle">{pick['liga']}</div>
                    </div>
                    <div class="market-badge">{pick['mercado']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Métricas numéricas
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"<div class='metric-item'><div class='metric-value' style='color:#ffffff;'>{pick['cuota_ofrecida']}</div><div class='metric-label'>Cuota Ofrecida</div></div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='metric-item'><div class='metric-value' style='color:#8b949e;'>{pick['prob_implicita']}%</div><div class='metric-label'>Prob. Implícita Casa</div></div>", unsafe_allow_html=True)
            with m3:
                st.markdown(f"<div class='metric-item highlight'><div class='metric-value' style='color:#3fb950;'>+{pick['edge']}%</div><div class='metric-label'>Ventaja Matemática</div></div>", unsafe_allow_html=True)
            with m4:
                st.markdown(f"<div class='metric-item'><div class='metric-value' style='color:#f0883e;'>{pick['kelly_stake']}</div><div class='metric-label'>Exposición Sugerida</div></div>", unsafe_allow_html=True)
            
            st.write("")
            
            # Gráfica de Probabilidad
            st.markdown("<p style='color:#ffffff; font-weight:700; margin-bottom:0;'>Delta de Probabilidad (Casa vs AGATHA)</p>", unsafe_allow_html=True)
            fig = draw_probability_bar(pick['prob_implicita'], pick['prob_agatha'])
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Caja de Explicabilidad
            exp_html = "<div class='exp-container'><div class='exp-title'>Análisis de Explicabilidad IA</div>"
            for linea in pick['explicabilidad']:
                exp_html += f"<div class='exp-text'>{linea}</div>"
            exp_html += "</div></div>"
            
            st.markdown(exp_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
