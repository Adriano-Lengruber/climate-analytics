"""
Climate Analytics Dashboard - Sistema Profissional de Monitoramento Climático
Dashboard principal para análise de mudanças climáticas e qualidade do ar
"""
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys
from pathlib import Path
import numpy as np
import requests
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from config.settings import Config
except ImportError:
    st.error("Erro ao importar configurações. Verifique se os módulos estão instalados.")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="🌍 Climate Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_user_location():
    """Detecta a localização do usuário usando IP com fallback robusto."""
    try:
        # Tentar múltiplos serviços de geolocalização
        services = [
            'http://ip-api.com/json/',
            'https://ipapi.co/json/',
            'https://freegeoip.app/json/'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Normalizar dados de diferentes APIs
                    if 'status' in data and data['status'] == 'success':  # ip-api
                        return {
                            'city': data.get('city', 'São Paulo'),
                            'country': data.get('country', 'Brazil'),
                            'country_code': data.get('countryCode', 'BR'),
                            'lat': data.get('lat', -23.5505),
                            'lon': data.get('lon', -46.6333),
                            'region': data.get('regionName', 'São Paulo')
                        }
                    elif 'city' in data:  # ipapi.co e freegeoip
                        return {
                            'city': data.get('city', 'São Paulo'),
                            'country': data.get('country_name', data.get('country', 'Brazil')),
                            'country_code': data.get('country_code', 'BR'),
                            'lat': data.get('latitude', data.get('lat', -23.5505)),
                            'lon': data.get('longitude', data.get('lon', -46.6333)),
                            'region': data.get('region', data.get('regionName', 'São Paulo'))
                        }
            except Exception as e:
                logger.warning(f"Erro ao usar serviço {service}: {e}")
                continue
                
    except Exception as e:
        logger.warning(f"Erro geral na detecção de localização: {e}")
    
    # Fallback para São Paulo se todos os serviços falharem
    return {
        'city': 'São Paulo',
        'country': 'Brazil',
        'country_code': 'BR', 
        'lat': -23.5505,
        'lon': -46.6333,
        'region': 'São Paulo'
    }

def get_available_cities():
    """Lista de cidades principais disponíveis (mantida para compatibilidade)."""
    return get_dynamic_cities()

def get_air_quality_status(aqi):
    """Retorna status da qualidade do ar baseado no AQI."""
    if aqi <= 50:
        return "🟢 Boa", "#00E400"
    elif aqi <= 100:
        return "🟡 Moderada", "#FFFF00"
    elif aqi <= 150:
        return "🟠 Insalubre para Grupos Sensíveis", "#FF7E00"
    elif aqi <= 200:
        return "🔴 Insalubre", "#FF0000"
    elif aqi <= 300:
        return "🟣 Muito Insalubre", "#8F3F97"
    else:
        return "🟤 Perigosa", "#7E0023"

def load_climate_data(selected_city=None):
    """Carrega dados climáticos completos do banco de dados."""
    try:
        if not os.path.exists(Config.DATABASE_PATH):
            return pd.DataFrame(), pd.DataFrame()
            
        conn = sqlite3.connect(Config.DATABASE_PATH)
        
        # Filtro por cidade se especificado
        city_filter = ""
        if selected_city:
            city_name = selected_city.split(',')[0].strip()
            city_filter = f"WHERE city LIKE '%{city_name}%'"
        
        # Dados meteorológicos completos
        weather_query = f"""
        SELECT timestamp, city, country, temperature, feels_like, humidity, 
               pressure, description, wind_speed, wind_direction, visibility, clouds
        FROM weather_data 
        {city_filter}
        ORDER BY timestamp DESC
        LIMIT 100
        """
        weather_df = pd.read_sql_query(weather_query, conn)
        
        # Dados de qualidade do ar completos  
        air_query = f"""
        SELECT timestamp, city, country, aqi_us, main_pollutant_us, aqi_cn, 
               main_pollutant_cn, temperature, pressure, humidity, wind_speed
        FROM air_quality_data 
        {city_filter}
        ORDER BY timestamp DESC
        LIMIT 100
        """
        air_df = pd.read_sql_query(air_query, conn)
        
        conn.close()
        
        # Converter timestamp com tratamento robusto
        if not weather_df.empty:
            weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'], errors='coerce', utc=True)
            weather_df = weather_df.dropna(subset=['timestamp'])
        if not air_df.empty:
            air_df['timestamp'] = pd.to_datetime(air_df['timestamp'], errors='coerce', utc=True)
            air_df = air_df.dropna(subset=['timestamp'])
        
        return weather_df, air_df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

def check_credentials():
    """Verifica se as credenciais estão configuradas."""
    try:
        if not os.path.exists('.env'):
            return False
        
        with open('.env', 'r') as f:
            env_content = f.read()
            
        has_weather_key = 'OPENWEATHER_API_KEY=' in env_content
        has_air_key = 'AIRVISUAL_API_KEY=' in env_content
        
        return has_weather_key and has_air_key
    except Exception:
        return False

def collect_data_for_city(city_name, lat, lon):
    """Coleta dados para uma cidade específica."""
    try:
        import subprocess
        # Executar o coletor de dados com parâmetros da cidade
        cmd = f'python data_collector.py --city="{city_name}" --lat={lat} --lon={lon}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        st.error(f"Erro ao coletar dados: {e}")
        return False

def create_weather_analysis(weather_df):
    """Análise meteorológica avançada."""
    if weather_df.empty:
        st.warning("📊 Nenhum dado meteorológico disponível. Colete dados primeiro.")
        return
    
    st.header("🌡️ Análise Meteorológica Detalhada")
    
    # Dados mais recentes
    latest = weather_df.iloc[0]
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🌡️ Temperatura", 
            f"{latest['temperature']:.1f}°C",
            delta=f"Sensação: {latest['feels_like']:.1f}°C"
        )
    
    with col2:
        st.metric("💧 Umidade", f"{latest['humidity']}%")
    
    with col3:
        st.metric("🌬️ Pressão", f"{latest['pressure']} hPa")
    
    with col4:
        st.metric("💨 Vento", f"{latest['wind_speed']} m/s")
    
    with col5:
        st.metric("👁️ Visibilidade", f"{latest['visibility']} km")
    
    # Informações contextuais
    st.markdown(f"""
    **📍 Localização:** {latest['city']}, {latest['country']}  
    **🌤️ Condições:** {latest['description'].title()}  
    **☁️ Nebulosidade:** {latest['clouds']}%  
    **🧭 Direção do Vento:** {latest['wind_direction']}°
    """)
    
    st.markdown("---")
    
    # Gráficos de tendência
    if len(weather_df) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de temperatura
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=weather_df['timestamp'],
                y=weather_df['temperature'],
                mode='lines+markers',
                name='Temperatura Real',
                line=dict(color='#FF6B6B', width=3),
                hovertemplate='<b>%{y:.1f}°C</b><br>%{x}<br><extra></extra>'
            ))
            fig_temp.add_trace(go.Scatter(
                x=weather_df['timestamp'],
                y=weather_df['feels_like'],
                mode='lines+markers',
                name='Sensação Térmica',
                line=dict(color='#4ECDC4', width=2, dash='dash'),
                hovertemplate='<b>Sensação: %{y:.1f}°C</b><br>%{x}<br><extra></extra>'
            ))
            
            # Zonas de conforto térmico
            fig_temp.add_hrect(y0=18, y1=24, fillcolor="lightgreen", opacity=0.2, annotation_text="Zona de Conforto")
            fig_temp.add_hrect(y0=30, y1=50, fillcolor="orange", opacity=0.1, annotation_text="Calor Intenso")
            fig_temp.add_hrect(y0=-10, y1=10, fillcolor="lightblue", opacity=0.1, annotation_text="Frio Intenso")
            
            fig_temp.update_layout(
                title="🌡️ Temperatura e Sensação Térmica",
                xaxis_title="Data/Hora",
                yaxis_title="Temperatura (°C)",
                height=450,
                showlegend=True,
                hovermode='x unified'
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            # Gráfico de umidade e pressão
            fig_env = go.Figure()
            
            # Normalizar pressão para visualização
            pressure_normalized = ((weather_df['pressure'] - 1000) / 20) * 100
            
            fig_env.add_trace(go.Scatter(
                x=weather_df['timestamp'],
                y=weather_df['humidity'],
                mode='lines+markers',
                name='Umidade (%)',
                line=dict(color='#45B7D1', width=3),
                hovertemplate='<b>Umidade: %{y}%</b><br>%{x}<br><extra></extra>'
            ))
            
            fig_env.add_trace(go.Scatter(
                x=weather_df['timestamp'],
                y=pressure_normalized,
                mode='lines+markers',
                name='Pressão (normalizada)',
                line=dict(color='#96CEB4', width=3),
                yaxis='y2',
                hovertemplate='<b>Pressão: %{customdata} hPa</b><br>%{x}<br><extra></extra>',
                customdata=weather_df['pressure']
            ))
            
            # Zonas de referência
            fig_env.add_hrect(y0=40, y1=60, fillcolor="lightgreen", opacity=0.2, annotation_text="Umidade Ideal")
            
            fig_env.update_layout(
                title="💧 Umidade e Pressão Atmosférica",
                xaxis_title="Data/Hora",
                yaxis=dict(title="Umidade (%)", side="left", range=[0, 100]),
                yaxis2=dict(title="Pressão (escala relativa)", side="right", overlaying="y", range=[0, 100]),
                height=450,
                hovermode='x unified'
            )
            st.plotly_chart(fig_env, use_container_width=True)

def create_air_quality_analysis(air_df):
    """Análise de qualidade do ar avançada."""
    if air_df.empty:
        st.warning("🌫️ Nenhum dado de qualidade do ar disponível. Colete dados primeiro.")
        return
    
    st.header("🌫️ Análise de Qualidade do Ar")
    
    # Dados mais recentes
    latest = air_df.iloc[0]
    
    # Status da qualidade do ar
    aqi_us_status, aqi_us_color = get_air_quality_status(latest['aqi_us'])
    aqi_cn_status, aqi_cn_color = get_air_quality_status(latest['aqi_cn'])
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🇺🇸 AQI US", 
            latest['aqi_us'],
            delta=f"Poluente: {latest['main_pollutant_us']}"
        )
        st.markdown(f"**Status:** {aqi_us_status}")
    
    with col2:
        st.metric(
            "🇨🇳 AQI China", 
            latest['aqi_cn'],
            delta=f"Poluente: {latest['main_pollutant_cn']}"
        )
        st.markdown(f"**Status:** {aqi_cn_status}")
    
    with col3:
        st.metric("🌡️ Temperatura", f"{latest['temperature']}°C")
    
    with col4:
        st.metric("💧 Umidade", f"{latest['humidity']}%")
    
    # Informações contextuais
    st.markdown(f"""
    **📍 Localização:** {latest['city']}, {latest['country']}  
    **⏰ Última Atualização:** {latest['timestamp'].strftime('%d/%m/%Y %H:%M')}
    """)
    
    # Explicação dos índices
    with st.expander("ℹ️ Entenda os Índices AQI"):
        st.markdown("""
        ### 🌍 Índices de Qualidade do Ar
        
        **AQI US (EPA):**
        - 🟢 0-50: Boa
        - 🟡 51-100: Moderada  
        - 🟠 101-150: Insalubre para grupos sensíveis
        - 🔴 151-200: Insalubre
        - 🟣 201-300: Muito insalubre
        - 🟤 301+: Perigosa
        
        **Principais Poluentes:**
        - **PM2.5**: Partículas finas (< 2.5 μm)
        - **PM10**: Partículas grossas (< 10 μm)  
        - **O3**: Ozônio
        - **NO2**: Dióxido de nitrogênio
        - **SO2**: Dióxido de enxofre
        - **CO**: Monóxido de carbono
        """)
    
    st.markdown("---")
    
    # Gráficos de tendência
    if len(air_df) > 1:
        # Gráfico comparativo AQI
        fig_aqi = go.Figure()
        fig_aqi.add_trace(go.Scatter(
            x=air_df['timestamp'],
            y=air_df['aqi_us'],
            mode='lines+markers',
            name='AQI US (EPA)',
            line=dict(color='#FF6B6B', width=3),
            hovertemplate='<b>AQI US: %{y}</b><br>%{x}<br><extra></extra>'
        ))
        fig_aqi.add_trace(go.Scatter(
            x=air_df['timestamp'],
            y=air_df['aqi_cn'],
            mode='lines+markers',
            name='AQI China',
            line=dict(color='#4ECDC4', width=3),
            hovertemplate='<b>AQI China: %{y}</b><br>%{x}<br><extra></extra>'
        ))
        
        # Zonas de qualidade do ar
        fig_aqi.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1, annotation_text="Boa")
        fig_aqi.add_hrect(y0=51, y1=100, fillcolor="yellow", opacity=0.1, annotation_text="Moderada")
        fig_aqi.add_hrect(y0=101, y1=150, fillcolor="orange", opacity=0.1, annotation_text="Insalubre (Sensíveis)")
        fig_aqi.add_hrect(y0=151, y1=200, fillcolor="red", opacity=0.1, annotation_text="Insalubre")
        
        fig_aqi.update_layout(
            title="🌫️ Evolução da Qualidade do Ar",
            xaxis_title="Data/Hora",
            yaxis_title="Índice AQI",
            height=500,
            hovermode='x unified'
        )
        st.plotly_chart(fig_aqi, use_container_width=True)

