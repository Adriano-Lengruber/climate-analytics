"""
Aplicação principal do dashboard Climate Analytics.
Dashboard interativo para visualização de dados climáticos e de qualidade do ar.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import Config
from src.api.weather_api import OpenWeatherClient
from src.api.air_quality_api import AirQualityClient
from src.dashboard.advanced_components import DashboardComponents
from src.dashboard.welcome_clean import show_welcome_page

# Configuração da página
st.set_page_config(**Config.STREAMLIT_CONFIG)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Função principal da aplicação."""
    
    # Verificar se deve mostrar a página de boas-vindas    # Sempre mostrar se não há credenciais configuradas
    
    # Verifica se existe arquivo .env com credenciais válidas
    env_exists = os.path.exists('.env')
    has_credentials = False
    
    # Debug - Adicionar informações sobre o estado
    st.sidebar.write(f"🔍 Debug: .env existe? {env_exists}")
    
    if env_exists:
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                has_openweather = 'OPENWEATHER_API_KEY=' in content and len(content.split('OPENWEATHER_API_KEY=')[1].split('\n')[0].strip()) > 10
                has_airvisual = 'AIRVISUAL_API_KEY=' in content and len(content.split('AIRVISUAL_API_KEY=')[1].split('\n')[0].strip()) > 10
                has_credentials = has_openweather and has_airvisual
        except:
            has_credentials = False
    
    # Debug - Adicionar mais informações
    st.sidebar.write(f"🔍 Debug: has_credentials? {has_credentials}")    # Se não há credenciais válidas, mostrar página de boas-vindas
    if not has_credentials:
        st.sidebar.write("🎯 Debug: Entrando na página de boas-vindas!")
        st.session_state.show_welcome = True  # Força a exibição da página de boas-vindas
        
        # Chama a página de boas-vindas e verifica se deve continuar
        system_ready = show_welcome_page()
        
        if system_ready:
            st.sidebar.write("🎯 Debug: Credenciais configuradas, continuando para dashboard")
            # Credenciais configuradas, continuar para dashboard
            st.session_state.show_welcome = False
            # NÃO faz return aqui, continua para o dashboard
        else:
            st.sidebar.write("🎯 Debug: Ainda mostrando página de boas-vindas")
            # Para aqui para manter a página de boas-vindas visível
            st.stop()  # Para a execução mas mantém o que já foi renderizado
    
    # Continua com o dashboard normal se as APIs estão configuradas
    
    # Header
    st.markdown('<h1 class="main-header">🌍 Climate & Air Quality Analytics</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Verificação de APIs
        api_status = check_api_configuration()
        display_api_status(api_status)
        
        st.markdown("---")
        
        # Seleção de localização
        location_type = st.radio(
            "Tipo de localização:",
            ["Cidade", "Coordenadas", "Localização atual"]
        )
        
        if location_type == "Cidade":
            city = st.text_input("Cidade:", value=Config.DEFAULT_CITY)
            country = st.text_input("País (código):", value=Config.DEFAULT_COUNTRY)
            location = {"type": "city", "city": city, "country": country}
        elif location_type == "Coordenadas":
            lat = st.number_input("Latitude:", value=Config.DEFAULT_LAT, format="%.4f")
            lon = st.number_input("Longitude:", value=Config.DEFAULT_LON, format="%.4f")
            location = {"type": "coords", "lat": lat, "lon": lon}
        else:
            location = {"type": "current"}
            st.info("📍 Usando localização padrão: São Paulo, BR")
      # Conteúdo principal
    if not any(api_status.values()):
        show_setup_instructions()
        return
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard Principal", 
        "🌡️ Análise Climática", 
        "💨 Qualidade do Ar", 
        "🤖 Previsões IA",
        "🧠 Análise Avançada"
    ])
    
    with tab1:
        show_main_dashboard(location)
    
    with tab2:
        show_climate_analysis(location)
    
    with tab3:
        show_air_quality_analysis(location)
    
    with tab4:
        show_ai_predictions(location)
    
    with tab5:
        show_advanced_analysis()

def check_api_configuration():
    """Verifica se as APIs estão configuradas."""
    return Config.validate_api_keys()

def display_api_status(api_status):
    """Exibe o status das APIs na sidebar."""
    st.subheader("📡 Status das APIs")
    
    for api, status in api_status.items():
        if status:
            st.success(f"✅ {api.title()}: Configurada")
        else:
            st.error(f"❌ {api.title()}: Não configurada")

def show_setup_instructions():
    """Mostra instruções de configuração."""
    st.error("🔑 APIs não configuradas!")
    
    st.markdown("""
    ### Configuração necessária:
    
    1. **Crie um arquivo `.env`** na raiz do projeto
    2. **Obtenha chaves gratuitas das APIs:**
       - [OpenWeatherMap](https://openweathermap.org/api) para dados meteorológicos
       - [AirVisual](https://www.airvisual.com/api) para qualidade do ar
    
    3. **Adicione as chaves no arquivo `.env`:**
    ```
    OPENWEATHER_API_KEY=sua_chave_aqui
    AIRVISUAL_API_KEY=sua_chave_aqui
    ```
    
    4. **Reinicie a aplicação**
    """)

def show_main_dashboard(location):
    """Dashboard principal com visão geral."""
    st.header("📊 Visão Geral")
    
    try:
        # Dados meteorológicos
        if Config.OPENWEATHER_API_KEY:
            weather_data = get_weather_data(location)
            if weather_data:
                display_weather_overview(weather_data)
        
        # Dados de qualidade do ar
        if Config.AIRVISUAL_API_KEY:
            air_data = get_air_quality_data(location)
            if air_data:
                display_air_quality_overview(air_data)
        
        # Mapa interativo
        display_interactive_map(location)
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

