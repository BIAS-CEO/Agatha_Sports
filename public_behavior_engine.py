import gc
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class PublicBehaviorModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def release_memory(self):
        gc.collect()

    def generate_training_data(self, samples: int = 10000) -> pd.DataFrame:
        np.random.seed(42)
        popularity_index = np.random.uniform(10, 100, samples)
        recent_win_streak = np.random.randint(0, 6, samples)
        is_popular_market = np.random.randint(0, 2, samples)
        odds_drop_pct = np.random.exponential(scale=2.0, size=samples)
        
        df = pd.DataFrame({'popularity_index': popularity_index, 'recent_win_streak': recent_win_streak, 'is_popular_market': is_popular_market, 'odds_drop_pct': odds_drop_pct})
        condition = ((df['popularity_index'] > 75) & (df['is_popular_market'] == 1) & (df['recent_win_streak'] >= 3))
        noise = np.random.uniform(0, 1, samples) > 0.85
        df['public_skew_detected'] = np.where(condition | noise, 1, 0)
        return df

    def train_model(self, df: pd.DataFrame):
        features =['popularity_index', 'recent_win_streak', 'is_popular_market', 'odds_drop_pct']
        X = df[features]
        y = df['public_skew_detected']
        X_scaled = self.scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        self.is_trained = True
        del X, y, X_scaled, X_train, X_test, y_train, y_test
        self.release_memory()

    def predict_public_bias(self, current_matches: pd.DataFrame) -> pd.DataFrame:
        if not self.is_trained: raise RuntimeError("Modelo no inicializado.")
        features =['popularity_index', 'recent_win_streak', 'is_popular_market', 'odds_drop_pct']
        for col in features:
            if col not in current_matches.columns: current_matches[col] = 0
        X_predict = self.scaler.transform(current_matches[features])
        probabilities = self.model.predict_proba(X_predict)[:, 1]
        current_matches['prob_public_money_%'] = np.round(probabilities * 100, 2)
        current_matches['directiva_tactica'] = np.where(current_matches['prob_public_money_%'] > 80.0, "FADE THE PUBLIC: Buscar valor (+EV) en la cuota opuesta.", "MERCADO NEUTRAL: Evaluar exclusivamente bajo métricas xG.")
        del X_predict
        self.release_memory()
        return current_matches