def create_alerts_section(weather_df, air_df):
    """Sistema de alertas inteligente."""
    st.header("🚨 Sistema de Alertas Inteligente")
    
    alerts = []
    recommendations = []
    
    # Alertas meteorológicos
    if not weather_df.empty:
        latest_temp = weather_df.iloc[0]['temperature']
        latest_humidity = weather_df.iloc[0]['humidity']
        latest_wind = weather_df.iloc[0]['wind_speed']
        
        if latest_temp > 35:
            alerts.append("🌡️ **ALERTA CALOR:** Temperatura extrema detectada!")
            recommendations.extend([
                "• Evite exposição ao sol entre 10h-16h",
                "• Mantenha-se hidratado",
                "• Use protetor solar e roupas leves"
            ])
        elif latest_temp < 5:
            alerts.append("❄️ **ALERTA FRIO:** Temperatura muito baixa!")
            recommendations.extend([
                "• Use roupas adequadas para o frio",
                "• Proteja extremidades do corpo"
            ])
        
        if latest_humidity > 80:
            alerts.append("💧 **UMIDADE ALTA:** Desconforto térmico possível")
            recommendations.append("• Use ventilação adequada em ambientes fechados")
        elif latest_humidity < 30:
            alerts.append("🏜️ **AR SECO:** Umidade muito baixa")
            recommendations.extend([
                "• Use umidificador ou recipientes com água",
                "• Hidrate-se mais frequentemente"
            ])
        
        if latest_wind > 15:
            alerts.append("💨 **VENTO FORTE:** Ventos intensos detectados")
            recommendations.append("• Cuidado com objetos soltos")
    
    # Alertas de qualidade do ar
    if not air_df.empty:
        latest_aqi = air_df.iloc[0]['aqi_us']
        
        if latest_aqi > 200:
            alerts.append("🚨 **EMERGÊNCIA:** Qualidade do ar muito perigosa!")
            recommendations.extend([
                "• Evite atividades ao ar livre",
                "• Use máscaras N95 se precisar sair",
                "• Mantenha janelas fechadas"
            ])
        elif latest_aqi > 150:
            alerts.append("🔴 **ALERTA CRÍTICO:** Qualidade do ar insalubre!")
            recommendations.extend([
                "• Limite atividades ao ar livre",
                "• Grupos sensíveis devem ficar em casa"
            ])
        elif latest_aqi > 100:
            alerts.append("🟠 **ATENÇÃO:** Qualidade inadequada para sensíveis")
            recommendations.append("• Crianças e idosos devem evitar exercícios externos")
        elif latest_aqi <= 50:
            alerts.append("🟢 **EXCELENTE:** Qualidade do ar ótima!")
            recommendations.append("• Aproveite para atividades ao ar livre")
    
    # Exibir alertas
    if alerts:
        for alert in alerts:
            if "EMERGÊNCIA" in alert or "CRÍTICO" in alert:
                st.error(alert)
            elif "ALERTA" in alert:
                st.warning(alert)
            else:
                st.success(alert)
    
    # Exibir recomendações
    if recommendations:
        st.markdown("**💡 Recomendações:**")
        for rec in recommendations:
            st.markdown(rec)
    
    if not alerts:
        st.info("ℹ️ **Condições normais.** Continue monitorando regularmente.")