def get_weather_data(location):
    """Obtém dados meteorológicos."""
    try:
        client = OpenWeatherClient()
        
        if location["type"] == "city":
            return client.get_current_weather(location["city"], location["country"])
        elif location["type"] == "coords":
            return client.get_current_weather_by_coords(location["lat"], location["lon"])
        else:
            return client.get_current_weather(Config.DEFAULT_CITY, Config.DEFAULT_COUNTRY)
    
    except Exception as e:
        st.error(f"Erro ao obter dados meteorológicos: {str(e)}")
        return None

def get_air_quality_data(location):
    """Obtém dados de qualidade do ar."""
    try:
        client = AirQualityClient()
        
        if location["type"] == "coords":
            return client.get_air_quality_by_coords(location["lat"], location["lon"])
        else:
            # Para cidade ou localização atual, usa coordenadas padrão
            return client.get_air_quality_by_coords(Config.DEFAULT_LAT, Config.DEFAULT_LON)
    
    except Exception as e:
        st.error(f"Erro ao obter dados de qualidade do ar: {str(e)}")
        return None

def display_weather_overview(weather_data):
    """Exibe overview dos dados meteorológicos."""
    st.subheader("🌡️ Condições Meteorológicas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Temperatura",
            f"{weather_data['weather']['temperature']:.1f}°C",
            f"Sensação: {weather_data['weather']['feels_like']:.1f}°C"
        )
    
    with col2:
        st.metric(
            "Umidade",
            f"{weather_data['weather']['humidity']}%"
        )
    
    with col3:
        st.metric(
            "Pressão",
            f"{weather_data['weather']['pressure']} hPa"
        )
    
    with col4:
        st.metric(
            "Vento",
            f"{weather_data['wind']['speed']} m/s"
        )
    
    # Informações adicionais
    st.info(f"📍 {weather_data['location']['city']}, {weather_data['location']['country']} | "
           f"🌤️ {weather_data['weather']['description'].title()}")

def display_air_quality_overview(air_data):
    """Exibe overview da qualidade do ar."""
    st.subheader("💨 Qualidade do Ar")
    
    aqi = air_data['air_quality']['aqi_us']
    aqi_info = AirQualityClient.get_aqi_category(aqi)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Índice AQI (US)", aqi)
        
    with col2:
        st.markdown(f"""
        <div style="background-color: {aqi_info['color']}; padding: 10px; border-radius: 5px; color: white;">
            <strong>{aqi_info['category']}</strong><br>
            {aqi_info['description']}
        </div>
        """, unsafe_allow_html=True)

def display_interactive_map(location):
    """Exibe mapa interativo."""
    st.subheader("🗺️ Localização")
    
    # Determina coordenadas para o mapa
    if location["type"] == "coords":
        lat, lon = location["lat"], location["lon"]
    else:
        lat, lon = Config.DEFAULT_LAT, Config.DEFAULT_LON
    
    # Cria mapa
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], popup="Localização atual").add_to(m)
    
    # Exibe mapa
    st_folium(m, width=700, height=500)

def show_climate_analysis(location):
    """Tab de análise climática detalhada."""
    st.header("🌡️ Análise Climática Detalhada")
    st.info("🚧 Em desenvolvimento - Análises históricas e tendências climáticas")

def show_air_quality_analysis(location):
    """Tab de análise de qualidade do ar."""
    st.header("💨 Análise de Qualidade do Ar")
    st.info("🚧 Em desenvolvimento - Análise detalhada de poluentes e tendências")

def show_ai_predictions(location):
    """Tab de previsões com IA."""
    st.header("🤖 Previsões com Inteligência Artificial")
    st.info("🚧 Em desenvolvimento - Modelos de ML para previsões climáticas")

def show_advanced_analysis():
    """Tab de análise avançada com novos componentes."""
    st.header("🧠 Análise Avançada de Dados Climáticos")
    
    # Verifica se há dados no banco
    db_path = Config.DATABASE_PATH
    
    try:
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM weather_data")
            weather_count = cursor.fetchone()[0]
            
            if weather_count == 0:
                st.warning("⚠️ Não há dados suficientes para análise avançada. Execute o coletor de dados primeiro.")
                return
    except Exception as e:
        st.error(f"Erro ao verificar banco de dados: {e}")
        return
    
    # Seletores de tipo de análise
    analysis_options = st.multiselect(
        "Selecione os tipos de análise:",
        [
            "🚨 Sistema de Alertas Inteligentes",
            "🔗 Análise de Correlações",
            "🌿 Índice de Saúde Ambiental",
            "🔮 Previsões Baseadas em Tendências"
        ],
        default=["🚨 Sistema de Alertas Inteligentes", "🌿 Índice de Saúde Ambiental"]
    )
    
    st.markdown("---")
    
    # Renderiza componentes selecionados
    if "🚨 Sistema de Alertas Inteligentes" in analysis_options:
        DashboardComponents.render_alert_panel(db_path)
        st.markdown("---")
    
    if "🔗 Análise de Correlações" in analysis_options:
        DashboardComponents.render_correlation_analysis(db_path)
        st.markdown("---")
    
    if "🌿 Índice de Saúde Ambiental" in analysis_options:
        DashboardComponents.render_environmental_health_index(db_path)
        st.markdown("---")
    
    if "🔮 Previsões Baseadas em Tendências" in analysis_options:
        DashboardComponents.render_forecast_panel(db_path)

if __name__ == "__main__":
    main()
