import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Importación del núcleo analítico para utilidades base
import sports_core as sc

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y CSS TÁCTICO
# ==============================================================================
st.set_page_config(page_title="Monitor Táctico | AGATHA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #050505; font-family: 'Share Tech Mono', monospace; color: #ECEFF4; }
    h1, h2, h3 { font-family: 'Rajdhani', sans-serif; color: #EBCB8B; text-transform: uppercase; }
    .metric-box {
        border-left: 4px solid #EBCB8B;
        background-color: #161B22;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .injury-box { border-left-color: #BF616A; background-color: rgba(191, 97, 106, 0.05); }
    .lineup-box { border-left-color: #A3BE8C; background-color: rgba(163, 190, 140, 0.05); }
    div.stButton > button {
        border: 1px solid #EBCB8B !important;
        background-color: rgba(235, 203, 139, 0.1) !important;
        color: #EBCB8B !important;
        border-radius: 0px !important;
        width: 100%;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover { background-color: rgba(235, 203, 139, 0.3) !important; box-shadow: 0 0 10px #EBCB8B; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CABECERA DE SISTEMA
# ==============================================================================
st.markdown("<h1>[3] MONITOR TÁCTICO EN TIEMPO REAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;'>// TELEMETRÍA DE ALINEACIONES, BAJAS CRÍTICAS Y ECOSISTEMA DEL ENCUENTRO</p>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# FUNCIONES DE EXTRACCIÓN ESPECÍFICAS DEL MÓDULO (API-FOOTBALL)
# ==============================================================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_tactical_lineups(fixture_id: int) -> list:
    """Extracción de formaciones y 11 inicial."""
    api_key = sc.get_secret("API_FOOTBALL_KEY")
    url = "https://v3.football.api-sports.io/fixtures/lineups"
    headers = {"x-apisports-key": api_key, "x-rapidapi-host": "v3.football.api-sports.io"}
    try:
        response = requests.get(url, headers=headers, params={"fixture": fixture_id}, timeout=10)
        response.raise_for_status()
        return response.json().get("response", [])
    except:
        return[]

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tactical_injuries(fixture_id: int) -> list:
    """Extracción de reportes médicos y ausencias disciplinarias."""
    api_key = sc.get_secret("API_FOOTBALL_KEY")
    url = "https://v3.football.api-sports.io/injuries"
    headers = {"x-apisports-key": api_key, "x-rapidapi-host": "v3.football.api-sports.io"}
    try:
        response = requests.get(url, headers=headers, params={"fixture": fixture_id}, timeout=10)
        response.raise_for_status()
        return response.json().get("response", [])
    except:
        return[]

# ==============================================================================
# PANEL DE CONTROL OPERATIVO
# ==============================================================================
# Rescate de la fecha y los partidos cargados en la sesión desde el Cuadrante 1
if 'fixtures' not in st.session_state or st.session_state['fixtures'].empty:
    st.warning("No se ha detectado telemetría base en la memoria del sistema. Regrese al MOTOR PREDICTIVO para cargar los partidos de la jornada.")
else:
    df_f = st.session_state['fixtures']
    
    col_1, col_2 = st.columns([1, 2])
    with col_1:
        target_league = st.selectbox("FILTRO DE COMPETICIÓN", ["TODAS"] + df_f['league_name'].unique().tolist())
    
    if target_league != "TODAS":
        df_f = df_f[df_f['league_name'] == target_league]
        
    partidos_lista = df_f.apply(lambda row: f"{row['home_team']} vs {row['away_team']} (ID: {row['fixture_id']})", axis=1).tolist()
    
    with col_2:
        partido_seleccionado = st.selectbox("SELECCIONAR NODO TÁCTICO", partidos_lista)

    st.markdown("---")

    # ==============================================================================
    # RENDERIZADO DE TELEMETRÍA TÁCTICA
    # ==============================================================================
    if st.button("INTERCEPTAR TELEMETRÍA EN VIVO"):
        idx = partidos_lista.index(partido_seleccionado)
        fixture_id = df_f.iloc[idx]['fixture_id']
        home_team_name = df_f.iloc[idx]['home_team']
        away_team_name = df_f.iloc[idx]['away_team']
        
        with st.spinner("Estableciendo enlace con servidores tácticos y reportes médicos..."):
            lineups = fetch_tactical_lineups(fixture_id)
            injuries = fetch_tactical_injuries(fixture_id)
            
            c_local, c_away = st.columns(2)
            
            # --- SECCIÓN: ALINEACIONES ---
            if not lineups:
                st.info("Alineaciones no disponibles aún. El protocolo estándar indica publicación 60 minutos antes del evento.")
            else:
                for team_data in lineups:
                    team_name = team_data['team']['name']
                    formation = team_data['formation']
                    coach = team_data['coach']['name']
                    start_xi = team_data['startXI']
                    
                    target_col = c_local if team_name == home_team_name else c_away
                    
                    with target_col:
                        st.markdown(f"<div class='metric-box lineup-box'>", unsafe_allow_html=True)
                        st.markdown(f"### FORMACIÓN: {team_name.upper()}")
                        st.write(f"**ESQUEMA TÁCTICO:** {formation}")
                        st.write(f"**DIRECTOR TÉCNICO:** {coach}")
                        st.markdown("**ONCE INICIAL:**")
                        
                        # Vectorización visual simple del equipo
                        xi_text = ""
                        for player in start_xi:
                            number = player['player']['number']
                            p_name = player['player']['name']
                            pos = player['player']['pos']
                            xi_text += f"[{pos}] {number} - {p_name} \n"
                        st.text(xi_text)
                        st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # --- SECCIÓN: REPORTE DE BAJAS Y LESIONES ---
            st.markdown("### REPORTE DE AUSENCIAS (LESIONES / SANCIONES)")
            if not injuries:
                st.success("No se detectan reportes médicos activos en la matriz de datos para este encuentro.")
            else:
                # Convertimos las lesiones a dataframe para mejor manipulación y evitar OOM
                df_injuries = pd.DataFrame(injuries)
                
                # Extraemos nombres de jugador y equipo lidiando con JSON anidado
                df_injuries['player_name'] = df_injuries['player'].apply(lambda x: x.get('name'))
                df_injuries['team_name'] = df_injuries['team'].apply(lambda x: x.get('name'))
                df_injuries['reason'] = df_injuries['player'].apply(lambda x: x.get('reason'))
                
                i_local, i_away = st.columns(2)
                
                with i_local:
                    bajas_local = df_injuries[df_injuries['team_name'] == home_team_name]
                    st.markdown(f"<div class='metric-box injury-box'>", unsafe_allow_html=True)
                    st.markdown(f"#### BAJAS: {home_team_name.upper()}")
                    if not bajas_local.empty:
                        for _, row in bajas_local.iterrows():
                            st.write(f"**{row['player_name']}**: {row['reason']}")
                    else:
                        st.write("Plantilla operativa al 100%.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with i_away:
                    bajas_away = df_injuries[df_injuries['team_name'] == away_team_name]
                    st.markdown(f"<div class='metric-box injury-box'>", unsafe_allow_html=True)
                    st.markdown(f"#### BAJAS: {away_team_name.upper()}")
                    if not bajas_away.empty:
                        for _, row in bajas_away.iterrows():
                            st.write(f"**{row['player_name']}**: {row['reason']}")
                    else:
                        st.write("Plantilla operativa al 100%.")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                del df_injuries
                
        sc.release_memory()
