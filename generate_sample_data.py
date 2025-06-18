"""
Script para gerar dados simulados para demonstração do projeto.
Cria dados realistas de temperatura, umidade e qualidade do ar.
"""
import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config

def generate_sample_data():
    """Gera dados simulados para demonstração."""
    
    # Configurar período de dados (último ano)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Gerar datas
    dates = pd.date_range(start=start_date, end=end_date, freq='6H')  # Dados de 6 em 6 horas
    
    print(f"📊 Gerando {len(dates)} registros de dados simulados...")
    
    # Dados meteorológicos simulados com padrões sazonais
    weather_data = []
    air_quality_data = []
    
    for i, date in enumerate(dates):
        # Padrão sazonal para São Paulo
        day_of_year = date.timetuple().tm_yday
        
        # Temperatura com variação sazonal (verão quente, inverno ameno)
        base_temp = 20 + 8 * np.sin((day_of_year - 80) * 2 * np.pi / 365)  # Pico no verão
        temp_variation = np.random.normal(0, 3)  # Variação diária
        hour_variation = 5 * np.sin((date.hour - 14) * np.pi / 12)  # Pico às 14h
        temperature = base_temp + temp_variation + hour_variation
        
        # Umidade (maior no verão)
        base_humidity = 65 + 15 * np.sin((day_of_year - 80) * 2 * np.pi / 365)
        humidity = max(30, min(95, base_humidity + np.random.normal(0, 10)))
        
        # Pressão atmosférica
        pressure = 1013 + np.random.normal(0, 15)
        
        # Vento
        wind_speed = max(0, np.random.exponential(4))
        wind_direction = np.random.uniform(0, 360)
        
        # Visibilidade
        visibility = max(1, np.random.normal(15, 5))
        
        # Nuvens
        clouds = np.random.uniform(0, 100)
        
        # Dados meteorológicos
        weather_record = {
            'timestamp': date.isoformat(),
            'city': 'São Paulo',
            'country': 'BR',
            'lat': -23.5505,
            'lon': -46.6333,
            'temperature': round(temperature, 1),
            'feels_like': round(temperature + np.random.normal(0, 2), 1),
            'humidity': int(humidity),
            'pressure': int(pressure),
            'description': _get_weather_description(temperature, humidity, clouds),
            'wind_speed': round(wind_speed, 1),
            'wind_direction': int(wind_direction),
            'visibility': round(visibility, 1),
            'clouds': int(clouds),
            'raw_data': json.dumps({'simulated': True})
        }
        weather_data.append(weather_record)
        
        # Dados de qualidade do ar (a cada 12 horas)
        if i % 2 == 0:
            # AQI baseado em condições meteorológicas e sazonalidade
            base_aqi = 40 + 30 * np.sin((day_of_year - 120) * 2 * np.pi / 365)  # Pior no inverno seco
            weather_factor = (100 - humidity) / 100 * 20  # Pior com baixa umidade
            wind_factor = max(0, (5 - wind_speed) / 5 * 15)  # Pior com pouco vento
            aqi = max(20, min(200, base_aqi + weather_factor + wind_factor + np.random.normal(0, 15)))
            
            air_record = {
                'timestamp': date.isoformat(),
                'city': 'São Paulo',
                'state': 'São Paulo',
                'country': 'BR',
                'lat': -23.5505,
                'lon': -46.6333,
                'aqi_us': int(aqi),
                'main_pollutant_us': _get_main_pollutant(aqi),
                'aqi_cn': int(aqi * 0.8),  # Escala chinesa ligeiramente diferente
                'main_pollutant_cn': _get_main_pollutant(aqi * 0.8),
                'temperature': round(temperature, 1),
                'pressure': int(pressure),
                'humidity': int(humidity),
                'wind_speed': round(wind_speed, 1),
                'wind_direction': int(wind_direction),
                'raw_data': json.dumps({'simulated': True})
            }
            air_quality_data.append(air_record)
    
    return weather_data, air_quality_data

def _get_weather_description(temp, humidity, clouds):
    """Gera descrição do tempo baseada nas condições."""
    if temp > 30:
        if humidity > 70:
            return "quente e úmido"
        else:
            return "quente e seco"
    elif temp > 20:
        if clouds > 70:
            return "nublado"
        elif humidity > 80:
            return "parcialmente nublado"
        else:
            return "ensolarado"
    else:
        if clouds > 70:
            return "frio e nublado"
        else:
            return "frio"

def _get_main_pollutant(aqi):
    """Retorna poluente principal baseado no AQI."""
    if aqi > 100:
        return "pm25"  # Material particulado fino
    elif aqi > 80:
        return "pm10"  # Material particulado
    elif aqi > 60:
        return "o3"    # Ozônio
    else:
        return "no2"   # Dióxido de nitrogênio

def save_to_database(weather_data, air_quality_data):
    """Salva dados simulados no banco."""
    Config.ensure_directories()
    
    try:
        with sqlite3.connect(Config.DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Limpar dados existentes
            cursor.execute("DELETE FROM weather_data WHERE raw_data LIKE '%simulated%'")
            cursor.execute("DELETE FROM air_quality_data WHERE raw_data LIKE '%simulated%'")
            
            # Inserir dados meteorológicos
            for record in weather_data:
                cursor.execute("""
                    INSERT INTO weather_data (
                        timestamp, city, country, lat, lon,
                        temperature, feels_like, humidity, pressure, description,
                        wind_speed, wind_direction, visibility, clouds, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record['timestamp'], record['city'], record['country'],
                    record['lat'], record['lon'], record['temperature'],
                    record['feels_like'], record['humidity'], record['pressure'],
                    record['description'], record['wind_speed'], record['wind_direction'],
                    record['visibility'], record['clouds'], record['raw_data']
                ))
            
            # Inserir dados de qualidade do ar
            for record in air_quality_data:
                cursor.execute("""
                    INSERT INTO air_quality_data (
                        timestamp, city, state, country, lat, lon,
                        aqi_us, main_pollutant_us, aqi_cn, main_pollutant_cn,
                        temperature, pressure, humidity, wind_speed, wind_direction, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record['timestamp'], record['city'], record['state'],
                    record['country'], record['lat'], record['lon'],
                    record['aqi_us'], record['main_pollutant_us'],
                    record['aqi_cn'], record['main_pollutant_cn'],
                    record['temperature'], record['pressure'], record['humidity'],
                    record['wind_speed'], record['wind_direction'], record['raw_data']
                ))
            
            conn.commit()
            
            print(f"✅ Dados salvos com sucesso!")
            print(f"📊 Registros meteorológicos: {len(weather_data)}")
            print(f"💨 Registros de qualidade do ar: {len(air_quality_data)}")
    
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
        raise

def main():
    """Função principal."""
    print("🔄 Gerando dados simulados para demonstração...")
    
    # Gerar dados
    weather_data, air_quality_data = generate_sample_data()
    
    # Salvar no banco
    save_to_database(weather_data, air_quality_data)
    
    print("✅ Dados de demonstração criados com sucesso!")
    print("🚀 Agora você pode executar o dashboard: streamlit run src/dashboard/app.py")

if __name__ == "__main__":
    main()