def show_welcome_page():
    """Página de boas-vindas e configuração."""
    st.title("🌍 Climate Analytics")
    st.markdown("### Sistema Profissional de Monitoramento Climático")
    st.markdown("---")
    
    st.info("🚀 **Configure suas credenciais para começar a análise climática**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔑 APIs Necessárias
        
        **OpenWeatherMap API** (Gratuita)
        - Dados meteorológicos em tempo real
        - Previsões de até 5 dias
        - Acesse: https://openweathermap.org/api
        
        **IQAir AirVisual API** (Gratuita)
        - Qualidade do ar global
        - Índices AQI US e China
        - Acesse: https://www.iqair.com/air-pollution-data-api
        """)
    
    with col2:
        st.markdown("""
        ### ⚙️ Como Configurar
        
        1. **Obtenha suas chaves das APIs**
        2. **Execute no terminal:**
        ```bash
        python setup_credentials.py
        ```
        3. **Ou crie arquivo `.env`:**
        ```env
        OPENWEATHER_API_KEY=sua_chave_aqui
        AIRVISUAL_API_KEY=sua_chave_aqui
        ```
        """)
    
    if st.button("🔄 Verificar Credenciais", type="primary"):
        st.info("♻️ Atualize a página para verificar as credenciais configuradas.")

def show_dashboard():
    """Dashboard principal com análises completas."""
    st.title("🌍 Climate Analytics")
    st.markdown("### Monitoramento Climático e Qualidade do Ar em Tempo Real")
      # Detecção automática de localização
    if 'user_location' not in st.session_state:
        with st.spinner("🌍 Detectando sua localização..."):
            st.session_state.user_location = get_user_location()
            
            # Adicionar cidade detectada às opções automaticamente
            detected_city_key = add_detected_city_to_options(st.session_state.user_location)
            st.session_state.selected_city = detected_city_key
            
            # Tentar coletar dados automaticamente para a cidade detectada
            if auto_collect_data_for_detected_city(detected_city_key, st.session_state.user_location):
                st.success(f"🚀 Coletando dados para {detected_city_key} em segundo plano...")
    
    # Seleção de cidade
    st.markdown("### 📍 Seleção de Localização")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Detecção automática
        location = st.session_state.user_location
        st.info(f"📡 **Localização Detectada:** {location['city']}, {location['country']}")
        
        if st.button("🔄 Usar Localização Atual"):
            detected_city_key = add_detected_city_to_options(location)
            st.session_state.selected_city = detected_city_key
            
            # Coletar dados automaticamente
            if auto_collect_data_for_detected_city(detected_city_key, location):
                st.success(f"🚀 Coletando dados para {detected_city_key}...")
            st.balloons()
    
    with col2:        # Seleção manual
        available_cities = get_available_cities()
        
        # Obter cidade selecionada de forma segura
        current_selected = st.session_state.get('selected_city', '')
        try:
            # Tentar encontrar a cidade na lista
            if current_selected in available_cities:
                default_index = list(available_cities.keys()).index(current_selected)
            else:
                default_index = 0
        except (ValueError, IndexError):
            default_index = 0
        
        selected_city = st.selectbox(
            "🏙️ Ou escolha uma cidade:",
            options=list(available_cities.keys()),
            index=default_index
        )
        st.session_state.selected_city = selected_city
          # Campo de busca livre
        custom_city = st.text_input("🔍 Ou digite qualquer cidade:", placeholder="Ex: Cidade, País")
        if custom_city:
            st.session_state.selected_city = custom_city
            st.info(f"Cidade personalizada: {custom_city}")
    
    with col3:
        # Botão para coletar dados
        current_city = st.session_state.get('selected_city', selected_city)
        if st.button("🔄 Coletar Dados", type="primary"):
            # Determinar coordenadas da cidade
            if current_city in available_cities:
                city_data = available_cities[current_city]
                lat, lon = city_data['lat'], city_data['lon']
            elif 'custom_city_data' in st.session_state and st.session_state.custom_city_data['name'] == current_city:
                # Usar dados da cidade detectada automaticamente
                lat, lon = st.session_state.custom_city_data['lat'], st.session_state.custom_city_data['lon']
            else:
                # Para cidades totalmente customizadas, tentar obter coordenadas (fallback para São Paulo)
                lat, lon = -23.5505, -46.6333
                st.warning(f"⚠️ Coordenadas padrão usadas para '{current_city}'. Para melhores resultados, use uma cidade da lista.")
            
            with st.spinner(f"🌐 Coletando dados para {current_city}..."):
                if collect_data_for_city(current_city, lat, lon):
                    st.success("✅ Dados coletados com sucesso!")
                    st.balloons()
                    time.sleep(2)
                else:
                    st.error("❌ Erro ao coletar dados. Verifique suas credenciais.")
                    st.info("💡 Dica: Verifique se suas chaves de API estão configuradas no arquivo .env")
    
    st.markdown("---")
      # Carregar dados para a cidade selecionada
    with st.spinner(f"🔄 Carregando dados para {current_city}..."):
        weather_df, air_df = load_climate_data(current_city)
        
        # Verificar se há dados para a cidade selecionada
        if weather_df.empty and air_df.empty:
            st.warning(f"⚠️ **Nenhum dado encontrado para '{current_city}'**")
            st.info("💡 **Sugestões:**")
            st.markdown("- Clique em '🔄 Coletar Dados' para obter dados desta cidade")
            st.markdown("- Ou selecione uma cidade que já possui dados (São Paulo)")
            
            # Tentar carregar dados gerais como fallback
            st.info("📊 Mostrando dados disponíveis no sistema:")
            weather_df, air_df = load_climate_data(None)  # Carregar todos os dados
      # Status dos dados
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Registros Meteorológicos", len(weather_df))
    with col2:
        st.metric("🌫️ Registros Qualidade do Ar", len(air_df))
    with col3:
        if not weather_df.empty:
            latest_time = weather_df.iloc[0]['timestamp']
            hours_ago = (datetime.now(latest_time.tz) - latest_time).total_seconds() / 3600
            st.metric("⏰ Última Coleta", f"{hours_ago:.1f}h atrás")
        else:
            st.metric("⏰ Última Coleta", "N/A")
    with col4:
        # Mostrar cidade dos dados reais
        if not weather_df.empty:
            actual_city = weather_df.iloc[0]['city']
            actual_country = weather_df.iloc[0]['country']
            data_location = f"{actual_city}, {actual_country}"
            if data_location != current_city:
                st.metric("🌍 Dados de", data_location, delta="(diferente da selecionada)")
            else:
                st.metric("🌍 Localização", current_city)
        else:
            st.metric("🌍 Localização Selecionada", current_city)
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️ Análise Meteorológica", 
        "🌫️ Qualidade do Ar", 
        "🚨 Alertas e Análises",
        "📋 Dados Brutos"
    ])
    
    with tab1:
        create_weather_analysis(weather_df)
    
    with tab2:
        create_air_quality_analysis(air_df)
    
    with tab3:
        create_alerts_section(weather_df, air_df)
    
    with tab4:
        st.header("📋 Dados Brutos para Análise")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌡️ Dados Meteorológicos")
            if not weather_df.empty:
                st.dataframe(weather_df, use_container_width=True)
                csv_weather = weather_df.to_csv(index=False)
                st.download_button(
                    "📥 Baixar Dados Meteorológicos (CSV)",
                    csv_weather,
                    f"meteorologia_{current_city.replace(', ', '_')}.csv",
                    "text/csv"
                )
            else:
                st.info("Nenhum dado meteorológico disponível")
        
        with col2:
            st.subheader("🌫️ Dados de Qualidade do Ar")
            if not air_df.empty:
                st.dataframe(air_df, use_container_width=True)
                csv_air = air_df.to_csv(index=False)
                st.download_button(
                    "📥 Baixar Dados Qualidade do Ar (CSV)",
                    csv_air,
                    f"qualidade_ar_{current_city.replace(', ', '_')}.csv",
                    "text/csv"
                )
            else:
                st.info("Nenhum dado de qualidade do ar disponível")

def get_dynamic_cities():
    """Obtém lista de cidades disponíveis incluindo cidades detectadas dinamicamente."""
    # Cidades base pré-definidas
    base_cities = {
        'São Paulo, BR': {'lat': -23.5505, 'lon': -46.6333, 'country': 'BR'},
        'Rio de Janeiro, BR': {'lat': -22.9068, 'lon': -43.1729, 'country': 'BR'},
        'Brasília, BR': {'lat': -15.8267, 'lon': -47.9218, 'country': 'BR'},
        'Salvador, BR': {'lat': -12.9714, 'lon': -38.5124, 'country': 'BR'},
        'Fortaleza, BR': {'lat': -3.7319, 'lon': -38.5267, 'country': 'BR'},
        'Belo Horizonte, BR': {'lat': -19.9167, 'lon': -43.9345, 'country': 'BR'},
        'Manaus, BR': {'lat': -3.1190, 'lon': -60.0217, 'country': 'BR'},
        'Curitiba, BR': {'lat': -25.4284, 'lon': -49.2733, 'country': 'BR'},
        'Recife, BR': {'lat': -8.0476, 'lon': -34.8770, 'country': 'BR'},
        'Porto Alegre, BR': {'lat': -30.0346, 'lon': -51.2177, 'country': 'BR'},
        'Itaperuna, Brazil': {'lat': -21.2044, 'lon': -41.8891, 'country': 'BR'},
        'Buenos Aires, AR': {'lat': -34.6118, 'lon': -58.3960, 'country': 'AR'},
        'Córdoba, AR': {'lat': -31.4201, 'lon': -64.1888, 'country': 'AR'},
        'Lima, PE': {'lat': -12.0464, 'lon': -77.0428, 'country': 'PE'},
        'Santiago, CL': {'lat': -33.4489, 'lon': -70.6693, 'country': 'CL'},
        'Bogotá, CO': {'lat': 4.7110, 'lon': -74.0721, 'country': 'CO'},
        'Caracas, VE': {'lat': 10.4806, 'lon': -66.9036, 'country': 'VE'},
        'New York, US': {'lat': 40.7128, 'lon': -74.0060, 'country': 'US'},
        'London, UK': {'lat': 51.5074, 'lon': -0.1278, 'country': 'GB'},
        'Paris, FR': {'lat': 48.8566, 'lon': 2.3522, 'country': 'FR'},
        'Tokyo, JP': {'lat': 35.6762, 'lon': 139.6503, 'country': 'JP'},
        'Beijing, CN': {'lat': 39.9042, 'lon': 116.4074, 'country': 'CN'},
        'Mumbai, IN': {'lat': 19.0760, 'lon': 72.8777, 'country': 'IN'},
        'Sydney, AU': {'lat': -33.8688, 'lon': 151.2093, 'country': 'AU'},
    }
    
    # Adicionar cidades dinâmicas do session_state
    if 'dynamic_cities' in st.session_state:
        base_cities.update(st.session_state.dynamic_cities)
    
    return base_cities

def add_detected_city_to_options(location_data):
    """Adiciona uma cidade detectada às opções disponíveis."""
    city_key = f"{location_data['city']}, {location_data['country_code']}"
    
    # Inicializar se não existir
    if 'dynamic_cities' not in st.session_state:
        st.session_state.dynamic_cities = {}
    
    # Adicionar cidade se não existir
    if city_key not in st.session_state.dynamic_cities:
        st.session_state.dynamic_cities[city_key] = {
            'lat': location_data['lat'],
            'lon': location_data['lon'],
            'country': location_data['country_code'],
            'detected': True  # Marca como cidade detectada automaticamente
        }
        logger.info(f"Cidade {city_key} adicionada dinamicamente às opções")
    
    return city_key

def auto_collect_data_for_detected_city(city_key, location_data):
    """Coleta automaticamente dados para uma cidade detectada se não existir no banco."""
    try:
        # Verificar se já existem dados para esta cidade
        if not os.path.exists(Config.DATABASE_PATH):
            return False
            
        conn = sqlite3.connect(Config.DATABASE_PATH)
        city_name = city_key.split(',')[0].strip()
        
        # Verificar dados meteorológicos
        weather_check = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM weather_data WHERE city LIKE ?",
            conn, params=[f'%{city_name}%']
        )
        
        # Verificar dados de qualidade do ar  
        air_check = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM air_quality_data WHERE city LIKE ?",
            conn, params=[f'%{city_name}%']
        )
        
        conn.close()
        
        # Se não há dados, coletar automaticamente
        if weather_check.iloc[0]['count'] == 0 and air_check.iloc[0]['count'] == 0:
            logger.info(f"Coletando dados automaticamente para {city_key}")
            
            # Coletar dados usando subprocess para não travar a interface
            import subprocess
            cmd = [
                'python', 'data_collector.py',
                f'--city={city_key}',
                f'--lat={location_data["lat"]}',
                f'--lon={location_data["lon"]}',
                f'--country={location_data["country_code"]}'
            ]
            
            # Executar em background
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
            
    except Exception as e:
        logger.error(f"Erro ao verificar/coletar dados para {city_key}: {e}")
        return False
    
    return False

def main():
    """Função principal."""
    
    # Sidebar
    with st.sidebar:
        st.title("🌍 Climate Analytics")
        st.markdown("### Sistema de Monitoramento Climático")
        st.markdown("---")
        
        # Status das credenciais
        has_credentials = check_credentials()
        if has_credentials:
            st.success("✅ APIs configuradas")
        else:
            st.error("❌ APIs não configuradas")
        
        st.markdown("---")
        
        # Status do sistema
        st.markdown("### 📊 Status do Sistema")
        try:
            db_exists = os.path.exists(Config.DATABASE_PATH)
            st.write(f"**Banco de dados:** {'✅ Conectado' if db_exists else '❌ Não encontrado'}")
        except:
            st.write("**Banco de dados:** ❌ Erro ao verificar")
        
        st.write(f"**Credenciais:** {'✅ Válidas' if has_credentials else '❌ Pendentes'}")
        
        # Informações da localização ativa
        if 'selected_city' in st.session_state:
            st.markdown("---")
            st.markdown("### 📍 Localização Ativa")
            st.info(f"🎯 {st.session_state.selected_city}")
            
            if st.button("🔄 Resetar Localização"):
                if 'user_location' in st.session_state:
                    del st.session_state.user_location
                if 'selected_city' in st.session_state:
                    del st.session_state.selected_city
                st.success("Localização resetada! Atualize a página.")
        
        st.markdown("---")
          # Ações rápidas
        st.markdown("### 🔧 Ações Rápidas")
        if st.button("🔄 Coletar Dados Gerais"):
            with st.spinner("Coletando dados..."):
                result = os.system("python data_collector.py")
                if result == 0:
                    st.success("✅ Dados coletados!")
                else:
                    st.error("❌ Erro na coleta")
        
        if st.button("🌍 Resetar Localização"):
            # Limpar cache de localização para re-detectar
            if 'user_location' in st.session_state:
                del st.session_state.user_location
            if 'selected_city' in st.session_state:
                del st.session_state.selected_city
            if 'dynamic_cities' in st.session_state:
                del st.session_state.dynamic_cities
            st.success("Localização resetada! Atualize a página para re-detectar.")
        
        # Teste com localização específica
        with st.expander("🧪 Teste de Localização"):
            test_city = st.text_input("Cidade para teste:")
            test_country = st.text_input("País para teste:")
            test_lat = st.number_input("Latitude:", value=0.0, format="%.4f")
            test_lon = st.number_input("Longitude:", value=0.0, format="%.4f")
            
            if st.button("🔬 Aplicar Localização de Teste"):
                if test_city and test_country:
                    st.session_state.user_location = {
                        'city': test_city,
                        'country': test_country,
                        'country_code': test_country[:2].upper(),
                        'lat': test_lat,
                        'lon': test_lon,
                        'region': test_city
                    }
                    # Adicionar às cidades dinâmicas
                    test_key = add_detected_city_to_options(st.session_state.user_location)
                    st.session_state.selected_city = test_key
                    st.success(f"Localização de teste aplicada: {test_city}, {test_country}")
                    st.info("Atualize a página para ver as alterações")
        
        # Informações do projeto
        st.markdown("---")
        st.markdown("### ℹ️ Sobre o Projeto")
        st.markdown("""
        **Objetivo:** Monitoramento e análise de mudanças climáticas e qualidade do ar
        
        **APIs Utilizadas:**
        - OpenWeatherMap
        - IQAir AirVisual
        
        **Funcionalidades:**
        - Detecção automática de localização
        - Seleção manual de cidades
        - Busca livre por qualquer cidade
        - Coleta automática de dados
        - Análises estatísticas avançadas
        - Visualizações interativas
        - Sistema de alertas inteligente
        - Export de dados
        """)
        
        # Roadmap de melhorias
        with st.expander("🚀 Melhorias Implementadas"):
            st.markdown("""
            ✅ **Concluído:**
            - Detecção automática de localização via IP
            - Seleção manual de cidades globais
            - Busca livre por qualquer cidade
            - Coleta de dados específica por cidade
            - Gráficos interativos com zonas de referência
            - Sistema de alertas inteligente
            - Interface responsiva e moderna
            - Remoção de loops/recarregamentos
            - Download de dados em CSV
            
            🔄 **Próximas melhorias:**
            - Previsões meteorológicas
            - Mapas interativos
            - Histórico de tendências
            - Relatórios automatizados
            - Integração com mais APIs
            - Notificações push
            - Dashboard mobile
            """)
    
    # Conteúdo principal
    if check_credentials():
        show_dashboard()
    else:
        show_welcome_page()

if __name__ == "__main__":
    main()
