"""
Sistema avançado de alertas climáticos e de qualidade do ar.
Detecta padrões anômalos e condições críticas em tempo real.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sqlite3
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Níveis de alerta."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertType(Enum):
    """Tipos de alerta."""
    AIR_QUALITY = "air_quality"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WIND = "wind"
    PRESSURE = "pressure"
    TREND_ANOMALY = "trend_anomaly"

@dataclass
class Alert:
    """Estrutura de um alerta."""
    id: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    description: str
    location: str
    value: float
    threshold: float
    timestamp: datetime
    recommendations: List[str]
    expires_at: Optional[datetime] = None

class ClimateAlertSystem:
    """Sistema inteligente de alertas climáticos."""
    
    def __init__(self, db_path: str):
        """
        Inicializa o sistema de alertas.
        
        Args:
            db_path: Caminho para o banco de dados
        """
        self.db_path = db_path
        self.active_alerts: List[Alert] = []
        
        # Thresholds configuráveis
        self.thresholds = {
            "aqi_moderate": 51,
            "aqi_unhealthy_sensitive": 101,
            "aqi_unhealthy": 151,
            "aqi_very_unhealthy": 201,
            "aqi_hazardous": 301,
            "temp_extreme_low": -10,
            "temp_extreme_high": 40,
            "humidity_very_low": 20,
            "humidity_very_high": 90,
            "wind_strong": 15,  # m/s
            "wind_extreme": 25,  # m/s
            "pressure_very_low": 980,  # hPa
            "pressure_very_high": 1030,  # hPa
        }
    
    def analyze_current_conditions(self, location: str = None) -> List[Alert]:
        """
        Analisa condições atuais e gera alertas.
        
        Args:
            location: Localização específica (opcional)
            
        Returns:
            Lista de alertas ativos
        """
        alerts = []
        
        try:
            # Busca dados mais recentes
            latest_data = self._get_latest_data(location)
            
            if not latest_data:
                return alerts
            
            # Análise de qualidade do ar
            air_alerts = self._analyze_air_quality(latest_data)
            alerts.extend(air_alerts)
            
            # Análise meteorológica
            weather_alerts = self._analyze_weather_conditions(latest_data)
            alerts.extend(weather_alerts)
            
            # Análise de tendências
            trend_alerts = self._analyze_trends(location)
            alerts.extend(trend_alerts)
            
            self.active_alerts = alerts
            logger.info(f"Gerados {len(alerts)} alertas para análise atual")
            
        except Exception as e:
            logger.error(f"Erro na análise de condições: {e}")
        
        return alerts
    
    def _analyze_air_quality(self, data: Dict) -> List[Alert]:
        """Analisa condições de qualidade do ar."""
        alerts = []
        
        if 'aqi_us' not in data or not data['aqi_us']:
            return alerts
        
        aqi = data['aqi_us']
        location = f"{data.get('city', 'Local')}, {data.get('country', '')}"
        
        recommendations = {
            "moderate": [
                "Pessoas sensíveis devem considerar reduzir atividades ao ar livre",
                "Monitore sintomas se você tem problemas respiratórios"
            ],
            "unhealthy_sensitive": [
                "Pessoas com doenças cardíacas ou pulmonares devem evitar atividades externas",
                "Idosos e crianças devem limitar tempo ao ar livre",
                "Use máscaras de proteção se necessário sair"
            ],
            "unhealthy": [
                "Todos devem evitar atividades ao ar livre prolongadas",
                "Use máscaras de proteção N95 ou superiores",
                "Mantenha janelas fechadas e use purificadores de ar"
            ],
            "very_unhealthy": [
                "Evite todas as atividades ao ar livre",
                "Pessoas sensíveis devem permanecer em ambientes fechados",
                "Procure atendimento médico se sentir sintomas respiratórios"
            ],
            "hazardous": [
                "EMERGÊNCIA: Evite completamente exposição ao ar livre",
                "Procure abrigo em ambiente fechado imediatamente",
                "Contate serviços de emergência se necessário"
            ]
        }
        
        if aqi >= self.thresholds["aqi_hazardous"]:
            alerts.append(Alert(
                id=f"aqi_hazardous_{int(datetime.now().timestamp())}",
                alert_type=AlertType.AIR_QUALITY,
                level=AlertLevel.EMERGENCY,
                title="🚨 QUALIDADE DO AR PERIGOSA",
                description=f"Índice de qualidade do ar extremamente alto: {aqi}",
                location=location,
                value=aqi,
                threshold=self.thresholds["aqi_hazardous"],
                timestamp=datetime.now(),
                recommendations=recommendations["hazardous"]
            ))
        elif aqi >= self.thresholds["aqi_very_unhealthy"]:
            alerts.append(Alert(
                id=f"aqi_very_unhealthy_{int(datetime.now().timestamp())}",
                alert_type=AlertType.AIR_QUALITY,
                level=AlertLevel.CRITICAL,
                title="⚠️ QUALIDADE DO AR MUITO PREJUDICIAL",
                description=f"Qualidade do ar muito prejudicial à saúde: {aqi}",
                location=location,
                value=aqi,
                threshold=self.thresholds["aqi_very_unhealthy"],
                timestamp=datetime.now(),
                recommendations=recommendations["very_unhealthy"]
            ))
        elif aqi >= self.thresholds["aqi_unhealthy"]:
            alerts.append(Alert(
                id=f"aqi_unhealthy_{int(datetime.now().timestamp())}",
                alert_type=AlertType.AIR_QUALITY,
                level=AlertLevel.CRITICAL,
                title="⚠️ QUALIDADE DO AR PREJUDICIAL",
                description=f"Qualidade do ar prejudicial à saúde: {aqi}",
                location=location,
                value=aqi,
                threshold=self.thresholds["aqi_unhealthy"],
                timestamp=datetime.now(),
                recommendations=recommendations["unhealthy"]
            ))
        elif aqi >= self.thresholds["aqi_unhealthy_sensitive"]:
            alerts.append(Alert(
                id=f"aqi_unhealthy_sensitive_{int(datetime.now().timestamp())}",
                alert_type=AlertType.AIR_QUALITY,
                level=AlertLevel.WARNING,
                title="⚠️ QUALIDADE DO AR PREJUDICIAL PARA GRUPOS SENSÍVEIS",
                description=f"Qualidade do ar pode afetar pessoas sensíveis: {aqi}",
                location=location,
                value=aqi,
                threshold=self.thresholds["aqi_unhealthy_sensitive"],
                timestamp=datetime.now(),
                recommendations=recommendations["unhealthy_sensitive"]
            ))
        elif aqi >= self.thresholds["aqi_moderate"]:
            alerts.append(Alert(
                id=f"aqi_moderate_{int(datetime.now().timestamp())}",
                alert_type=AlertType.AIR_QUALITY,
                level=AlertLevel.INFO,
                title="ℹ️ QUALIDADE DO AR MODERADA",
                description=f"Qualidade do ar aceitável para a maioria: {aqi}",
                location=location,
                value=aqi,
                threshold=self.thresholds["aqi_moderate"],
                timestamp=datetime.now(),
                recommendations=recommendations["moderate"]
            ))
        
        return alerts
    
    def _analyze_weather_conditions(self, data: Dict) -> List[Alert]:
        """Analisa condições meteorológicas extremas."""
        alerts = []
        location = f"{data.get('city', 'Local')}, {data.get('country', '')}"
        
        # Análise de temperatura
        if 'temperature' in data and data['temperature'] is not None:
            temp = data['temperature']
            
            if temp >= self.thresholds["temp_extreme_high"]:
                alerts.append(Alert(
                    id=f"temp_high_{int(datetime.now().timestamp())}",
                    alert_type=AlertType.TEMPERATURE,
                    level=AlertLevel.WARNING,
                    title="🌡️ TEMPERATURA EXTREMAMENTE ALTA",
                    description=f"Temperatura muito alta: {temp}°C",
                    location=location,
                    value=temp,
                    threshold=self.thresholds["temp_extreme_high"],
                    timestamp=datetime.now(),
                    recommendations=[
                        "Evite exposição prolongada ao sol",
                        "Mantenha-se hidratado",
                        "Use roupas leves e protetor solar",
                        "Procure ambientes climatizados"
                    ]
                ))
            elif temp <= self.thresholds["temp_extreme_low"]:
                alerts.append(Alert(
                    id=f"temp_low_{int(datetime.now().timestamp())}",
                    alert_type=AlertType.TEMPERATURE,
                    level=AlertLevel.WARNING,
                    title="🧊 TEMPERATURA EXTREMAMENTE BAIXA",
                    description=f"Temperatura muito baixa: {temp}°C",
                    location=location,
                    value=temp,
                    threshold=self.thresholds["temp_extreme_low"],
                    timestamp=datetime.now(),
                    recommendations=[
                        "Use roupas adequadas para o frio",
                        "Evite exposição prolongada",
                        "Proteja extremidades do corpo",
                        "Mantenha-se aquecido"
                    ]
                ))
        
        # Análise de vento
        if 'wind_speed' in data and data['wind_speed'] is not None:
            wind = data['wind_speed']
            
            if wind >= self.thresholds["wind_extreme"]:
                alerts.append(Alert(
                    id=f"wind_extreme_{int(datetime.now().timestamp())}",
                    alert_type=AlertType.WIND,
                    level=AlertLevel.CRITICAL,
                    title="💨 VENTOS EXTREMOS",
                    description=f"Ventos muito fortes: {wind} m/s",
                    location=location,
                    value=wind,
                    threshold=self.thresholds["wind_extreme"],
                    timestamp=datetime.now(),
                    recommendations=[
                        "Evite atividades ao ar livre",
                        "Cuidado com objetos que podem voar",
                        "Evite áreas com árvores ou estruturas altas",
                        "Dirija com extrema cautela"
                    ]
                ))
            elif wind >= self.thresholds["wind_strong"]:
                alerts.append(Alert(
                    id=f"wind_strong_{int(datetime.now().timestamp())}",
                    alert_type=AlertType.WIND,
                    level=AlertLevel.WARNING,
                    title="💨 VENTOS FORTES",
                    description=f"Ventos fortes: {wind} m/s",
                    location=location,
                    value=wind,
                    threshold=self.thresholds["wind_strong"],
                    timestamp=datetime.now(),
                    recommendations=[
                        "Tenha cuidado ao caminhar",
                        "Dirija com atenção",
                        "Fixe objetos soltos"
                    ]
                ))
        
        return alerts
    
    def _analyze_trends(self, location: str = None) -> List[Alert]:
        """Analisa tendências e detecta anomalias."""
        alerts = []
        
        try:
            # Busca dados históricos para análise de tendência
            historical_data = self._get_historical_data(location, days=7)
            
            if len(historical_data) < 5:  # Dados insuficientes
                return alerts
            
            df = pd.DataFrame(historical_data)
            
            # Análise de tendência de AQI
            if 'aqi_us' in df.columns:
                aqi_trend = self._calculate_trend(df['aqi_us'].dropna())
                if aqi_trend > 20:  # Piora significativa
                    alerts.append(Alert(
                        id=f"aqi_trend_{int(datetime.now().timestamp())}",
                        alert_type=AlertType.TREND_ANOMALY,
                        level=AlertLevel.WARNING,
                        title="📈 TENDÊNCIA DE PIORA NA QUALIDADE DO AR",
                        description=f"Qualidade do ar tem piorado consistentemente (+{aqi_trend:.1f} pontos)",
                        location=location or "Geral",
                        value=aqi_trend,
                        threshold=20,
                        timestamp=datetime.now(),
                        recommendations=[
                            "Monitore mais de perto a qualidade do ar",
                            "Considere ajustar atividades ao ar livre",
                            "Verifique previsões meteorológicas"
                        ]
                    ))
            
        except Exception as e:
            logger.error(f"Erro na análise de tendências: {e}")
        
        return alerts
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calcula tendência linear de uma série temporal."""
        if len(series) < 2:
            return 0
        
        x = np.arange(len(series))
        z = np.polyfit(x, series, 1)
        return z[0] * len(series)  # Tendência total no período
    
    def _get_latest_data(self, location: str = None) -> Dict:
        """Busca dados mais recentes do banco."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Query para dados mais recentes
                query = """
                    SELECT w.city, w.country, w.temperature, w.humidity, w.pressure,
                           w.wind_speed, a.aqi_us, a.main_pollutant_us
                    FROM weather_data w
                    LEFT JOIN air_quality_data a ON w.city = a.city AND w.country = a.country
                    WHERE w.timestamp = (SELECT MAX(timestamp) FROM weather_data)
                """
                
                if location:
                    query += f" AND w.city LIKE '%{location}%'"
                
                query += " LIMIT 1"
                
                cursor.execute(query)
                row = cursor.fetchone()
                
                if row:
                    return {
                        'city': row[0],
                        'country': row[1],
                        'temperature': row[2],
                        'humidity': row[3],
                        'pressure': row[4],
                        'wind_speed': row[5],
                        'aqi_us': row[6],
                        'main_pollutant_us': row[7]
                    }
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados mais recentes: {e}")
        
        return {}
    
    def _get_historical_data(self, location: str = None, days: int = 7) -> List[Dict]:
        """Busca dados históricos para análise de tendências."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                query = """
                    SELECT w.timestamp, w.city, w.country, w.temperature, 
                           w.humidity, w.pressure, w.wind_speed, a.aqi_us
                    FROM weather_data w
                    LEFT JOIN air_quality_data a ON w.city = a.city 
                        AND w.country = a.country 
                        AND date(w.timestamp) = date(a.timestamp)
                    WHERE datetime(w.timestamp) >= ?
                """
                
                params = [cutoff_date.isoformat()]
                
                if location:
                    query += " AND w.city LIKE ?"
                    params.append(f"%{location}%")
                
                query += " ORDER BY w.timestamp"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [
                    {
                        'timestamp': row[0],
                        'city': row[1],
                        'country': row[2],
                        'temperature': row[3],
                        'humidity': row[4],
                        'pressure': row[5],
                        'wind_speed': row[6],
                        'aqi_us': row[7]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados históricos: {e}")
        
        return []
    
    def get_alerts_summary(self) -> Dict:
        """Retorna resumo dos alertas por nível e tipo."""
        summary = {
            "total": len(self.active_alerts),
            "by_level": {},
            "by_type": {},
            "critical_count": 0
        }
        
        for alert in self.active_alerts:
            # Por nível
            level = alert.level.value
            summary["by_level"][level] = summary["by_level"].get(level, 0) + 1
            
            # Por tipo
            alert_type = alert.alert_type.value
            summary["by_type"][alert_type] = summary["by_type"].get(alert_type, 0) + 1
            
            # Críticos
            if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
                summary["critical_count"] += 1
        
        return summary
    
    def export_alerts_to_json(self) -> str:
        """Exporta alertas para JSON."""
        import json
        
        alerts_data = []
        for alert in self.active_alerts:
            alerts_data.append({
                "id": alert.id,
                "type": alert.alert_type.value,
                "level": alert.level.value,
                "title": alert.title,
                "description": alert.description,
                "location": alert.location,
                "value": alert.value,
                "threshold": alert.threshold,
                "timestamp": alert.timestamp.isoformat(),
                "recommendations": alert.recommendations
            })
        
        return json.dumps(alerts_data, indent=2, ensure_ascii=False)
