"""
Módulo de modelos de Machine Learning para previsões climáticas.
Inclui modelos para previsão de temperatura e classificação de qualidade do ar.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class TemperaturePredictionModel:
    """Modelo para previsão de temperatura baseado em dados históricos."""
    
    def __init__(self):
        """Inicializa o modelo de previsão de temperatura."""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features temporais e climáticas para o modelo.
        
        Args:
            df: DataFrame com dados climáticos
            
        Returns:
            DataFrame com features preparadas
        """
        features = df.copy()
        
        # Features temporais
        if 'timestamp' in features.columns:
            features['timestamp'] = pd.to_datetime(features['timestamp'])
            features['month'] = features['timestamp'].dt.month
            features['day_of_year'] = features['timestamp'].dt.dayofyear
            features['hour'] = features['timestamp'].dt.hour
            
            # Encoding cíclico para capturar sazonalidade
            features['month_sin'] = np.sin(2 * np.pi * features['month'] / 12)
            features['month_cos'] = np.cos(2 * np.pi * features['month'] / 12)
            features['day_sin'] = np.sin(2 * np.pi * features['day_of_year'] / 365)
            features['day_cos'] = np.cos(2 * np.pi * features['day_of_year'] / 365)
        
        # Features climáticas derivadas
        if 'humidity' in features.columns and 'pressure' in features.columns:
            features['humidity_pressure_ratio'] = features['humidity'] / features['pressure']
        
        if 'wind_speed' in features.columns:
            features['wind_speed_log'] = np.log1p(features['wind_speed'])
        
        # Selecionar features numéricas relevantes
        numeric_features = [
            'month_sin', 'month_cos', 'day_sin', 'day_cos',
            'humidity', 'pressure', 'wind_speed', 'humidity_pressure_ratio',
            'wind_speed_log'
        ]
        
        # Filtrar apenas features que existem
        available_features = [col for col in numeric_features if col in features.columns]
        
        return features[available_features]
    
    def train(self, df: pd.DataFrame, target_col: str = 'temperature') -> Dict[str, float]:
        """
        Treina o modelo de previsão de temperatura.
        
        Args:
            df: DataFrame com dados de treinamento
            target_col: Nome da coluna target
            
        Returns:
            Dicionário com métricas de performance
        """
        try:
            # Preparar features
            X = self.prepare_features(df)
            y = df[target_col]
            
            # Remover linhas com valores ausentes
            mask = ~(X.isnull().any(axis=1) | y.isnull())
            X = X[mask]
            y = y[mask]
            
            if len(X) < 10:
                raise ValueError("Dados insuficientes para treinamento")
            
            # Normalizar features
            X_scaled = self.scaler.fit_transform(X)
            
            # Configurar modelo
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
            
            # Treinar modelo
            self.model.fit(X_scaled, y)
            
            # Validação cruzada
            cv_scores = cross_val_score(self.model, X_scaled, y, cv=5, 
                                      scoring='neg_mean_squared_error')
            
            # Previsões para métricas
            y_pred = self.model.predict(X_scaled)
            
            # Métricas
            metrics = {
                'mse': mean_squared_error(y, y_pred),
                'rmse': np.sqrt(mean_squared_error(y, y_pred)),
                'r2': r2_score(y, y_pred),
                'cv_rmse_mean': np.sqrt(-cv_scores.mean()),
                'cv_rmse_std': np.sqrt(cv_scores.std())
            }
            
            self.feature_names = X.columns.tolist()
            self.is_trained = True
            
            logger.info(f"Modelo treinado com sucesso. R²: {metrics['r2']:.3f}")
            
            return metrics
        
        except Exception as e:
            logger.error(f"Erro no treinamento do modelo: {e}")
            raise
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Faz previsões de temperatura.
        
        Args:
            df: DataFrame com dados para previsão
            
        Returns:
            Array com previsões
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado")
        
        X = self.prepare_features(df)
        X = X[self.feature_names]  # Garantir mesma ordem de features
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict(X_scaled)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Retorna importância das features.
        
        Returns:
            DataFrame com importância das features
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def save_model(self, path: str):
        """Salva o modelo treinado."""
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Modelo salvo em: {path}")
    
    def load_model(self, path: str):
        """Carrega modelo treinado."""
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Modelo carregado de: {path}")
        
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise

