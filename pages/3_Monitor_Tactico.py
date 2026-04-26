import streamlit as st
import pandas as pd
import requests
import sports_core as sc

st.set_page_config(page_title="Monitor Táctico | AGATHA", layout="wide")
sc.set_agatha_theme()

st.markdown("""
<style>
    div.stButton > button { border-color: #EBCB8B !important; color: #EBCB8B !important; }
    div.stButton > button:hover { background-color: rgba(235, 203, 139, 0.1) !important; box-shadow: 0 0 10px #EBCB8B; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#EBCB8B;'>[3] MONITOR TÁCTICO EN TIEMPO REAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// TELEMETRÍA DE ALINEACIONES, BAJAS CRÍTICAS Y ECOSISTEMA DEL ENCUENTRO</p>", unsafe_allow_html=True)
st.markdown("---")

@st.cache_data(ttl=900, show_spinner=False)
def fetch_tactical_lineups(fixture_id: int) -> list:
    api_key = sc.get_secret("API_FOOTBALL_KEY")
    try:
        r = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers={"x-apisports-key": api_key}, params={"fixture": fixture_id}, timeout=10)
        return r.json().get("response",[])
    except: return[]

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tactical_injuries(fixture_id: int) -> list:
    api_key = sc.get_secret("API_FOOTBALL_KEY")
    try:
        r = requests.get("https://v3.football.api-sports.io/injuries", headers={"x-apisports-key": api_key}, params={"fixture": fixture_id}, timeout=10)
        return r.json().get("response", [])
    except: return[]

if 'fixtures' not in st.session_state or st.session_state['fixtures'].empty:
    st.warning("No se ha detectado telemetría base. Regrese al MOTOR PREDICTIVO para cargar los partidos.")
else:
    df_f = st.session_state['fixtures']
    col_1, col_2 = st.columns([1, 2])
    with col_1: target_league = st.selectbox("FILTRO DE COMPETICIÓN",["TODAS"] + df_f['league_name'].unique().tolist())
    if target_league != "TODAS": df_f = df_f[df_f['league_name'] == target_league]
    partidos_lista = df_f.apply(lambda row: f"{row['home_team']} vs {row['away_team']} (ID: {row['fixture_id']})", axis=1).tolist()
    with col_2: partido_seleccionado = st.selectbox("SELECCIONAR NODO TÁCTICO", partidos_lista)

    st.markdown("---")

    if st.button("INTERCEPTAR TELEMETRÍA EN VIVO"):
        idx = partidos_lista.index(partido_seleccionado)
        fixture_id = df_f.iloc[idx]['fixture_id']
        home_t = df_f.iloc[idx]['home_team']
        away_t = df_f.iloc[idx]['away_team']
        
        with st.spinner("Estableciendo enlace con reportes médicos..."):
            lineups = fetch_tactical_lineups(fixture_id)
            injuries = fetch_tactical_injuries(fixture_id)
            
            c_local, c_away = st.columns(2)
            if not lineups:
                st.info("Alineaciones no disponibles aún.")
            else:
                for t_data in lineups:
                    t_name = t_data['team']['name']
                    target_col = c_local if t_name == home_t else c_away
                    with target_col:
                        st.markdown(f"<div class='metric-box lineup-box'><h3 style='color:#A3BE8C;'>FORMACIÓN: {t_name.upper()}</h3>", unsafe_allow_html=True)
                        st.write(f"**ESQUEMA:** {t_data['formation']}")
                        xi_text = "".join([f"[{p['player']['pos']}] {p['player']['number']} - {p['player']['name']} \n" for p in t_data['startXI']])
                        st.text(xi_text)
                        st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<h3 style='color:#EBCB8B;'>REPORTE DE AUSENCIAS</h3>", unsafe_allow_html=True)
            if not injuries:
                st.success("Sin reportes médicos activos.")
            else:
                df_inj = pd.DataFrame(injuries)
                df_inj['player_name'] = df_inj['player'].apply(lambda x: x.get('name'))
                df_inj['team_name'] = df_inj['team'].apply(lambda x: x.get('name'))
                df_inj['reason'] = df_inj['player'].apply(lambda x: x.get('reason'))
                
                i_local, i_away = st.columns(2)
                with i_local:
                    bl = df_inj[df_inj['team_name'] == home_t]
                    st.markdown(f"<div class='metric-box injury-box'><h4 style='color:#BF616A;'>BAJAS: {home_t.upper()}</h4>", unsafe_allow_html=True)
                    if not bl.empty:
                        for _, row in bl.iterrows(): st.write(f"**{row['player_name']}**: {row['reason']}")
                    else: st.write("Plantilla 100% operativa.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with i_away:
                    ba = df_inj[df_inj['team_name'] == away_t]
                    st.markdown(f"<div class='metric-box injury-box'><h4 style='color:#BF616A;'>BAJAS: {away_t.upper()}</h4>", unsafe_allow_html=True)
                    if not ba.empty:
                        for _, row in ba.iterrows(): st.write(f"**{row['player_name']}**: {row['reason']}")
                    else: st.write("Plantilla 100% operativa.")
                    st.markdown("</div>", unsafe_allow_html=True)
        sc.release_memory()
