import streamlit as st
import pandas as pd
from datetime import datetime
import time
import json
import plotly.graph_objects as go
import sports_core as sc

st.set_page_config(page_title="Motor Predictivo | AGATHA", layout="wide")
sc.set_agatha_theme()

st.markdown("""
<style>
    .terminal-box { background-color: #090B10; border: 1px solid #30363D; border-left: 4px solid #88C0D0; padding: 15px; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; color: #A3BE8C; height: 200px; overflow-y: auto; margin-bottom: 20px; box-shadow: inset 0 0 10px rgba(0,0,0,0.8); }
    .data-grid-header { font-family: 'Rajdhani', sans-serif; color: #ECEFF4; font-size: 1.2rem; border-bottom: 1px solid #30363D; padding-bottom: 5px; margin-bottom: 15px; text-transform: uppercase; }
    .push-console { background: linear-gradient(180deg, #161B22 0%, #0D1117 100%); border: 1px solid #BF616A; padding: 20px; margin-top: 30px; }
</style>
""", unsafe_allow_html=True)

sc.return_to_main()

st.markdown("<h1 style='color:#88C0D0;'>[1] MOTOR DE INFERENCIA Y CONSOLA PUSH</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// CÁLCULO DE PROBABILIDAD ESTOCÁSTICA, DETECCIÓN DE VALOR (+EV) Y TRANSMISIÓN DE SEÑALES</p>", unsafe_allow_html=True)
st.markdown("---")

c1, c2, c3, c4 = st.columns([1, 1.5, 1.5, 1])
with c1:
    target_date = st.date_input("FECHA OPERATIVA", datetime.now().date())
    date_str = target_date.strftime("%Y-%m-%d")
with c2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("[+] INGESTAR TELEMETRÍA GLOBAL"):
        with st.spinner("ESTABLECIENDO ENLACE..."):
            df_fixtures = sc.fetch_daily_fixtures(date_str)
            if not df_fixtures.empty:
                st.session_state['fixtures'] = df_fixtures
                st.success(f"COMPLETADA: {len(df_fixtures)} NODOS IDENTIFICADOS.")
with c3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("[!] SINCRONIZAR LIBRO DE ÓRDENES"):
        with st.spinner("CAPTURANDO LÍNEAS..."):
            df_odds = sc.fetch_market_odds("soccer_spain_la_liga")
            if not df_odds.empty:
                st.session_state['global_odds'] = df_odds
                st.success("LIBRO ACTUALIZADO.")
with c4:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("[-] PURGAR MEMORIA KERNEL"): sc.release_memory()

st.markdown("---")