class AirQualityClassifier:
    """Classificador para qualidade do ar baseado em condições meteorológicas."""
    
    def __init__(self):
        """Inicializa o classificador de qualidade do ar."""
        self.categories = {
            "Boa": (0, 50),
            "Moderada": (51, 100),
            "Insalubre para grupos sensíveis": (101, 150),
            "Insalubre": (151, 200),
            "Muito insalubre": (201, 300),
            "Perigosa": (301, 500)
        }
    
    def classify_aqi(self, aqi_value: float) -> Dict[str, str]:
        """
        Classifica valor AQI em categoria.
        
        Args:
            aqi_value: Valor do índice AQI
            
        Returns:
            Dicionário com categoria e informações
        """
        for category, (min_val, max_val) in self.categories.items():
            if min_val <= aqi_value <= max_val:
                return {
                    "category": category,
                    "range": f"{min_val}-{max_val}",
                    "level": self._get_alert_level(category)
                }
        
        return {
            "category": "Valor inválido",
            "range": "N/A",
            "level": "unknown"
        }
    
    def _get_alert_level(self, category: str) -> str:
        """Retorna nível de alerta baseado na categoria."""
        alert_levels = {
            "Boa": "safe",
            "Moderada": "caution",
            "Insalubre para grupos sensíveis": "warning",
            "Insalubre": "danger",
            "Muito insalubre": "danger",
            "Perigosa": "emergency"
        }
        return alert_levels.get(category, "unknown")

def create_temperature_forecast(historical_data: pd.DataFrame, 
                              days_ahead: int = 7) -> pd.DataFrame:
    """
    Cria previsão de temperatura para os próximos dias.
    
    Args:
        historical_data: Dados históricos
        days_ahead: Número de dias para prever
        
    Returns:
        DataFrame com previsões
    """
    if historical_data.empty:
        return pd.DataFrame()
    
    # Criar modelo e treinar
    model = TemperaturePredictionModel()
    
    try:
        metrics = model.train(historical_data)
        logger.info(f"Modelo treinado para previsão. R²: {metrics['r2']:.3f}")
        
        # Criar datas futuras
        last_date = pd.to_datetime(historical_data['timestamp']).max()
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=days_ahead,
            freq='D'
        )
        
        # Criar DataFrame para previsão (baseado em médias históricas)
        last_week_data = historical_data.tail(7)
        
        forecast_data = []
        for date in future_dates:
            # Usar médias dos últimos dados como base
            avg_humidity = last_week_data['humidity'].mean() if 'humidity' in last_week_data.columns else 60
            avg_pressure = last_week_data['pressure'].mean() if 'pressure' in last_week_data.columns else 1013
            avg_wind = last_week_data['wind_speed'].mean() if 'wind_speed' in last_week_data.columns else 5
            
            forecast_data.append({
                'timestamp': date,
                'humidity': avg_humidity,
                'pressure': avg_pressure,
                'wind_speed': avg_wind
            })
        
        forecast_df = pd.DataFrame(forecast_data)
        
        # Fazer previsões
        predictions = model.predict(forecast_df)
        forecast_df['predicted_temperature'] = predictions
        
        # Adicionar intervalo de confiança (simulado)
        forecast_df['temp_lower'] = predictions - 2
        forecast_df['temp_upper'] = predictions + 2
        
        return forecast_df[['timestamp', 'predicted_temperature', 'temp_lower', 'temp_upper']]
    
    except Exception as e:
        logger.error(f"Erro na criação de previsão: {e}")
        return pd.DataFrame()
