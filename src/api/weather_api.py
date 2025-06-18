"""
Cliente para integração com a API do OpenWeatherMap.
Fornece dados meteorológicos atuais, previsões e dados históricos.
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from config.settings import Config

logger = logging.getLogger(__name__)

class OpenWeatherClient:
    """Cliente para API do OpenWeatherMap."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente OpenWeather.
        
        Args:
            api_key: Chave da API. Se não fornecida, usa a configuração.
        """
        self.api_key = api_key or Config.OPENWEATHER_API_KEY
        self.base_url = Config.OPENWEATHER_BASE_URL
        self.session = requests.Session()
        
        if not self.api_key:
            raise ValueError("API key do OpenWeatherMap não configurada")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz requisição para a API.
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Resposta JSON da API
            
        Raises:
            requests.RequestException: Erro na requisição
        """
        params["appid"] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {e}")
            raise
    
    def get_current_weather(self, city: str, country: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém dados meteorológicos atuais para uma cidade.
        
        Args:
            city: Nome da cidade
            country: Código do país (opcional)
            
        Returns:
            Dados meteorológicos atuais
        """
        location = f"{city},{country}" if country else city
        params = {
            "q": location,
            "units": "metric",
            "lang": "pt_br"
        }
        
        data = self._make_request("weather", params)
        
        # Processa e padroniza os dados
        return self._process_current_weather(data)
    
    def get_current_weather_by_coords(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Obtém dados meteorológicos atuais por coordenadas.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dados meteorológicos atuais
        """
        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "lang": "pt_br"
        }
        
        data = self._make_request("weather", params)
        return self._process_current_weather(data)
    
    def get_forecast(self, city: str, country: Optional[str] = None, days: int = 5) -> List[Dict[str, Any]]:
        """
        Obtém previsão meteorológica.
        
        Args:
            city: Nome da cidade
            country: Código do país (opcional)
            days: Número de dias de previsão (máximo 5)
            
        Returns:
            Lista com previsões meteorológicas
        """
        location = f"{city},{country}" if country else city
        params = {
            "q": location,
            "units": "metric",
            "lang": "pt_br",
            "cnt": min(days * 8, 40)  # API retorna dados de 3 em 3 horas
        }
        
        data = self._make_request("forecast", params)
        return self._process_forecast(data)
    
    def _process_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados de clima atual."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": {
                "city": data["name"],
                "country": data["sys"]["country"],
                "lat": data["coord"]["lat"],
                "lon": data["coord"]["lon"]
            },
            "weather": {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "main": data["weather"][0]["main"],
                "icon": data["weather"][0]["icon"]
            },
            "wind": {
                "speed": data["wind"].get("speed", 0),
                "direction": data["wind"].get("deg", 0)
            },
            "visibility": data.get("visibility", 0) / 1000,  # Converte para km
            "clouds": data["clouds"]["all"],
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"], timezone.utc).isoformat(),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"], timezone.utc).isoformat()
        }
    
    def _process_forecast(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa dados de previsão."""
        forecasts = []
        
        for item in data["list"]:
            forecast = {
                "timestamp": datetime.fromtimestamp(item["dt"], timezone.utc).isoformat(),
                "weather": {
                    "temperature": item["main"]["temp"],
                    "temperature_min": item["main"]["temp_min"],
                    "temperature_max": item["main"]["temp_max"],
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "description": item["weather"][0]["description"],
                    "main": item["weather"][0]["main"],
                    "icon": item["weather"][0]["icon"]
                },
                "wind": {
                    "speed": item["wind"].get("speed", 0),
                    "direction": item["wind"].get("deg", 0)
                },
                "clouds": item["clouds"]["all"],
                "pop": item.get("pop", 0)  # Probabilidade de precipitação
            }
            forecasts.append(forecast)
        
        return forecasts