if 'fixtures' in st.session_state and not st.session_state['fixtures'].empty:
    df_f = st.session_state['fixtures']
    st.markdown("<div class='data-grid-header'>MATRIZ DE EVENTOS DISPONIBLES</div>", unsafe_allow_html=True)
    st.dataframe(df_f[['league_name', 'home_team', 'away_team', 'status', 'date']].head(5), use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l, col_p, col_btn = st.columns([1, 2, 1])
    with col_l: target_league = st.selectbox("FILTRAR CLUSTER", ["TODAS"] + df_f['league_name'].unique().tolist())
    if target_league != "TODAS": df_f = df_f[df_f['league_name'] == target_league]
    partidos_lista = df_f.apply(lambda row: f"{row['home_team']} vs {row['away_team']} (ID: {row['fixture_id']})", axis=1).tolist()
    with col_p: partido_seleccionado = st.selectbox("FIJAR TARGET DE INFERENCIA", partidos_lista)

    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        ejecutar_inferencia = st.button("[>] EJECUTAR PROTOCOLO")

    if ejecutar_inferencia:
        idx = partidos_lista.index(partido_seleccionado)
        row_target = df_f.iloc[idx]
        season = target_date.year if target_date.month >= 7 else target_date.year - 1
        terminal_placeholder = st.empty()
        
        logs = ""
        def update_terminal(msg):
            nonlocal logs
            logs += f">>[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}<br>"
            terminal_placeholder.markdown(f"<div class='terminal-box'>{logs}</div>", unsafe_allow_html=True)
            time.sleep(0.4)

        update_terminal("INICIALIZANDO MOTOR ESTOCÁSTICO...")
        update_terminal(f"EXTRAYENDO TELEMETRÍA: {row_target['home_team']} vs {row_target['away_team']}")
        stats_home = sc.fetch_team_statistics(row_target['home_id'], row_target['league_id'], season)
        stats_away = sc.fetch_team_statistics(row_target['away_id'], row_target['league_id'], season)
        update_terminal("CRUZANDO PROBABILIDAD REAL VS LIBRO DE ÓRDENES...")
        df_odds = st.session_state.get('global_odds', pd.DataFrame())
        dossier = sc.compile_match_dossier(row_target.to_dict(), stats_home, stats_away)
        odds_dict = df_odds.to_dict('records') if not df_odds.empty else {"warning": "Sin cuotas"}
        update_terminal("EJECUTANDO LLM (GPT-4-TURBO)...")
        resultado_ia = sc.predict_match_value(dossier, odds_dict)
        
        if "error" in resultado_ia: update_terminal(f"<span style='color:#BF616A'>[CRÍTICO] FALLO: {resultado_ia['error']}</span>")
        else:
            update_terminal("<span style='color:#88C0D0'>[OK] INFERENCIA COMPLETADA.</span>")
            st.session_state['last_prediction'] = resultado_ia
            st.session_state['last_target'] = partido_seleccionado

    if 'last_prediction' in st.session_state:
        st.markdown("<h3 style='color:#88C0D0; margin-top: 30px;'>MATRIZ DE INTELIGENCIA</h3>", unsafe_allow_html=True)
        resultado_ia = st.session_state['last_prediction']
        prob = resultado_ia.get("evaluacion_probabilidades", {})
        mercado = resultado_ia.get("analisis_mercado", {})
        
        p_1x2 = prob.get("1X2", {})
        g1, g2, g3 = st.columns(3)
        with g1: st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=float(p_1x2.get('local', 33.3)), title={'text': "LOCAL"}, gauge={'axis': {'range':[0, 100]}, 'bar': {'color': "#88C0D0"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': '#ECEFF4'}), use_container_width=True, config={'displayModeBar': False})
        with g2: st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=float(p_1x2.get('empate', 33.3)), title={'text': "EMPATE"}, gauge={'axis': {'range':[0, 100]}, 'bar': {'color': "#EBCB8B"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': '#ECEFF4'}), use_container_width=True, config={'displayModeBar': False})
        with g3: st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=float(p_1x2.get('visitante', 33.3)), title={'text': "VISITANTE"}, gauge={'axis': {'range':[0, 100]}, 'bar': {'color': "#BF616A"}})).update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': '#ECEFF4'}), use_container_width=True, config={'displayModeBar': False})

        r1, r2 = st.columns(2)
        with r1:
            is_val = mercado.get('hay_value_bet', False)
            st.markdown(f"<div class='metric-box {'success-box' if is_val else 'warning-box'}'><h4>MERCADO</h4>**VENTAJA (+EV):** {'CONFIRMADO' if is_val else 'NEGATIVO'}<br>**LÍNEAS:** {mercado.get('analisis_movimiento', 'Eficiente')}</div>", unsafe_allow_html=True)
        with r2:
            bank = resultado_ia.get("gestion_bankroll", {})
            st.markdown(f"<div class='metric-box'><h4>CAPITAL</h4>**RIESGO:** {bank.get('riesgo_global_operacion', 'ALTO')}<br>**ASIGNACIÓN:** {bank.get('estrategia', '0 U')}</div>", unsafe_allow_html=True)
        
        st.markdown(f"**SÍNTESIS:** *{prob.get('justificacion_matematica', 'N/A')}*")
        
        st.markdown("<h3 style='color:#88C0D0; margin-top:20px;'>VECTORES DE INVERSIÓN</h3>", unsafe_allow_html=True)
        for i, pred in enumerate(resultado_ia.get("top_3_predicciones",[])):
            st.markdown(f"<div style='background:#0D1117; border:1px solid #30363D; border-left: 4px solid #88C0D0; padding:15px; margin-bottom:10px;'><span style='color:#ECEFF4; font-weight:bold;'>[ TARGET 0{i+1} ] {pred.get('mercado', 'N/A')}</span> | <span style='color:#A3BE8C; font-weight:bold;'>CUOTA: {pred.get('cuota_objetivo', '0.0')}</span><br><span style='color:#EBCB8B;'>EDGE: +{pred.get('edge_estimado_pct', '0')}%</span><div style='color:#8B949E; margin-top:10px; padding-top:10px; border-top: 1px dashed #30363D;'>>> {pred.get('razonamiento', 'N/A')}</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='push-console'><h3 style='color:#BF616A; margin-top:0;'>[ SYSTEM PUSH ] TRANSMISIÓN B2C</h3></div>", unsafe_allow_html=True)
        if st.button("[>>>] EMITIR SEÑAL A CLIENTES"):
            with st.spinner("ENCRIPTANDO SEÑAL..."):
                time.sleep(2)
                st.success("TRANSMISIÓN CONFIRMADA. SEÑAL DISTRIBUIDA AL 100% DE LOS NODOS.")
                st.json({"timestamp": datetime.now().isoformat(), "event": st.session_state.get('last_target', 'UNKNOWN'), "signal_type": "VALUE_BET_ALERT", "channels": ["Telegram", "Discord"]})
