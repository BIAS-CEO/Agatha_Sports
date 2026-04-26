import os
import gc
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime

# ==============================================================================
# GESTIÓN DE MEMORIA Y RECURSOS
# ==============================================================================
def release_memory():
    """Liberación explícita de memoria para prevención OOM."""
    gc.collect()

# ==============================================================================
# GESTIÓN DE CREDENCIALES
# ==============================================================================
def get_secret(key: str) -> str:
    """Extracción segura de secretos compatible con Streamlit."""
    try:
        return st.secrets["api_keys"][key]
    except KeyError:
        st.error(f"BRECHA DE CONFIGURACIÓN: Clave {key} no encontrada en secrets.toml.")
        st.stop()

# ==============================================================================
# CAPA 2: PIPELINE DE INGESTA (API-FOOTBALL)
# ==============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_daily_fixtures(date_str: str) -> pd.DataFrame:
    """Ingesta de partidos programados para una fecha específica."""
    api_key = get_secret("API_FOOTBALL_KEY")
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-apisports-key": api_key,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    params = {"date": date_str}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json().get("response",[])
        
        if not data:
            return pd.DataFrame()
            
        df_list =[]
        for item in data:
            df_list.append({
                "fixture_id": item["fixture"]["id"],
                "league_name": item["league"]["name"],
                "league_id": item["league"]["id"],
                "home_team": item["teams"]["home"]["name"],
                "home_id": item["teams"]["home"]["id"],
                "away_team": item["teams"]["away"]["name"],
                "away_id": item["teams"]["away"]["id"],
                "status": item["fixture"]["status"]["short"],
                "date": item["fixture"]["date"]
            })
            
        df = pd.DataFrame(df_list)
        return df
    except Exception as e:
        st.error(f"FALLO DE CONEXIÓN (API-Football): {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_team_statistics(team_id: int, league_id: int, season: int) -> dict:
    """Extracción de telemetría histórica del equipo para el dossier táctico."""
    api_key = get_secret("API_FOOTBALL_KEY")
    url = "https://v3.football.api-sports.io/teams/statistics"
    headers = {
        "x-apisports-key": api_key,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    params = {
        "team": team_id,
        "league": league_id,
        "season": season
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json().get("response", {})
    except Exception as e:
        return {"error": str(e)}

# ==============================================================================
# CAPA 2: PIPELINE DE INGESTA (THE ODDS API)
# ==============================================================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_market_odds(sport_key: str = "soccer_spain_la_liga") -> pd.DataFrame:
    """Extracción de cuotas de mercado (Benchmark para cálculo +EV)."""
    api_key = get_secret("ODDS_API_KEY")
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h,totals",
        "oddsFormat": "decimal"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return pd.DataFrame()
            
        odds_list =[]
        for match in data:
            match_name = f"{match['home_team']} vs {match['away_team']}"
            bookmakers = match.get("bookmakers",[])
            
            if not bookmakers:
                continue
                
            # Extraer la mejor línea disponible (Pinnacle o primer bookmaker)
            target_bookmaker = next((b for b in bookmakers if b["key"] == "pinnacle"), bookmakers[0])
            
            for market in target_bookmaker.get("markets",[]):
                market_name = market["key"]
                for outcome in market.get("outcomes",[]):
                    odds_list.append({
                        "match": match_name,
                        "home_team": match['home_team'],
                        "away_team": match['away_team'],
                        "bookmaker": target_bookmaker["title"],
                        "market": market_name,
                        "selection": outcome["name"],
                        "price": outcome["price"]
                    })
                    
        return pd.DataFrame(odds_list)
    except Exception as e:
        st.error(f"FALLO DE CONEXIÓN (The Odds API): {str(e)}")
        return pd.DataFrame()

# ==============================================================================
# CAPA 3: MOTOR DE INTELIGENCIA PREDICTIVA (OPENAI)
# ==============================================================================
def extract_json_from_response(response_str: str) -> dict:
    """Filtro estricto para purgar ruido del LLM y devolver diccionario puro."""
    try:
        if not isinstance(response_str, str): return {}
        if "```json" in response_str:
            response_str = response_str.split("```json")[1].split("```")[0]
        elif "```" in response_str:
            response_str = response_str.split("```")[1].split("```")[0]
        return json.loads(response_str.strip())
    except json.JSONDecodeError:
        return {"error": "JSON_DECODE_FAILED", "raw_output": response_str}

def _execute_openai_call(prompt: str, system_message: str, temperature: float) -> str:
    """Transmisión sincronizada al núcleo de inferencia lógica."""
    api_key = get_secret("OPENAI_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4-turbo",
        "messages":[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return json.dumps({"error": f"Fallo de motor IA: {str(e)}"})

@st.cache_data(ttl=3600, show_spinner=False)
def predict_match_value(dossier_partido: dict, cuotas_mercado: dict) -> dict:
    """
    Protocolo de análisis 'Billy Walters'.
    Determina probabilidad real, compara con cuotas y calcula el edge (+EV).
    """
    system_prompt = """
    Soy AGATHA. Actúo como Analista Profesional de Apuestas Deportivas y Modelador Matemático.
    Detecto ineficiencias en el mercado (Value Bets / +EV) procesando estadísticas tácticas. No emito opiniones, calculo probabilidades.

    Salida OBLIGATORIA en JSON estricto:
    {
        "evaluacion_probabilidades": {
            "1X2": {"local": 0.0, "empate": 0.0, "visitante": 0.0},
            "justificacion_matematica": "Análisis táctico (xG, bajas, contexto)."
        },
        "analisis_mercado": {
            "hay_value_bet": true/false,
            "analisis_movimiento": "Análisis de sharps vs público."
        },
        "top_3_predicciones":[
            {
                "mercado": "Ej: Asian Handicap -1",
                "cuota_objetivo": 0.0,
                "edge_estimado_pct": 0.0,
                "nivel_riesgo": "BAJO/MEDIO/ALTO",
                "razonamiento": "Justificación matemática."
            }
        ],
        "gestion_bankroll": {
            "estrategia": "Kelly fraccional recomendado.",
            "riesgo_global_operacion": "BAJO/MEDIO/ALTO"
        }
    }
    """
    
    prompt = f"""
    **DOSSIER DE INTELIGENCIA DEL PARTIDO:**
    {json.dumps(dossier_partido, indent=2, ensure_ascii=False)}

    **CUOTAS ACTUALES DEL MERCADO:**
    {json.dumps(cuotas_mercado, indent=2, ensure_ascii=False)}

    **ACCIÓN REQUERIDA:**
    Ejecuta el cálculo predictivo y genera el JSON de inteligencia.
    """
    
    raw_response = _execute_openai_call(prompt, system_prompt, 0.2)
    return extract_json_from_response(raw_response)

# ==============================================================================
# UTILIDAD DE ENSAMBLAJE
# ==============================================================================
def compile_match_dossier(match_data: dict, home_stats: dict, away_stats: dict) -> dict:
    """Fusiona telemetría cruda en un dossier estructurado para el LLM."""
    dossier = {
        "contexto_evento": {
            "liga": match_data.get("league_name"),
            "fecha": match_data.get("date"),
            "local": match_data.get("home_team"),
            "visitante": match_data.get("away_team")
        },
        "rendimiento_local": home_stats,
        "rendimiento_visitante": away_stats
    }
    return dossier
