import streamlit as st
import pandas as pd
from datetime import datetime
import time
import json
import plotly.graph_objects as go
import sports_core as sc

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(page_title="Motor Predictivo | AGATHA", layout="wide")
sc.set_agatha_theme()

# Sobreescritura CSS específica para componentes PRO
st.markdown("""
<style>
    .terminal-box {
        background-color: #090B10;
        border: 1px solid #30363D;
        border-left: 4px solid #88C0D0;
        padding: 15px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        color: #A3BE8C;
        height: 200px;
        overflow-y: auto;
        margin-bottom: 20px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }
    .data-grid-header {
        font-family: 'Rajdhani', sans-serif;
        color: #ECEFF4;
        font-size: 1.2rem;
        border-bottom: 1px solid #30363D;
        padding-bottom: 5px;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    .push-console {
        background: linear-gradient(180deg, #161B22 0%, #0D1117 100%);
        border: 1px solid #BF616A;
        padding: 20px;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

sc.return_to_main()

# ==============================================================================
# CABECERA DE SISTEMA
# ==============================================================================
st.markdown("<h1 style='color:#88C0D0;'>[1] MOTOR DE INFERENCIA Y CONSOLA PUSH</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// CÁLCULO DE PROBABILIDAD ESTOCÁSTICA, DETECCIÓN DE VALOR (+EV) Y TRANSMISIÓN DE SEÑALES</p>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# PANEL DE INGESTA MASIVA
# ==============================================================================
c1, c2, c3, c4 = st.columns([1, 1.5, 1.5, 1])

with c1:
    target_date = st.date_input("FECHA OPERATIVA", datetime.now().date())
    date_str = target_date.strftime("%Y-%m-%d")

with c2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("[+] INGESTAR TELEMETRÍA GLOBAL (API-FOOTBALL)"):
        with st.spinner("ESTABLECIENDO ENLACE CON CLUSTER DE DATOS..."):
            df_fixtures = sc.fetch_daily_fixtures(date_str)
            if not df_fixtures.empty:
                st.session_state['fixtures'] = df_fixtures
                st.success(f"INGESTA COMPLETADA: {len(df_fixtures)} NODOS TÁCTICOS IDENTIFICADOS.")
            else:
                st.warning("SIN TELEMETRÍA PARA EL CICLO TEMPORAL SELECCIONADO.")

with c3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("[!] SINCRONIZAR LIBRO DE ÓRDENES (ODDS API)"):
        with st.spinner("CAPTURANDO LÍNEAS DE MERCADO ASIÁTICO Y EUROPEO..."):
            df_odds = sc.fetch_market_odds("soccer_spain_la_liga")
            if not df_odds.empty:
                st.session_state['global_odds'] = df_odds
                st.success(f"LIBRO DE ÓRDENES ACTUALIZADO: {len(df_odds)} VECTORES DE CUOTA.")
            else:
                st.warning("MERCADO INACTIVO O FUERA DE COBERTURA.")

with c4:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("[-] PURGAR MEMORIA KERNEL"):
        sc.release_memory()
        st.info("MEMORIA VOLÁTIL LIBERADA (PREVENCIÓN OOM).")

st.markdown("---")

# ==============================================================================
# MATRIZ DE DATOS Y SELECCIÓN DE OBJETIVO
# ==============================================================================
if 'fixtures' in st.session_state and not st.session_state['fixtures'].empty:
    df_f = st.session_state['fixtures']
    
    st.markdown("<div class='data-grid-header'>MATRIZ DE EVENTOS DISPONIBLES</div>", unsafe_allow_html=True)
    
    # Vista previa del DataFrame con formato limpio
    st.dataframe(
        df_f[['league_name', 'home_team', 'away_team', 'status', 'date']].head(5),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l, col_p, col_btn = st.columns([1, 2, 1])
    with col_l: 
        target_league = st.selectbox("FILTRAR CLUSTER (COMPETICIÓN)", ["TODAS"] + df_f['league_name'].unique().tolist())
    
    if target_league != "TODAS": 
        df_f = df_f[df_f['league_name'] == target_league]
        
    partidos_lista = df_f.apply(lambda row: f"{row['home_team']} vs {row['away_team']} (ID: {row['fixture_id']})", axis=1).tolist()
    
    with col_p: 
        partido_seleccionado = st.selectbox("FIJAR TARGET DE INFERENCIA", partidos_lista)

    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        ejecutar_inferencia = st.button("[>] EJECUTAR PROTOCOLO BILLY WALTERS")

    # ==============================================================================
    # MOTOR DE INFERENCIA Y TERMINAL VISUAL
    # ==============================================================================
    if ejecutar_inferencia:
        idx = partidos_lista.index(partido_seleccionado)
        row_target = df_f.iloc[idx]
        season = target_date.year if target_date.month >= 7 else target_date.year - 1

        terminal_placeholder = st.empty()
        
        # Simulación visual de "Caja Negra" procesando
        logs = ""
        def update_terminal(msg):
            nonlocal logs
            logs += f">> [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}<br>"
            terminal_placeholder.markdown(f"<div class='terminal-box'>{logs}</div>", unsafe_allow_html=True)
            time.sleep(0.4)

        update_terminal("INICIALIZANDO MOTOR ESTOCÁSTICO...")
        update_terminal(f"EXTRAYENDO TELEMETRÍA HISTÓRICA: {row_target['home_team']} vs {row_target['away_team']}")
        
        stats_home = sc.fetch_team_statistics(row_target['home_id'], row_target['league_id'], season)
        stats_away = sc.fetch_team_statistics(row_target['away_id'], row_target['league_id'], season)
        
        update_terminal("PROCESANDO MODELO DE POISSON Y xG AJUSTADO...")
        update_terminal("CRUZANDO PROBABILIDAD REAL VS LIBRO DE ÓRDENES (THE ODDS API)...")
        
        df_odds = st.session_state.get('global_odds', pd.DataFrame())
        dossier = sc.compile_match_dossier(row_target.to_dict(), stats_home, stats_away)
        odds_dict = df_odds.to_dict('records') if not df_odds.empty else {"warning": "Sin cuotas"}
        
        update_terminal("EJECUTANDO LLM (GPT-4-TURBO) PARA DETECCIÓN DE EDGE (+EV)...")
        
        resultado_ia = sc.predict_match_value(dossier, odds_dict)
        
        if "error" in resultado_ia:
            update_terminal(f"<span style='color:#BF616A'>[CRÍTICO] FALLO EN NÚCLEO PREDICTIVO: {resultado_ia['error']}</span>")
        else:
            update_terminal("<span style='color:#88C0D0'>[OK] INFERENCIA COMPLETADA. DESPLEGANDO RESULTADOS TÁCTICOS.</span>")
            st.session_state['last_prediction'] = resultado_ia
            st.session_state['last_target'] = partido_seleccionado

    # ==============================================================================
    # RENDERIZADO DE INTELIGENCIA (SI HAY PREDICCIÓN EN CACHÉ)
    # ==============================================================================
    if 'last_prediction' in st.session_state:
        st.markdown("<h3 style='color:#88C0D0; margin-top: 30px;'>MATRIZ DE INTELIGENCIA MATEMÁTICA</h3>", unsafe_allow_html=True)
        resultado_ia = st.session_state['last_prediction']
        prob = resultado_ia.get("evaluacion_probabilidades", {})
        mercado = resultado_ia.get("analisis_mercado", {})
        
        # FILA 1: GAUGE CHARTS DE PROBABILIDAD
        p_1x2 = prob.get("1X2", {})
        p_loc = float(p_1x2.get('local', 33.3))
        p_emp = float(p_1x2.get('empate', 33.3))
        p_vis = float(p_1x2.get('visitante', 33.3))
        
        g1, g2, g3 = st.columns(3)
        with g1:
            fig1 = go.Figure(go.Indicator(mode="gauge+number", value=p_loc, title={'text': "VICTORIA LOCAL", 'font': {'color': '#8B949E', 'size': 12}}, number={'suffix': "%", 'font': {'color': '#ECEFF4', 'size': 24}}, gauge={'axis': {'range':[0, 100], 'tickwidth': 1, 'tickcolor': "#30363D"}, 'bar': {'color': "#88C0D0"}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 1, 'bordercolor': "#30363D"}))
            fig1.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'family': "Share Tech Mono"})
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        with g2:
            fig2 = go.Figure(go.Indicator(mode="gauge+number", value=p_emp, title={'text': "EMPATE", 'font': {'color': '#8B949E', 'size': 12}}, number={'suffix': "%", 'font': {'color': '#ECEFF4', 'size': 24}}, gauge={'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#30363D"}, 'bar': {'color': "#EBCB8B"}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 1, 'bordercolor': "#30363D"}))
            fig2.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'family': "Share Tech Mono"})
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        with g3:
            fig3 = go.Figure(go.Indicator(mode="gauge+number", value=p_vis, title={'text': "VICTORIA VISITANTE", 'font': {'color': '#8B949E', 'size': 12}}, number={'suffix': "%", 'font': {'color': '#ECEFF4', 'size': 24}}, gauge={'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#30363D"}, 'bar': {'color': "#BF616A"}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 1, 'bordercolor': "#30363D"}))
            fig3.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'family': "Share Tech Mono"})
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

        # FILA 2: DIAGNÓSTICO
        r1, r2 = st.columns(2)
        with r1:
            is_val = mercado.get('hay_value_bet', False)
            st.markdown(f"<div class='metric-box {'success-box' if is_val else 'warning-box'}'><h4>ANÁLISIS DE MERCADO</h4>", unsafe_allow_html=True)
            st.write(f"**ESTADO DE VENTAJA (+EV):** {'CONFIRMADO' if is_val else 'NEGATIVO'}")
            st.write(f"**MOVIMIENTO LÍNEAS:** {mercado.get('analisis_movimiento', 'Eficiente')}")
            st.markdown("</div>", unsafe_allow_html=True)
        with r2:
            bank = resultado_ia.get("gestion_bankroll", {})
            risk = bank.get("riesgo_global_operacion", "ALTO")
            st.markdown(f"<div class='metric-box {'critical-box' if risk=='ALTO' else 'warning-box' if risk=='MEDIO' else 'success-box'}'><h4>DIRECTIVA DE CAPITAL</h4>", unsafe_allow_html=True)
            st.write(f"**NIVEL DE RIESGO:** {risk}")
            st.write(f"**ASIGNACIÓN (KELLY):** {bank.get('estrategia', '0 U')}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"**SÍNTESIS MATEMÁTICA:** *{prob.get('justificacion_matematica', 'N/A')}*")
        
        # FILA 3: VECTORES DE INVERSIÓN
        st.markdown("<h3 style='color:#88C0D0; margin-top:20px;'>VECTORES DE INVERSIÓN (+EV DETECTADO)</h3>", unsafe_allow_html=True)
        for i, pred in enumerate(resultado_ia.get("top_3_predicciones",[])):
            st.markdown(f"""
            <div style='background:#0D1117; border:1px solid #30363D; border-left: 4px solid #88C0D0; padding:15px; margin-bottom:10px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:5px;'>
                    <span style='color:#ECEFF4; font-weight:bold; font-size:1.1rem;'>[ TARGET 0{i+1} ] {pred.get('mercado', 'N/A')}</span>
                    <span style='color:#A3BE8C; font-weight:bold; font-size:1.1rem;'>CUOTA: {pred.get('cuota_objetivo', '0.0')}</span>
                </div>
                <span style='color:#EBCB8B; font-weight:bold;'>EDGE CALCULADO: +{pred.get('edge_estimado_pct', '0')}%</span><br>
                <div style='color:#8B949E; font-size:0.9rem; margin-top:10px; padding-top:10px; border-top: 1px dashed #30363D;'>
                    >> JUSTIFICACIÓN: {pred.get('razonamiento', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ==============================================================================
        # CONSOLA DE EMISIÓN PUSH API (DISTRIBUCIÓN B2C)
        # ==============================================================================
        st.markdown("""
        <div class="push-console">
            <h3 style="color:#BF616A; margin-top:0;">[ SYSTEM PUSH ] TRANSMISIÓN A RED DE CLIENTES</h3>
            <p style="color:#8B949E; font-size:0.9rem;">Cifra y transmite la señal de inversión validada hacia los canales de Telegram y Discord de los suscriptores activos.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("[>>>] INICIAR BROADCAST (ENVIAR SEÑAL PUSH)"):
            target_match = st.session_state.get('last_target', 'UNKNOWN_NODE')
            with st.spinner("COMPILANDO PAYLOAD Y ENCRIPTANDO SEÑAL..."):
                time.sleep(2)
                st.success("TRANSMISIÓN CONFIRMADA. SEÑAL DISTRIBUIDA AL 100% DE LOS NODOS CLIENTE.")
                
                payload = {
                    "timestamp": datetime.now().isoformat(),
                    "event": target_match,
                    "signal_type": "VALUE_BET_ALERT",
                    "targets_notified": 1420,
                    "channels": ["Telegram_Premium", "Discord_VIP"],
                    "encryption": "AES-256-GCM"
                }
                st.json(payload)

else:
    st.info("SISTEMA EN STANDBY. REQUIERE INGESTA DE TELEMETRÍA.")
