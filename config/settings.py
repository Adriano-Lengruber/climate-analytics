"""
Configurações centralizadas do projeto Climate Analytics.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Classe de configuração principal."""
    
    # Diretórios do projeto
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # APIs - Carrega das variáveis de ambiente
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    AIRVISUAL_API_KEY: Optional[str] = os.getenv("AIRVISUAL_API_KEY")
    NASA_API_KEY: Optional[str] = os.getenv("NASA_API_KEY", "DEMO_KEY")
    
    # URLs das APIs
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    AIRVISUAL_BASE_URL = "https://api.airvisual.com/v2"
    NASA_BASE_URL = "https://api.nasa.gov"
    
    # Banco de dados
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/climate_data.db")
    
    # Configurações gerais
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    CACHE_DURATION_HOURS = int(os.getenv("CACHE_DURATION_HOURS", "1"))
    
    # Localização padrão
    DEFAULT_CITY = os.getenv("DEFAULT_CITY", "São Paulo")
    DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "BR")
    DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", "-23.5505"))
    DEFAULT_LON = float(os.getenv("DEFAULT_LON", "-46.6333"))
    
    # Configurações do Streamlit
    STREAMLIT_CONFIG = {
        "page_title": "Climate & Air Quality Analytics",
        "page_icon": "🌍",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Cria diretórios necessários se não existirem."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_api_keys(cls) -> dict:
        """Valida se as chaves de API estão configuradas."""
        validation = {
            "openweather": cls.OPENWEATHER_API_KEY is not None and cls.OPENWEATHER_API_KEY != "demo_key_for_testing",
            "airvisual": cls.AIRVISUAL_API_KEY is not None and cls.AIRVISUAL_API_KEY != "demo_key_for_testing",
            "nasa": cls.NASA_API_KEY is not None
        }
        return validation
    
    @classmethod
    def get_api_status(cls) -> dict:
        """Retorna status detalhado das APIs."""
        validation = cls.validate_api_keys()
        
        status = {
            "openweather": {
                "configured": validation["openweather"],
                "key_preview": cls._mask_api_key(cls.OPENWEATHER_API_KEY) if cls.OPENWEATHER_API_KEY else None
            },
            "airvisual": {
                "configured": validation["airvisual"], 
                "key_preview": cls._mask_api_key(cls.AIRVISUAL_API_KEY) if cls.AIRVISUAL_API_KEY else None
            },
            "nasa": {
                "configured": validation["nasa"],
                "key_preview": cls._mask_api_key(cls.NASA_API_KEY) if cls.NASA_API_KEY else None
            }
        }
        return status
    
    @staticmethod
    def _mask_api_key(key: str) -> str:
        """Mascara chave de API para exibição segura."""
        if not key or len(key) < 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"
