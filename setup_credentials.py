"""
Script de configuração completa do projeto Climate Analytics.
Configura credenciais seguras e testa conexões com APIs.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.credential_manager import SecureCredentialManager, setup_credentials_interactive
from src.api.weather_api import OpenWeatherClient
from src.api.air_quality_api import AirQualityClient
import requests
import json

def test_openweather_api(api_key: str) -> bool:
    """Testa conexão com OpenWeatherMap."""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": "London,UK",
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        temp = data['main']['temp']
        
        print(f"✅ OpenWeatherMap: Funcionando! (Londres: {temp}°C)")
        return True
    
    except Exception as e:
        print(f"❌ OpenWeatherMap: Erro - {str(e)[:100]}")
        return False

def test_airvisual_api(api_key: str) -> bool:
    """Testa conexão com AirVisual."""
    try:
        url = "https://api.airvisual.com/v2/city"
        params = {
            "city": "London",
            "state": "England", 
            "country": "UK",
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data["status"] == "success":
            aqi = data["data"]["current"]["pollution"]["aqius"]
            print(f"✅ AirVisual: Funcionando! (Londres AQI: {aqi})")
            return True
        else:
            print(f"❌ AirVisual: Erro na resposta - {data}")
            return False
    
    except Exception as e:
        print(f"❌ AirVisual: Erro - {str(e)[:100]}")
        return False

def test_nasa_api(api_key: str) -> bool:
    """Testa conexão com NASA."""
    try:
        url = "https://api.nasa.gov/planetary/apod"
        params = {"api_key": api_key}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ NASA: Funcionando! (APOD: {data.get('title', 'OK')[:50]}...)")
        return True
    
    except Exception as e:
        print(f"❌ NASA: Erro - {str(e)[:100]}")
        return False

def test_all_apis():
    """Testa todas as APIs configuradas."""
    print("\n🧪 TESTANDO CONEXÕES COM APIS")
    print("=" * 40)
    
    manager = SecureCredentialManager()
    credentials = manager.load_credentials()
    
    if not credentials:
        print("❌ Nenhuma credencial encontrada!")
        return False
    
    results = {}
    
    # Testar OpenWeatherMap
    if 'OPENWEATHER_API_KEY' in credentials:
        results['openweather'] = test_openweather_api(credentials['OPENWEATHER_API_KEY'])
    
    # Testar AirVisual
    if 'AIRVISUAL_API_KEY' in credentials:
        results['airvisual'] = test_airvisual_api(credentials['AIRVISUAL_API_KEY'])
    
    # Testar NASA
    if 'NASA_API_KEY' in credentials:
        results['nasa'] = test_nasa_api(credentials['NASA_API_KEY'])
    
    # Resumo
    print(f"\n📊 RESUMO DOS TESTES:")
    working_apis = sum(results.values())
    total_apis = len(results)
    
    print(f"✅ APIs funcionando: {working_apis}/{total_apis}")
    
    if working_apis > 0:
        print("🚀 Pronto para usar dados reais!")
        return True
    else:
        print("⚠️ Verifique suas chaves de API")
        return False

def setup_project():
    """Configuração completa do projeto."""
    print("🌍 CONFIGURAÇÃO DO PROJETO CLIMATE ANALYTICS")
    print("=" * 50)
    
    print("\n📋 Este script vai:")
    print("1. Configurar suas credenciais de API de forma segura")
    print("2. Testar conexões com os serviços")
    print("3. Atualizar configurações do projeto")
    
    proceed = input("\n▶️  Continuar? (s/N): ").lower().strip()
    if proceed != 's':
        print("❌ Configuração cancelada.")
        return False
    
    # Configurar credenciais
    print("\n" + "="*50)
    success = setup_credentials_interactive()
    
    if success:
        # Testar APIs
        print("\n" + "="*50)
        test_all_apis()
        
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
        print("\n📋 Próximos passos:")
        print("1. Execute: streamlit run src/dashboard/app.py")
        print("2. Execute: python data_collector.py")
        print("3. Acesse: http://localhost:8501")
        
        return True
    else:
        print("❌ Erro na configuração das credenciais")
        return False

def main():
    """Função principal."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test-only":
        # Apenas testar APIs existentes
        test_all_apis()
    else:
        # Configuração completa
        setup_project()

if __name__ == "__main__":
    main()
