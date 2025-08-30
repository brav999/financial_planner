import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import calendar

class FinancialPredictor:
    
    def __init__(self):
        self.models = {
            'receita': LinearRegression(),
            'custo': LinearRegression()
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
        
        # Features temporais
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        
        # Feature de tendência (meses desde início)
        min_date = df['date'].min()
        df['months_since_start'] = ((df['date'] - min_date).dt.days / 30.44).round()
        
        # Encoding de categorias
        if 'categoria' in df.columns:
            if 'categoria' not in self.label_encoders:
                self.label_encoders['categoria'] = LabelEncoder()
                df['categoria_encoded'] = self.label_encoders['categoria'].fit_transform(df['categoria'])
            else:
                # Para dados novos, usar encoder já treinado
                try:
                    df['categoria_encoded'] = self.label_encoders['categoria'].transform(df['categoria'])
                except ValueError:
                    # Categoria nova não vista no treinamento
                    df['categoria_encoded'] = 0
        
        return df
    
    def aggregate_monthly_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega dados por mês e tipo"""
        df_agg = df.groupby(['competencia', 'tipo']).agg({
            'valor': 'sum',
            'year': 'first',
            'month': 'first',
            'quarter': 'first',
            'months_since_start': 'first'
        }).reset_index()
        
        return df_agg
    
    def train(self, financial_data: List[Dict]) -> Dict[str, float]:
        """Treina os modelos de previsão"""
        df = pd.DataFrame(financial_data)
        
        if df.empty:
            raise ValueError("Não há dados suficientes para treinamento")
        
        # Preparar features
        df_features = self.prepare_features(df)
        df_agg = self.aggregate_monthly_data(df_features)
        
        # Features para o modelo
        feature_columns = ['year', 'month', 'quarter', 'months_since_start']
        
        accuracy_scores = {}
        
        for tipo in ['receita', 'custo']:
            df_tipo = df_agg[df_agg['tipo'] == tipo].copy()
            
            if len(df_tipo) < 3:
                # Dados insuficientes, usar média simples
                self.models[tipo] = float(np.mean(df_tipo['valor'])) if not df_tipo.empty else 0.0
                accuracy_scores[tipo] = 0.0
                continue
            
            X = df_tipo[feature_columns]
            y = df_tipo['valor']
            
            # Treinar modelo
            self.models[tipo].fit(X, y)
            
            # Calcular acurácia
            y_pred = self.models[tipo].predict(X)
            accuracy_scores[tipo] = r2_score(y, y_pred)
        
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
            future_date = base_datetime + timedelta(days=period)
            
            # Preparar features para a data futura
            features = {
                'year': future_date.year,
                'month': future_date.month,
                'quarter': (future_date.month - 1) // 3 + 1,
                'months_since_start': period // 30  # Aproximação
            }
            
            X_future = pd.DataFrame([features])
            
            for tipo in ['receita', 'custo']:
                if isinstance(self.models[tipo], (int, float)):
                    # Modelo simples (média)
                    prediction = self.models[tipo]
                    confidence_interval = [prediction * 0.9, prediction * 1.1]
                else:
                    # Modelo treinado
                    prediction = self.models[tipo].predict(X_future)[0]
                    # Intervalo de confiança simples (±15%)
                    confidence_interval = [prediction * 0.85, prediction * 1.15]
                
                key = f"{tipo}_{period}d"
                predictions[key] = {
                    'valor_previsto': float(max(0, prediction)),  # Converter para float Python
                    'intervalo_confianca': [float(max(0, confidence_interval[0])), float(confidence_interval[1])],
                    'acuracia_historica': float(self.accuracy_scores.get(tipo, 0.0)),
                    'modelo_usado': 'linear_regression' if hasattr(self.models[tipo], 'predict') else 'simple_average'
                }
        
        return predictions
