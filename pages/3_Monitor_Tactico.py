import streamlit as st
import pandas as pd
import requests
import sports_core as sc

st.set_page_config(page_title="Monitor Táctico | AGATHA", layout="wide")
sc.set_agatha_theme()
sc.return_to_main()

st.markdown("""<style>div.stButton > button { border-color: #EBCB8B !important; color: #EBCB8B !important; } div.stButton > button:hover { background-color: rgba(235, 203, 139, 0.1) !important; }</style>""", unsafe_allow_html=True)
st.markdown("<h1 style='color:#EBCB8B;'>[3] MONITOR TÁCTICO EN TIEMPO REAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// TELEMETRÍA DE ALINEACIONES Y BAJAS CRÍTICAS</p>", unsafe_allow_html=True)
st.markdown("---")

@st.cache_data(ttl=900, show_spinner=False)
def fetch_tactics(fixture_id: int, endpoint: str):
    try:
        r = requests.get(f"https://v3.football.api-sports.io/{endpoint}", headers={"x-apisports-key": sc.get_secret("API_FOOTBALL_KEY")}, params={"fixture": fixture_id}, timeout=10)
        return r.json().get("response",[])
    except: return[]

if 'fixtures' not in st.session_state or st.session_state['fixtures'].empty:
    st.warning("Sin telemetría base. Cargue partidos en el Cuadrante 1.")
else:
    df_f = st.session_state['fixtures']
    col_1, col_2 = st.columns([1, 2])
    with col_1: target_league = st.selectbox("COMPETICIÓN", ["TODAS"] + df_f['league_name'].unique().tolist())
    if target_league != "TODAS": df_f = df_f[df_f['league_name'] == target_league]
    partidos = df_f.apply(lambda r: f"{r['home_team']} vs {r['away_team']} (ID: {r['fixture_id']})", axis=1).tolist()
    with col_2: part_sel = st.selectbox("NODO TÁCTICO", partidos)

    if st.button("INTERCEPTAR TELEMETRÍA"):
        row = df_f.iloc[partidos.index(part_sel)]
        with st.spinner("Enlazando..."):
            lineups = fetch_tactics(row['fixture_id'], "fixtures/lineups")
            injuries = fetch_tactics(row['fixture_id'], "injuries")
            
            cl, ca = st.columns(2)
            for t in lineups:
                tgt = cl if t['team']['name'] == row['home_team'] else ca
                with tgt:
                    st.markdown(f"<div class='metric-box lineup-box'><h3 style='color:#A3BE8C;'>FORMACIÓN: {t['team']['name']}</h3>", unsafe_allow_html=True)
                    st.text("".join([f"[{p['player']['pos']}] {p['player']['number']} - {p['player']['name']}\n" for p in t['startXI']]))
                    st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<h3 style='color:#EBCB8B;'>REPORTES MÉDICOS</h3>", unsafe_allow_html=True)
            df_inj = pd.DataFrame(injuries)
            if not df_inj.empty:
                df_inj['p'] = df_inj['player'].apply(lambda x: x.get('name'))
                df_inj['t'] = df_inj['team'].apply(lambda x: x.get('name'))
                df_inj['r'] = df_inj['player'].apply(lambda x: x.get('reason'))
                il, ia = st.columns(2)
                with il:
                    st.markdown(f"<div class='metric-box injury-box'><h4 style='color:#BF616A;'>BAJAS: {row['home_team']}</h4>", unsafe_allow_html=True)
                    for _, r in df_inj[df_inj['t'] == row['home_team']].iterrows(): st.write(f"**{r['p']}**: {r['r']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with ia:
                    st.markdown(f"<div class='metric-box injury-box'><h4 style='color:#BF616A;'>BAJAS: {row['away_team']}</h4>", unsafe_allow_html=True)
                    for _, r in df_inj[df_inj['t'] == row['away_team']].iterrows(): st.write(f"**{r['p']}**: {r['r']}")
                    st.markdown("</div>", unsafe_allow_html=True)
            else: st.success("Sin bajas.")
