import gc
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# ==============================================================================
# MOTOR DE PREDICCIÓN DE COMPORTAMIENTO MASIVO (PUBLIC MONEY SKEW)
# ==============================================================================

class PublicBehaviorModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def release_memory(self):
        """Liberación explícita de tensores y dataframes para prevención OOM."""
        gc.collect()

    def generate_training_data(self, samples: int = 10000) -> pd.DataFrame:
        """
        Generación de dataset sintético basado en patrones históricos de apuestas.
        En producción, se alimenta del histórico de cuotas de The Odds API y Betfair Exchange.
        """
        np.random.seed(42)
        
        # Vectores de comportamiento público
        # 1. Popularidad del equipo (0 a 100)
        popularity_index = np.random.uniform(10, 100, samples)
        
        # 2. Racha de victorias recientes (0 a 5)
        recent_win_streak = np.random.randint(0, 6, samples)
        
        # 3. Tipo de mercado (1 = Over/Favorito, 0 = Under/Underdog)
        is_popular_market = np.random.randint(0, 2, samples)
        
        # 4. Caída de cuota desde apertura (Drop percentage)
        odds_drop_pct = np.random.exponential(scale=2.0, size=samples)
        
        # Construcción de la matriz
        df = pd.DataFrame({
            'popularity_index': popularity_index,
            'recent_win_streak': recent_win_streak,
            'is_popular_market': is_popular_market,
            'odds_drop_pct': odds_drop_pct
        })
        
        # Lógica de clasificación: Alta probabilidad de sesgo público si:
        # Equipo popular + En racha + Mercado de acción + Fuerte caída de cuota
        condition = (
            (df['popularity_index'] > 75) & 
            (df['is_popular_market'] == 1) & 
            (df['recent_win_streak'] >= 3)
        )
        
        # Ruido estocástico para realismo
        noise = np.random.uniform(0, 1, samples) > 0.85
        df['public_skew_detected'] = np.where(condition | noise, 1, 0)
        
        return df

    def train_model(self, df: pd.DataFrame):
        """Entrenamiento del clasificador de sesgo cognitivo."""
        features =['popularity_index', 'recent_win_streak', 'is_popular_market', 'odds_drop_pct']
        
        X = df[features]
        y = df['public_skew_detected']
        
        X_scaled = self.scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Limpieza de matrices de entrenamiento
        del X, y, X_scaled, X_train, X_test, y_train, y_test
        self.release_memory()

    def predict_public_bias(self, current_matches: pd.DataFrame) -> pd.DataFrame:
        """
        Inferencia sobre la matriz de partidos actual.
        Devuelve la probabilidad matemática de que el público infle la cuota.
        """
        if not self.is_trained:
            raise RuntimeError("El modelo Predictivo de Comportamiento no ha sido inicializado.")
            
        features =['popularity_index', 'recent_win_streak', 'is_popular_market', 'odds_drop_pct']
        
        # Validación de integridad de la matriz
        for col in features:
            if col not in current_matches.columns:
                current_matches[col] = 0
                
        X_predict = self.scaler.transform(current_matches[features])
        
        # Obtención de probabilidades (Clase 1: Existe sesgo público)
        probabilities = self.model.predict_proba(X_predict)[:, 1]
        
        current_matches['prob_public_money_%'] = np.round(probabilities * 100, 2)
        
        # Directiva Táctica: Fading the Public
        current_matches['directiva_tactica'] = np.where(
            current_matches['prob_public_money_%'] > 80.0,
            "FADE THE PUBLIC: Buscar valor (+EV) en la cuota opuesta (Underdog/Under). Inflación detectada.",
            "MERCADO NEUTRAL: Evaluar exclusivamente bajo métricas xG."
        )
        
        del X_predict
        self.release_memory()
        
        return current_matches

# ==============================================================================
# EJECUCIÓN AISLADA (TESTING)
# ==============================================================================
if __name__ == "__main__":
    engine = PublicBehaviorModel()
    
    # 1. Ingesta de datos históricos y calibración
    historical_data = engine.generate_training_data(samples=50000)
    engine.train_model(historical_data)
    
    # 2. Simulación de matriz de partidos actuales (Ingesta The Odds API)
    live_market = pd.DataFrame({
        'match': ['Real Madrid vs Alaves', 'Getafe vs Osasuna', 'Man City vs Fulham'],
        'popularity_index': [95, 30, 92],
        'recent_win_streak':[4, 1, 5],
        'is_popular_market': [1, 0, 1], # 1 = Mercado Over/Favorito
        'odds_drop_pct':[5.2, 0.5, 6.8]
    })
    
    # 3. Predicción de comportamiento poblacional
    analyzed_market = engine.predict_public_bias(live_market)
    
    # Extracción de resultados
    print(analyzed_market[['match', 'prob_public_money_%', 'directiva_tactica']].to_string(index=False))
