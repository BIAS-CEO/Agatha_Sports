import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Importación del núcleo analítico
import sports_core as sc

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA (VISIÓN SUSCRIPTOR - CAPA 5)
# ==============================================================================
st.set_page_config(page_title="Recomendaciones | Inteligencia Deportiva", layout="wide")

# Sobrescribimos el CSS táctico con un diseño limpio y corporativo para B2C
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        font-family: 'Helvetica Neue', sans-serif;
        color: #c9d1d9;
    }[data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
    
    .nav-header {
        border-bottom: 1px solid #30363d;
        padding: 20px 0px;
        margin-bottom: 30px;
    }
    .brand-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    
    .pick-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 25px;
        margin-bottom: 20px;
    }
    .pick-header {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid #21262d;
        padding-bottom: 15px;
        margin-bottom: 15px;
    }
    .match-title { font-size: 1.4rem; font-weight: bold; color: #ffffff; }
    .market-badge {
        background-color: #1f6feb;
        color: #ffffff;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    .metric-item {
        background-color: #0d1117;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
    }
    .metric-value { font-size: 1.5rem; font-weight: bold; color: #58a6ff; }
    .metric-label { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; }
    
    .explicability-box {
        background-color: #0d1117;
        border-left: 4px solid #238636;
        padding: 15px;
        color: #8b949e;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .no-picks {
        text-align: center;
        padding: 50px;
        background-color: #161b22;
        border: 1px dashed #30363d;
        border-radius: 8px;
    }
    
    div.stButton > button {
        background-color: transparent !important;
        border: 1px solid #30363d !important;
        color: #8b949e !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        border-color: #58a6ff !important;
        color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CABECERA DE USUARIO
# ==============================================================================
st.markdown("""
<div class="nav-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div class="brand-title">QUANTUM SPORTS ANALYTICS</div>
        <div style="color: #8b949e;">Área Privada de Suscriptor</div>
    </div>
</div>
""", unsafe_allow_html=True)

col_ret, _ = st.columns([0.2, 0.8])
with col_ret:
    if st.button("<< SALIR AL PANEL DE ADMINISTRACIÓN"):
        st.switch_page("app.py")

st.markdown("## Recomendaciones Estadísticas Diarias")
st.markdown("Filtro Activo (Capa 4): `Edge mínimo > 3.0%` | `Gestión Kelly Fraccional`")
st.write("")

# ==============================================================================
# CAPA 4 (GATING) & CAPA 5 (ENTREGA)
# ==============================================================================
if 'fixtures' not in st.session_state or st.session_state['fixtures'].empty:
    st.markdown("""
    <div class="no-picks">
        <h3 style="color: #8b949e;">El modelo analítico está procesando la jornada actual.</h3>
        <p>No hay recomendaciones publicadas en este momento. Las alertas se activarán cuando se detecte valor (+EV) en el mercado.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    df_f = st.session_state['fixtures']
    partidos_lista = df_f.apply(lambda row: f"{row['home_team']} vs {row['away_team']}", axis=1).tolist()
    
    c_sel, _ = st.columns([1, 1])
    with c_sel:
        partido_seleccionado = st.selectbox("Mercados analizados hoy:", partidos_lista)
    
    if st.button("Consultar Análisis del Modelo"):
        idx = partidos_lista.index(partido_seleccionado)
        row_target = df_f.iloc[idx]
        
        with st.spinner("Recuperando datos y procesando modelo de predicción..."):
            # Extracción en segundo plano (Capa 1 y 2)
            season = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
            stats_home = sc.fetch_team_statistics(row_target['home_id'], row_target['league_id'], season)
            stats_away = sc.fetch_team_statistics(row_target['away_id'], row_target['league_id'], season)
            df_odds = sc.fetch_market_odds("soccer_spain_la_liga")
            
            dossier = sc.compile_match_dossier(row_target.to_dict(), stats_home, stats_away)
            odds_dict = df_odds.to_dict('records') if not df_odds.empty else {"warning": "Sin cuotas"}
            
            # Inferencia (Capa 3)
            resultado_ia = sc.predict_match_value(dossier, odds_dict)
            
            if "error" in resultado_ia:
                st.error("Servicio temporalmente no disponible.")
            else:
                top_preds = resultado_ia.get("top_3_predicciones",[])
                
                # APLICACIÓN DE CAPA 4 (FILTRO CONSERVADOR GATING)
                picks_filtrados =[p for p in top_preds if p.get('edge_estimado_pct', 0) >= 3.0]
                
                if not picks_filtrados:
                    st.markdown("""
                    <div class="no-picks">
                        <h3 style="color: #8b949e;">PASO (NO BET)</h3>
                        <p>El modelo no ha detectado ninguna ineficiencia que supere nuestro umbral de seguridad (Edge > 3%). Protegemos el bankroll priorizando la calidad sobre el volumen.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("Se ha detectado valor matemático en este evento.")
                    
                    for pick in picks_filtrados:
                        # Cálculo de Kelly simulado para el UI del usuario (asumiendo 1 unidad = 1% bankroll)
                        bank_simulado = 1000
                        prob_impl = (1 / pick.get('cuota_objetivo', 2.0)) * 100
                        prob_real = prob_impl + pick.get('edge_estimado_pct', 0)
                        kelly = ((((pick.get('cuota_objetivo', 2.0) - 1) * (prob_real/100)) - (1 - (prob_real/100))) / (pick.get('cuota_objetivo', 2.0) - 1)) * 0.25 # Kelly fraccional 1/4
                        unidades = max(round(kelly * 100, 1), 0.5)
                        
                        st.markdown(f"""
                        <div class="pick-card">
                            <div class="pick-header">
                                <div class="match-title">{partido_seleccionado}</div>
                                <div class="market-badge">{pick.get('mercado')}</div>
                            </div>
                            
                            <div class="metrics-grid">
                                <div class="metric-item">
                                    <div class="metric-value">{pick.get('cuota_objetivo')}</div>
                                    <div class="metric-label">Cuota Objetivo</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-value" style="color: #2ea043;">+{pick.get('edge_estimado_pct')}%</div>
                                    <div class="metric-label">Valor Esperado (Edge)</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-value" style="color: #f0883e;">{unidades} U</div>
                                    <div class="metric-label">Stake Sugerido (Kelly)</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-value" style="color: #a5d6ff;">{pick.get('nivel_riesgo')}</div>
                                    <div class="metric-label">Nivel de Riesgo</div>
                                </div>
                            </div>
                            
                            <div style="font-weight: bold; margin-bottom: 10px; color: #ffffff;">Explicabilidad del Modelo:</div>
                            <div class="explicability-box">
                                {pick.get('razonamiento')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
