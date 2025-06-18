"""
Cliente para integração com a API do AirVisual.
Fornece dados de qualidade do ar e poluição.
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from config.settings import Config

logger = logging.getLogger(__name__)

class AirQualityClient:
    """Cliente para API do AirVisual (IQAir)."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente AirVisual.
        
        Args:
            api_key: Chave da API. Se não fornecida, usa a configuração.
        """
        self.api_key = api_key or Config.AIRVISUAL_API_KEY
        self.base_url = Config.AIRVISUAL_BASE_URL
        self.session = requests.Session()
        
        if not self.api_key:
            raise ValueError("API key do AirVisual não configurada")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz requisição para a API.
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Resposta JSON da API
        """
        params["key"] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] != "success":
                raise requests.RequestException(f"API retornou erro: {data}")
            
            return data["data"]
        except requests.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {e}")
            raise
    
    def get_air_quality_by_city(self, city: str, state: str, country: str) -> Dict[str, Any]:
        """
        Obtém qualidade do ar por cidade.
        
        Args:
            city: Nome da cidade
            state: Estado/província
            country: País
            
        Returns:
            Dados de qualidade do ar
        """
        params = {
            "city": city,
            "state": state,
            "country": country
        }
        
        data = self._make_request("city", params)
        return self._process_air_quality_data(data)
    
    def get_air_quality_by_coords(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Obtém qualidade do ar por coordenadas.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dados de qualidade do ar
        """
        params = {
            "lat": lat,
            "lon": lon
        }
        
        data = self._make_request("nearest_city", params)
        return self._process_air_quality_data(data)
    
    def get_countries(self) -> List[str]:
        """
        Obtém lista de países disponíveis.
        
        Returns:
            Lista de países
        """
        data = self._make_request("countries", {})
        return [country["country"] for country in data]
    
    def get_states(self, country: str) -> List[str]:
        """
        Obtém lista de estados/províncias para um país.
        
        Args:
            country: País
            
        Returns:
            Lista de estados
        """
        params = {"country": country}
        data = self._make_request("states", params)
        return [state["state"] for state in data]
    
    def get_cities(self, country: str, state: str) -> List[str]:
        """
        Obtém lista de cidades para um estado.
        
        Args:
            country: País
            state: Estado
            
        Returns:
            Lista de cidades
        """
        params = {
            "country": country,
            "state": state
        }
        data = self._make_request("cities", params)
        return [city["city"] for city in data]
    
    def _process_air_quality_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados de qualidade do ar.
        
        Args:
            data: Dados brutos da API
            
        Returns:
            Dados processados e padronizados
        """
        current = data["current"]
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": {
                "city": data["city"],
                "state": data["state"],
                "country": data["country"],
                "lat": data["location"]["coordinates"][1],
                "lon": data["location"]["coordinates"][0]
            },
            "air_quality": {
                "aqi_us": current["pollution"]["aqius"],
                "main_pollutant_us": current["pollution"]["mainus"],
                "aqi_cn": current["pollution"]["aqicn"],
                "main_pollutant_cn": current["pollution"]["maincn"],
            },
            "weather": {
                "temperature": current["weather"]["tp"],
                "pressure": current["weather"]["pr"],
                "humidity": current["weather"]["hu"],
                "wind_speed": current["weather"]["ws"],
                "wind_direction": current["weather"]["wd"],
                "icon": current["weather"]["ic"]
            }
        }
    
    @staticmethod
    def get_aqi_category(aqi: int) -> Dict[str, str]:
        """
        Retorna categoria e cor para um valor de AQI.
        
        Args:
            aqi: Valor do AQI
            
        Returns:
            Dicionário com categoria, cor e descrição
        """
        if aqi <= 50:
            return {
                "category": "Boa",
                "color": "#00e400",
                "description": "Qualidade do ar satisfatória, sem riscos"
            }
        elif aqi <= 100:
            return {
                "category": "Moderada",
                "color": "#ffff00",
                "description": "Aceitável para a maioria das pessoas"
            }
        elif aqi <= 150:
            return {
                "category": "Insalubre para grupos sensíveis",
                "color": "#ff7e00",
                "description": "Pessoas sensíveis podem ter sintomas"
            }
        elif aqi <= 200:
            return {
                "category": "Insalubre",
                "color": "#ff0000",
                "description": "Todos podem começar a ter problemas de saúde"
            }
        elif aqi <= 300:
            return {
                "category": "Muito insalubre",
                "color": "#8f3f97",
                "description": "Alerta de saúde, todos podem ser afetados"
            }
        else:
            return {
                "category": "Perigosa",
                "color": "#7e0023",
                "description": "Emergência de saúde, população inteira afetada"
            }
