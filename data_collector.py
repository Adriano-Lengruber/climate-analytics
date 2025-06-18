"""
Script principal para coleta de dados meteorológicos e de qualidade do ar.
Executa coleta automatizada e armazena os dados em banco local.
"""
import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config
from src.api.weather_api import OpenWeatherClient
from src.api.air_quality_api import AirQualityClient

# Configuração de logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCollector:
    """Coletor de dados climáticos e de qualidade do ar."""
    
    def __init__(self):
        """Inicializa o coletor de dados."""
        Config.ensure_directories()
        self.db_path = Config.DATABASE_PATH
        self.init_database()
        
        # Inicializa clientes de API
        self.weather_client = None
        self.air_client = None
        
        try:
            if Config.OPENWEATHER_API_KEY:
                self.weather_client = OpenWeatherClient()
                logger.info("Cliente OpenWeather inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente OpenWeather: {e}")
        
        try:
            if Config.AIRVISUAL_API_KEY:
                self.air_client = AirQualityClient()
                logger.info("Cliente AirVisual inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente AirVisual: {e}")
    
    def init_database(self):
        """Inicializa o banco de dados SQLite."""
        try:
            # Garante que o diretório existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de dados meteorológicos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        city TEXT NOT NULL,
                        country TEXT NOT NULL,
                        lat REAL NOT NULL,
                        lon REAL NOT NULL,
                        temperature REAL,
                        feels_like REAL,
                        humidity INTEGER,
                        pressure INTEGER,
                        description TEXT,
                        wind_speed REAL,
                        wind_direction REAL,
                        visibility REAL,
                        clouds INTEGER,
                        raw_data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de dados de qualidade do ar
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS air_quality_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        city TEXT NOT NULL,
                        state TEXT,
                        country TEXT NOT NULL,
                        lat REAL NOT NULL,
                        lon REAL NOT NULL,
                        aqi_us INTEGER,
                        main_pollutant_us TEXT,
                        aqi_cn INTEGER,
                        main_pollutant_cn TEXT,
                        temperature REAL,
                        pressure INTEGER,
                        humidity INTEGER,
                        wind_speed REAL,
                        wind_direction REAL,
                        raw_data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_data(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_weather_location ON weather_data(city, country)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_air_timestamp ON air_quality_data(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_air_location ON air_quality_data(city, country)")
                
                conn.commit()
                logger.info("Banco de dados inicializado com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def collect_weather_data(self, city: str = None, country: str = None):
        """
        Coleta dados meteorológicos para uma cidade.
        
        Args:
            city: Nome da cidade (usa padrão se não fornecido)
            country: Código do país (usa padrão se não fornecido)
        """
        if not self.weather_client:
            logger.warning("Cliente OpenWeather não disponível")
            return
        
        city = city or Config.DEFAULT_CITY
        country = country or Config.DEFAULT_COUNTRY
        
        try:
            logger.info(f"Coletando dados meteorológicos para {city}, {country}")
            data = self.weather_client.get_current_weather(city, country)
            
            self._save_weather_data(data)
            logger.info(f"Dados meteorológicos salvos para {city}, {country}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados meteorológicos: {e}")
    
    def collect_air_quality_data(self, lat: float = None, lon: float = None):
        """
        Coleta dados de qualidade do ar para coordenadas.
        
        Args:
            lat: Latitude (usa padrão se não fornecido)
            lon: Longitude (usa padrão se não fornecido)
        """
        if not self.air_client:
            logger.warning("Cliente AirVisual não disponível")
            return
        
        lat = lat or Config.DEFAULT_LAT
        lon = lon or Config.DEFAULT_LON
        
        try:
            logger.info(f"Coletando dados de qualidade do ar para {lat}, {lon}")
            data = self.air_client.get_air_quality_by_coords(lat, lon)
            
            self._save_air_quality_data(data)
            logger.info(f"Dados de qualidade do ar salvos para {lat}, {lon}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados de qualidade do ar: {e}")
    
    def _save_weather_data(self, data: dict):
        """Salva dados meteorológicos no banco."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO weather_data (
                        timestamp, city, country, lat, lon,
                        temperature, feels_like, humidity, pressure, description,
                        wind_speed, wind_direction, visibility, clouds, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['timestamp'],
                    data['location']['city'],
                    data['location']['country'],
                    data['location']['lat'],
                    data['location']['lon'],
                    data['weather']['temperature'],
                    data['weather']['feels_like'],
                    data['weather']['humidity'],
                    data['weather']['pressure'],
                    data['weather']['description'],
                    data['wind']['speed'],
                    data['wind']['direction'],
                    data['visibility'],
                    data['clouds'],
                    json.dumps(data)
                ))
                conn.commit()
        
        except Exception as e:
            logger.error(f"Erro ao salvar dados meteorológicos: {e}")
            raise
    
    def _save_air_quality_data(self, data: dict):
        """Salva dados de qualidade do ar no banco."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO air_quality_data (
                        timestamp, city, state, country, lat, lon,
                        aqi_us, main_pollutant_us, aqi_cn, main_pollutant_cn,
                        temperature, pressure, humidity, wind_speed, wind_direction, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['timestamp'],
                    data['location']['city'],
                    data['location'].get('state'),
                    data['location']['country'],
                    data['location']['lat'],
                    data['location']['lon'],
                    data['air_quality']['aqi_us'],
                    data['air_quality']['main_pollutant_us'],
                    data['air_quality']['aqi_cn'],
                    data['air_quality']['main_pollutant_cn'],
                    data['weather']['temperature'],
                    data['weather']['pressure'],
                    data['weather']['humidity'],
                    data['weather']['wind_speed'],
                    data['weather']['wind_direction'],
                    json.dumps(data)
                ))
                conn.commit()
        
        except Exception as e:
            logger.error(f"Erro ao salvar dados de qualidade do ar: {e}")
            raise
    
    def collect_all_data(self):
        """Coleta todos os tipos de dados."""
        logger.info("Iniciando coleta completa de dados")
        
        # Coleta dados meteorológicos
        self.collect_weather_data()
        
        # Coleta dados de qualidade do ar
        self.collect_air_quality_data()
        
        logger.info("Coleta completa finalizada")

def main():
    """Função principal."""
    try:
        collector = DataCollector()
        collector.collect_all_data()
        
    except Exception as e:
        logger.error(f"Erro na execução principal: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
