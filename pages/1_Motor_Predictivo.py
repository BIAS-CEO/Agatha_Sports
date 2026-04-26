import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Importación del núcleo analítico
import sports_core as sc

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y CSS TÁCTICO
# ==============================================================================
st.set_page_config(page_title="Motor Predictivo | AGATHA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #050505; font-family: 'Share Tech Mono', monospace; color: #ECEFF4; }
    h1, h2, h3 { font-family: 'Rajdhani', sans-serif; color: #88C0D0; text-transform: uppercase; }
    .metric-box {
        border-left: 4px solid #88C0D0;
        background-color: #161B22;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .warning-box { border-left-color: #EBCB8B; }
    .critical-box { border-left-color: #BF616A; }
    .success-box { border-left-color: #A3BE8C; }
    div.stButton > button {
        border: 1px solid #88C0D0 !important;
        background-color: rgba(136,192,208,0.1) !important;
        color: #88C0D0 !important;
        border-radius: 0px !important;
        width: 100%;
        text-transform: uppercase;
    }
    div.stButton > button:hover { background-color: rgba(136,192,208,0.3) !important; box-shadow: 0 0 10px #88C0D0; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CABECERA DE SISTEMA
# ==============================================================================
st.markdown("<h1>[1] MOTOR DE INFERENCIA PREDICTIVA</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// CÁLCULO DE PROBABILIDAD REAL, DETECCIÓN DE VALOR ESPERADO (+EV) Y RIESGO ESTOCÁSTICO</p>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# PANEL DE CONTROL OPERATIVO
# ==============================================================================
c1, c2, c3 = st.columns([1, 2, 1])

with c1:
    target_date = st.date_input("FECHA OPERATIVA", datetime.now().date())
    date_str = target_date.strftime("%Y-%m-%d")

with c2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("EXTRAER TELEMETRÍA DE PARTIDOS (API-FOOTBALL)"):
        with st.spinner("Conectando con cluster API-Football..."):
            df_fixtures = sc.fetch_daily_fixtures(date_str)
            if not df_fixtures.empty:
                st.session_state['fixtures'] = df_fixtures
                st.success(f"Operación completada. {len(df_fixtures)} nodos tácticos identificados.")
            else:
                st.warning("No se ha recuperado telemetría para esta fecha.")

with c3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("LIBERAR MEMORIA KERNEL"):
        sc.release_memory()
        st.info("Memoria RAM purgada. Prevención OOM ejecutada.")

st.markdown("---")

# ==============================================================================
# FLUJO DE ANÁLISIS
# ==============================================================================
if 'fixtures' in st.session_state and not st.session_state['fixtures'].empty:
    df_f = st.session_state['fixtures']
    
    # Filtrar competiciones principales para evitar saturación
    ligas_disponibles = df_f['league_name'].unique().tolist()
    
    col_l, col_p = st.columns(2)
    with col_l:
        target_league = st.selectbox("FILTRAR POR LIGA", ["TODAS"] + ligas_disponibles)
    
    if target_league != "TODAS":
        df_f = df_f[df_f['league_name'] == target_league]
        
    partidos_lista = df_f.apply(lambda row: f"{row['home_team']} vs {row['away_team']} (ID: {row['fixture_id']})", axis=1).tolist()
    
    with col_p:
        partido_seleccionado = st.selectbox("SELECCIONAR NODO (PARTIDO)", partidos_lista)

    if st.button("EJECUTAR ANÁLISIS DE VECTOR MATEMÁTICO (DOV)"):
        # Extracción de IDs críticos
        idx = partidos_lista.index(partido_seleccionado)
        row_target = df_f.iloc[idx]
        
        fixture_id = row_target['fixture_id']
        league_id = row_target['league_id']
        home_id = row_target['home_id']
        away_id = row_target['away_id']
        
        # Cálculo de temporada (Europa)
        current_year = target_date.year
        season = current_year if target_date.month >= 7 else current_year - 1

        with st.spinner("Ingestando telemetría histórica, cuotas de mercado y procesando inferencia LLM. Protocolo Billy Walters activado..."):
            # 1. Extracción de estadísticas
            stats_home = sc.fetch_team_statistics(home_id, league_id, season)
            stats_away = sc.fetch_team_statistics(away_id, league_id, season)
            
            # 2. Extracción de cuotas del mercado
            df_odds = sc.fetch_market_odds("soccer_spain_la_liga") # Nota: Ajustar sport_key dinámicamente si es necesario en el futuro
            
            # 3. Compilación de dossier
            dossier = sc.compile_match_dossier(row_target.to_dict(), stats_home, stats_away)
            
            # 4. Inferencia predictiva
            odds_dict = df_odds.to_dict('records') if not df_odds.empty else {"warning": "No hay cuotas disponibles en The Odds API para esta liga/partido en este momento."}
            resultado_ia = sc.predict_match_value(dossier, odds_dict)
            
            if "error" in resultado_ia:
                st.error(f"Fallo en el núcleo predictivo: {resultado_ia['error']}")
            else:
                # ==============================================================================
                # RENDERIZADO DEL INFORME TÁCTICO
                # ==============================================================================
                st.markdown("### REPORTE DE INTELIGENCIA MATEMÁTICA")
                
                # Bloque 1: Probabilidades y Mercado
                prob = resultado_ia.get("evaluacion_probabilidades", {})
                mercado = resultado_ia.get("analisis_mercado", {})
                
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
                    st.markdown("#### PROBABILIDAD REAL 1X2")
                    p_1x2 = prob.get("1X2", {})
                    st.write(f"**LOCAL:** {p_1x2.get('local', 0)}%")
                    st.write(f"**EMPATE:** {p_1x2.get('empate', 0)}%")
                    st.write(f"**VISITANTE:** {p_1x2.get('visitante', 0)}%")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with r2:
                    is_value = mercado.get('hay_value_bet', False)
                    box_class = 'metric-box success-box' if is_value else 'metric-box warning-box'
                    st.markdown(f"<div class='{box_class}'>", unsafe_allow_html=True)
                    st.markdown("#### ESTADO DEL MERCADO")
                    st.write(f"**VALUE BET DETECTADO:** {'AFIRMATIVO' if is_value else 'NEGATIVO'}")
                    st.write(f"**ANÁLISIS DE LÍNEAS:** {mercado.get('analisis_movimiento', 'N/A')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with r3:
                    bankroll = resultado_ia.get("gestion_bankroll", {})
                    risk = bankroll.get("riesgo_global_operacion", "ALTO")
                    risk_class = 'metric-box critical-box' if risk == 'ALTO' else 'metric-box warning-box' if risk == 'MEDIO' else 'metric-box success-box'
                    st.markdown(f"<div class='{risk_class}'>", unsafe_allow_html=True)
                    st.markdown("#### DIRECTIVA DE RIESGO")
                    st.write(f"**NIVEL DE RIESGO:** {risk}")
                    st.write(f"**ESTRATEGIA:** {bankroll.get('estrategia', 'N/A')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown(f"**JUSTIFICACIÓN MATEMÁTICA:** *{prob.get('justificacion_matematica', 'N/A')}*")
                
                # Bloque 2: Top Predicciones
                st.markdown("### TARGETS DE INVERSIÓN (TOP 3)")
                top_preds = resultado_ia.get("top_3_predicciones",[])
                
                if top_preds:
                    for i, pred in enumerate(top_preds):
                        st.markdown(f"""
                        <div style="background-color:#0D1117; border: 1px solid #30363D; padding: 10px; margin-bottom: 5px;">
                            <span style="color:#88C0D0; font-weight:bold;">[ {i+1} ] MERCADO:</span> {pred.get('mercado')} | 
                            <span style="color:#A3BE8C;">CUOTA: {pred.get('cuota_objetivo')}</span> | 
                            <span style="color:#EBCB8B;">EDGE (+EV): {pred.get('edge_estimado_pct')}%</span><br>
                            <span style="color:#8B949E; font-size: 0.9rem;">>> TÁCTICA: {pred.get('razonamiento')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Sin objetivos de inversión viables para este nodo.")
                
                # Bloque 3: Datos Crudos (Para auditoría)
                with st.expander("VER DOSSIER DE INTELIGENCIA RAW (JSON)"):
                    st.json(resultado_ia)
                    
            sc.release_memory()

else:
    st.info("Sistema a la espera de inyección de telemetría. Seleccione una fecha y proceda a la extracción.")
