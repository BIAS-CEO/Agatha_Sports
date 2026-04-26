import streamlit as st
import pandas as pd
from datetime import datetime
import json
import sports_core as sc

st.set_page_config(page_title="Motor Predictivo | AGATHA", layout="wide")
sc.set_agatha_theme()
sc.return_to_main()

st.markdown("<h1 style='color:#88C0D0;'>[1] MOTOR DE INFERENCIA PREDICTIVA</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// CÁLCULO DE PROBABILIDAD REAL Y DETECCIÓN DE VALOR (+EV)</p>", unsafe_allow_html=True)
st.markdown("---")

c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    target_date = st.date_input("FECHA OPERATIVA", datetime.now().date())
    date_str = target_date.strftime("%Y-%m-%d")

with c2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("EXTRAER TELEMETRÍA DE PARTIDOS"):
        with st.spinner("Conectando con cluster API-Football..."):
            df_fixtures = sc.fetch_daily_fixtures(date_str)
            if not df_fixtures.empty:
                st.session_state['fixtures'] = df_fixtures
                st.success(f"Operación completada. {len(df_fixtures)} nodos identificados.")
            else:
                st.warning("No se ha recuperado telemetría.")

with c3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("LIBERAR MEMORIA KERNEL"):
        sc.release_memory()
        st.info("Memoria RAM purgada.")

st.markdown("---")

if 'fixtures' in st.session_state and not st.session_state['fixtures'].empty:
    df_f = st.session_state['fixtures']
    col_l, col_p = st.columns(2)
    with col_l: target_league = st.selectbox("FILTRAR POR COMPETICIÓN", ["TODAS"] + df_f['league_name'].unique().tolist())
    if target_league != "TODAS": df_f = df_f[df_f['league_name'] == target_league]
    partidos_lista = df_f.apply(lambda row: f"{row['home_team']} vs {row['away_team']} (ID: {row['fixture_id']})", axis=1).tolist()
    with col_p: partido_seleccionado = st.selectbox("SELECCIONAR NODO (PARTIDO)", partidos_lista)

    if st.button("EJECUTAR ANÁLISIS MATEMÁTICO"):
        idx = partidos_lista.index(partido_seleccionado)
        row_target = df_f.iloc[idx]
        season = target_date.year if target_date.month >= 7 else target_date.year - 1

        with st.spinner("Procesando inferencia LLM..."):
            stats_home = sc.fetch_team_statistics(row_target['home_id'], row_target['league_id'], season)
            stats_away = sc.fetch_team_statistics(row_target['away_id'], row_target['league_id'], season)
            df_odds = sc.fetch_market_odds("soccer_spain_la_liga")
            dossier = sc.compile_match_dossier(row_target.to_dict(), stats_home, stats_away)
            odds_dict = df_odds.to_dict('records') if not df_odds.empty else {"warning": "Sin cuotas"}
            resultado_ia = sc.predict_match_value(dossier, odds_dict)
            
            if "error" in resultado_ia:
                st.error(f"Fallo predictivo: {resultado_ia['error']}")
            else:
                st.markdown("<h3 style='color:#88C0D0;'>REPORTE DE INTELIGENCIA</h3>", unsafe_allow_html=True)
                prob = resultado_ia.get("evaluacion_probabilidades", {})
                mercado = resultado_ia.get("analisis_mercado", {})
                r1, r2, r3 = st.columns(3)
                with r1:
                    st.markdown("<div class='metric-box'><h4>PROBABILIDAD 1X2</h4>", unsafe_allow_html=True)
                    st.write(f"**LOCAL:** {prob.get('1X2', {}).get('local', 0)}% | **EMPATE:** {prob.get('1X2', {}).get('empate', 0)}% | **VISITANTE:** {prob.get('1X2', {}).get('visitante', 0)}%")
                    st.markdown("</div>", unsafe_allow_html=True)
                with r2:
                    is_val = mercado.get('hay_value_bet', False)
                    st.markdown(f"<div class='metric-box {'success-box' if is_val else 'warning-box'}'><h4>MERCADO</h4>", unsafe_allow_html=True)
                    st.write(f"**VALUE:** {'SI' if is_val else 'NO'} | **MOV:** {mercado.get('analisis_movimiento', '')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with r3:
                    bank = resultado_ia.get("gestion_bankroll", {})
                    risk = bank.get("riesgo_global_operacion", "ALTO")
                    st.markdown(f"<div class='metric-box {'critical-box' if risk=='ALTO' else 'warning-box' if risk=='MEDIO' else 'success-box'}'><h4>DIRECTIVA</h4>", unsafe_allow_html=True)
                    st.write(f"**RIESGO:** {risk} | **ESTRATEGIA:** {bank.get('estrategia', '')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown(f"**JUSTIFICACIÓN:** *{prob.get('justificacion_matematica', '')}*")
                for i, pred in enumerate(resultado_ia.get("top_3_predicciones",[])):
                    st.markdown(f"<div style='background:#0D1117; border:1px solid #30363D; padding:10px; margin-bottom:5px;'><span style='color:#88C0D0;'>[{i+1}] {pred.get('mercado')}</span> | <span style='color:#A3BE8C;'>CUOTA: {pred.get('cuota_objetivo')}</span> | <span style='color:#EBCB8B;'>EDGE: {pred.get('edge_estimado_pct')}%</span><br><span style='color:#8B949E; font-size:0.9rem;'>{pred.get('razonamiento')}</span></div>", unsafe_allow_html=True)
            sc.release_memory()
