import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List
from datetime import datetime
from dateutil.relativedelta import relativedelta


class FinancialPredictor:
    
    def __init__(self):
        self.models = {
            'receita': RandomForestRegressor(n_estimators=100, random_state=42),
            'custo': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        self.label_encoders = {}
        self.is_trained = False
        self.last_training_date = None
        self.accuracy_scores = {}
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepara features para o modelo"""
        df = df.copy()
        
        # Converter competencia para datetime
        df['date'] = pd.to_datetime(df['competencia'])
        
        # Features temporais básicas
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        
        # Tendência (meses desde início)
        min_date = df['date'].min()
        df['months_since_start'] = ((df['date'] - min_date).dt.days / 30.44).round()
        
        # Sazonalidade cíclica (mês)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Encoding de categorias, se existir
        if 'categoria' in df.columns:
            if 'categoria' not in self.label_encoders:
                self.label_encoders['categoria'] = LabelEncoder()
                df['categoria_encoded'] = self.label_encoders['categoria'].fit_transform(df['categoria'])
            else:
                try:
                    df['categoria_encoded'] = self.label_encoders['categoria'].transform(df['categoria'])
                except ValueError:
                    df['categoria_encoded'] = 0
        
        return df
    
    def aggregate_monthly_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega dados por mês e tipo"""
        df_agg = df.groupby(['competencia', 'tipo']).agg({
            'valor': 'sum',
            'year': 'first',
            'month': 'first',
            'quarter': 'first',
            'months_since_start': 'first',
            'month_sin': 'first',
            'month_cos': 'first'
        }).reset_index()
        
        return df_agg
    
    def train(self, financial_data: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Treina os modelos de previsão"""
        df = pd.DataFrame(financial_data)
        
        if df.empty:
            raise ValueError("Não há dados suficientes para treinamento")
        
        df_features = self.prepare_features(df)
        df_agg = self.aggregate_monthly_data(df_features)
        
        feature_columns = ['year', 'month', 'quarter', 
                           'months_since_start', 'month_sin', 'month_cos']
        
        accuracy_scores = {}
        
        for tipo in ['receita', 'custo']:
            df_tipo = df_agg[df_agg['tipo'] == tipo].copy()
            
            if len(df_tipo) < 3:
                # Dados insuficientes, usar média simples
                self.models[tipo] = float(np.mean(df_tipo['valor'])) if not df_tipo.empty else 0.0
                accuracy_scores[tipo] = {"r2": 0.0, "mape": 0.0}
            else:
                # Dados suficientes, treinar modelo
                X = df_tipo[feature_columns]
                y = df_tipo['valor']
                
                # Garantir que o modelo seja um objeto treinável
                if isinstance(self.models[tipo], (int, float)):
                    self.models[tipo] = LinearRegression()
                
                self.models[tipo].fit(X, y)
                
                # Avaliação
                y_pred = self.models[tipo].predict(X)
                r2 = r2_score(y, y_pred)
                mape = 1 - mean_absolute_percentage_error(y, y_pred)  # 1 - erro → "quanto acertou"
                
                accuracy_scores[tipo] = {"r2": r2, "mape": mape}
        
        self.is_trained = True
        self.last_training_date = datetime.utcnow()
        self.accuracy_scores = accuracy_scores
        
        return accuracy_scores
    
    def predict_future(self, base_date: str, periods: List[int]) -> Dict:
        """Faz previsões para os períodos especificados"""
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado")
        
        predictions = {}
        base_datetime = datetime.strptime(base_date, '%Y-%m')
        
        for period in periods:
            # Avançar em meses (30 = 1 mês, 60 = 2 meses)
            future_date = base_datetime + relativedelta(months=period // 30)
            
            features = {
                'year': future_date.year,
                'month': future_date.month,
                'quarter': (future_date.month - 1) // 3 + 1,
                'months_since_start': (future_date.year - base_datetime.year) * 12 
                                       + (future_date.month - base_datetime.month),
                'month_sin': np.sin(2 * np.pi * future_date.month / 12),
                'month_cos': np.cos(2 * np.pi * future_date.month / 12)
            }
            
            X_future = pd.DataFrame([features])
            
            for tipo in ['receita', 'custo']:
                if isinstance(self.models[tipo], (int, float)):
                    prediction = self.models[tipo]
                    confidence_interval = [prediction * 0.9, prediction * 1.1]
                    r2_val, mape_val = 0.0, 0.0
                else:
                    prediction = self.models[tipo].predict(X_future)[0]
                    confidence_interval = [prediction * 0.85, prediction * 1.15]
                    r2_val = float(self.accuracy_scores.get(tipo, {}).get("r2", 0.0))
                    mape_val = float(self.accuracy_scores.get(tipo, {}).get("mape", 0.0))
                
                key = f"{tipo}_{period}d"
                predictions[key] = {
                    'valor_previsto': float(max(0, prediction)),
                    'intervalo_confianca': [
                        float(max(0, confidence_interval[0])),
                        float(confidence_interval[1])
                    ],
                    'acuracia_r2': r2_val,
                    'acuracia_mape': mape_val,
                    'modelo_usado': 'random_forest' if hasattr(self.models[tipo], 'predict') else 'simple_average'
                }
        
        return predictions
