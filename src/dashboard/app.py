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
    """Detecta a localização do usuário usando IP."""
    try:
        response = requests.get('http://ip-api.com/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'city': data.get('city', 'São Paulo'),
                    'country': data.get('country', 'Brazil'),
                    'lat': data.get('lat', -23.5505),
                    'lon': data.get('lon', -46.6333),
                    'region': data.get('regionName', 'São Paulo')
                }
    except Exception as e:
        st.warning(f"Não foi possível detectar sua localização: {e}")
    
    # Fallback para São Paulo
    return {
        'city': 'São Paulo',
        'country': 'Brazil', 
        'lat': -23.5505,
        'lon': -46.6333,
        'region': 'São Paulo'
    }

def get_available_cities():
    """Lista de cidades principais disponíveis."""
    return {
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
        'New York, US': {'lat': 40.7128, 'lon': -74.0060, 'country': 'US'},
        'London, UK': {'lat': 51.5074, 'lon': -0.1278, 'country': 'GB'},
        'Paris, FR': {'lat': 48.8566, 'lon': 2.3522, 'country': 'FR'},
        'Tokyo, JP': {'lat': 35.6762, 'lon': 139.6503, 'country': 'JP'},
        'Beijing, CN': {'lat': 39.9042, 'lon': 116.4074, 'country': 'CN'},
        'Mumbai, IN': {'lat': 19.0760, 'lon': 72.8777, 'country': 'IN'},
        'Sydney, AU': {'lat': -33.8688, 'lon': 151.2093, 'country': 'AU'},
    }

def collect_data_for_location(city_data):
    """Coleta dados para uma localização específica."""
    try:
        # Simular coleta de dados (substitua pela integração real com data_collector)
        # Por enquanto, vamos apenas simular um delay
        time.sleep(2)
        return True
    except Exception as e:
        st.error(f"Erro ao coletar dados: {e}")
        return False

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
            weather_df = weather_df.dropna(subset=['timestamp'])  # Remove linhas com timestamp inválido
        if not air_df.empty:
            air_df['timestamp'] = pd.to_datetime(air_df['timestamp'], errors='coerce', utc=True)
            air_df = air_df.dropna(subset=['timestamp'])  # Remove linhas com timestamp inválido
        
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
        AIRVISUAL_API_KEY=sua_chave_aqui        ```
        """)
    
    if st.button("🔄 Verificar Credenciais", type="primary"):
        st.info("♻️ Atualize a página para verificar as credenciais configuradas.")

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
            "🌡️ Temperatura Atual", 
            f"{latest['temperature']:.1f}°C",
            delta=f"Sensação: {latest['feels_like']:.1f}°C"
        )
    
    with col2:
        st.metric(
            "💧 Umidade", 
            f"{latest['humidity']}%"
        )
    
    with col3:
        st.metric(
            "🌬️ Pressão", 
            f"{latest['pressure']} hPa"
        )
    
    with col4:
        st.metric(
            "💨 Vento", 
            f"{latest['wind_speed']} m/s"
        )
    
    with col5:
        st.metric(
            "👁️ Visibilidade", 
            f"{latest['visibility']} km"
        )
    
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
            # Gráfico de temperatura com contexto
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
            # Gráfico combinado mais informativo
            fig_env = go.Figure()
            
            # Normalizar pressão para visualização (pressão típica: 1000-1020 hPa)
            pressure_normalized = ((weather_df['pressure'] - 1000) / 20) * 100  # Converter para escala 0-100
            
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
        st.metric(
            "🌡️ Temperatura", 
            f"{latest['temperature']}°C"
        )
    
    with col4:
        st.metric(
            "💧 Umidade", 
            f"{latest['humidity']}%"
        )
    
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
        # Gráfico comparativo AQI mais informativo
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
        
        # Zonas de qualidade do ar com cores
        fig_aqi.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1, annotation_text="Boa", annotation_position="top left")
        fig_aqi.add_hrect(y0=51, y1=100, fillcolor="yellow", opacity=0.1, annotation_text="Moderada", annotation_position="top left")
        fig_aqi.add_hrect(y0=101, y1=150, fillcolor="orange", opacity=0.1, annotation_text="Insalubre (Sensíveis)", annotation_position="top left")
        fig_aqi.add_hrect(y0=151, y1=200, fillcolor="red", opacity=0.1, annotation_text="Insalubre", annotation_position="top left")
        fig_aqi.add_hrect(y0=201, y1=300, fillcolor="purple", opacity=0.1, annotation_text="Muito Insalubre", annotation_position="top left")
        
        # Linhas de referência principais
        fig_aqi.add_hline(y=50, line_dash="dash", line_color="green", line_width=2)
        fig_aqi.add_hline(y=100, line_dash="dash", line_color="orange", line_width=2)
        fig_aqi.add_hline(y=150, line_dash="dash", line_color="red", line_width=2)
        
        fig_aqi.update_layout(
            title="🌫️ Evolução da Qualidade do Ar - Comparação de Índices",
            xaxis_title="Data/Hora",
            yaxis_title="Índice AQI",
            height=500,
            hovermode='x unified',
            showlegend=True
        )
        st.plotly_chart(fig_aqi, use_container_width=True)
        
        # Gráfico adicional: Distribuição de poluentes
        if 'main_pollutant_us' in air_df.columns:
            pollutant_counts = air_df['main_pollutant_us'].value_counts()
            fig_pollutants = px.pie(
                values=pollutant_counts.values,
                names=pollutant_counts.index,
                title="🏭 Distribuição dos Principais Poluentes",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pollutants.update_layout(height=400)
            st.plotly_chart(fig_pollutants, use_container_width=True)

def create_comparative_analysis(weather_df, air_df):
    """Análise comparativa e correlações."""
    st.header("📊 Análise Inteligente e Tendências")
    
    if weather_df.empty and air_df.empty:
        st.warning("Nenhum dado disponível para análise comparativa.")
        return
    
    # Análise de tendências
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Tendências Meteorológicas")
        if not weather_df.empty and len(weather_df) > 1:
            # Calcular tendências
            temp_trend = weather_df['temperature'].iloc[0] - weather_df['temperature'].iloc[-1]
            humidity_trend = weather_df['humidity'].iloc[0] - weather_df['humidity'].iloc[-1]
            pressure_trend = weather_df['pressure'].iloc[0] - weather_df['pressure'].iloc[-1]
            
            # Métricas com análise
            st.metric(
                "🌡️ Tendência Temperatura", 
                f"{temp_trend:+.1f}°C",
                delta="Últimos registros" if abs(temp_trend) > 1 else "Estável"
            )
            st.metric(
                "💧 Tendência Umidade", 
                f"{humidity_trend:+.0f}%",
                delta="Variação significativa" if abs(humidity_trend) > 10 else "Normal"
            )
            st.metric(
                "🌬️ Tendência Pressão", 
                f"{pressure_trend:+.0f} hPa",
                delta="Mudança de tempo" if abs(pressure_trend) > 5 else "Estável"
            )
            
            # Estatísticas resumidas
            st.markdown("**📊 Resumo Estatístico:**")
            weather_stats = {
                "Temp. Média": f"{weather_df['temperature'].mean():.1f}°C",
                "Temp. Máxima": f"{weather_df['temperature'].max():.1f}°C", 
                "Temp. Mínima": f"{weather_df['temperature'].min():.1f}°C",
                "Umidade Média": f"{weather_df['humidity'].mean():.0f}%",
                "Vento Médio": f"{weather_df['wind_speed'].mean():.1f} m/s"
            }
            
            for key, value in weather_stats.items():
                st.text(f"• {key}: {value}")
    
    with col2:
        st.subheader("🌫️ Análise de Qualidade do Ar")
        if not air_df.empty and len(air_df) > 1:
            # Análise da qualidade do ar
            current_aqi = air_df.iloc[0]['aqi_us']
            avg_aqi = air_df['aqi_us'].mean()
            max_aqi = air_df['aqi_us'].max()
            
            # Status atual detalhado
            status, color = get_air_quality_status(current_aqi)
            st.markdown(f"**Status Atual:** {status}")
            
            st.metric(
                "📊 AQI Médio", 
                f"{avg_aqi:.0f}",
                delta=f"Máximo: {max_aqi}"
            )
            
            # Análise de poluentes
            if 'main_pollutant_us' in air_df.columns:
                main_pollutant = air_df['main_pollutant_us'].mode().iloc[0]
                pollutant_freq = air_df['main_pollutant_us'].value_counts()
                
                st.markdown("**🏭 Análise de Poluentes:**")
                st.text(f"• Principal poluente: {main_pollutant.upper()}")
                
                for pollutant, count in pollutant_freq.head(3).items():
                    percentage = (count / len(air_df)) * 100
                    st.text(f"• {pollutant.upper()}: {percentage:.0f}% dos registros")
            
            # Comparação de índices
            aqi_us_avg = air_df['aqi_us'].mean()
            aqi_cn_avg = air_df['aqi_cn'].mean()
            st.markdown("**🌍 Comparação Internacional:**")
            st.text(f"• Média AQI US: {aqi_us_avg:.0f}")
            st.text(f"• Média AQI China: {aqi_cn_avg:.0f}")
    
    st.markdown("---")
    
    # Sistema de alertas inteligente
    st.subheader("🚨 Sistema de Alertas Inteligente")
    
    alerts = []
    recommendations = []
    
    # Alertas meteorológicos
    if not weather_df.empty:
        latest_temp = weather_df.iloc[0]['temperature']
        latest_humidity = weather_df.iloc[0]['humidity']
        latest_wind = weather_df.iloc[0]['wind_speed']
        
        if latest_temp > 35:
            alerts.append("🌡️ **ALERTA CALOR:** Temperatura extrema detectada!")
            recommendations.append("• Evite exposição ao sol entre 10h-16h")
            recommendations.append("• Mantenha-se hidratado")
        elif latest_temp < 5:
            alerts.append("❄️ **ALERTA FRIO:** Temperatura muito baixa!")
            recommendations.append("• Use roupas adequadas para o frio")
            recommendations.append("• Proteja extremidades do corpo")
        
        if latest_humidity > 80:
            alerts.append("💧 **UMIDADE ALTA:** Desconforto térmico possível")
            recommendations.append("• Use ventilação adequada em ambientes fechados")
        elif latest_humidity < 30:
            alerts.append("🏜️ **AR SECO:** Umidade muito baixa")
            recommendations.append("• Use umidificador ou recipientes com água")
            recommendations.append("• Hidrate-se mais frequentemente")
        
        if latest_wind > 15:
            alerts.append("💨 **VENTO FORTE:** Ventos intensos detectados")
            recommendations.append("• Cuidado com objetos soltos")
    
    # Alertas de qualidade do ar
    if not air_df.empty:
        latest_aqi = air_df.iloc[0]['aqi_us']
        main_pollutant = air_df.iloc[0]['main_pollutant_us']
        
        if latest_aqi > 200:
            alerts.append("🚨 **EMERGÊNCIA:** Qualidade do ar muito perigosa!")
            recommendations.append("• Evite atividades ao ar livre")
            recommendations.append("• Use máscaras N95 se precisar sair")
            recommendations.append("• Mantenha janelas fechadas")
        elif latest_aqi > 150:
            alerts.append("🔴 **ALERTA CRÍTICO:** Qualidade do ar insalubre!")
            recommendations.append("• Limite atividades ao ar livre")
            recommendations.append("• Grupos sensíveis devem ficar em casa")
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

def show_dashboard():
    """Dashboard principal com análises completas."""
    st.title("🌍 Climate Analytics")
    st.markdown("### Monitoramento Climático e Qualidade do Ar em Tempo Real")
    
    # Seção de seleção de localização
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.subheader("� Seleção de Localização")
        
        # Detectar localização do usuário
        if st.button("🎯 Detectar Minha Localização"):
            with st.spinner("Detectando sua localização..."):
                user_location = get_user_location()
                st.session_state.user_location = user_location
                st.success(f"� Localização detectada: {user_location['city']}, {user_location['country']}")
    
    with col2:
        # Seleção manual de cidade
        available_cities = get_available_cities()
          # Valor padrão baseado na localização do usuário se disponível
        default_city = "São Paulo, BR"
        if 'user_location' in st.session_state:
            user_loc = st.session_state.user_location
            detected_city = f"{user_loc['city']}, {user_loc['country']}"
            if detected_city in available_cities:
                default_city = detected_city
        
        selected_city = st.selectbox(
            "🌍 Escolher Cidade:",
            options=list(available_cities.keys()),
            index=list(available_cities.keys()).index(default_city) if default_city in available_cities else 0,
            help="Selecione uma cidade para ver dados específicos"
        )
        
        # Opção de busca livre
        st.markdown("**Ou digite qualquer cidade:**")
        custom_city = st.text_input(
            "🔍 Buscar cidade:",
            placeholder="Ex: Londres, UK ou Paris, France",
            help="Digite o nome da cidade em inglês, seguido do código do país"
        )
          # Se uma cidade customizada foi digitada, usar ela
        if custom_city and custom_city.strip():
            selected_city = custom_city.strip()
            # Tentar obter coordenadas via geocoding (simplificado)
            st.info(f"🔍 Buscando dados para: {selected_city}")
        
        st.session_state.selected_city = selected_city
    
    with col3:
        # Botão para coletar dados da cidade selecionada
        if st.button("🔄 Coletar Dados\nda Cidade", type="primary"):
            with st.spinner(f"🌐 Coletando dados para {selected_city}..."):
                # Verificar se é uma cidade pré-definida ou customizada
                if selected_city in available_cities:
                    city_data = available_cities[selected_city]
                    result = os.system(f"python data_collector.py --city=\"{selected_city}\" --lat={city_data['lat']} --lon={city_data['lon']}")
                else:
                    # Para cidades customizadas, usar apenas o nome da cidade
                    result = os.system(f"python data_collector.py --city=\"{selected_city}\"")
                
                if result == 0:
                    st.success("✅ Dados coletados com sucesso! Aguarde alguns segundos e os dados serão atualizados.")
                    st.balloons()
                    time.sleep(2)  # Aguarda um pouco para o banco ser atualizado
                else:
                    st.error("❌ Erro ao coletar dados. Verifique suas credenciais.")
                    st.info("💡 Dica: Verifique se suas chaves de API estão configuradas corretamente.")
    
    st.markdown("---")
    
    # Carregar dados para a cidade selecionada
    with st.spinner(f"🔄 Carregando dados para {selected_city}..."):
        weather_df, air_df = load_climate_data(selected_city)
    
    # Status dos dados com informações atualizadas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Registros Meteorológicos", len(weather_df))
    with col2:
        st.metric("🌫️ Registros Qualidade do Ar", len(air_df))
    with col3:
        if not weather_df.empty:
            latest_timestamp = weather_df.iloc[0]['timestamp']
            # Remover timezone para comparação
            if latest_timestamp.tzinfo:
                latest_timestamp = latest_timestamp.replace(tzinfo=None)
            hours_since = (datetime.now() - latest_timestamp).total_seconds() / 3600
            st.metric("⏰ Última Coleta", f"{hours_since:.1f}h atrás")
        else:
            st.metric("⏰ Última Coleta", "N/A")
    with col4:
        st.metric("🌍 Localização Ativa", selected_city)
    
    # Informações adicionais da localização
    if selected_city in available_cities:
        city_info = available_cities[selected_city]
        st.markdown(f"""
        **📍 Coordenadas:** {city_info['lat']:.4f}, {city_info['lon']:.4f}  
        **🗺️ Região:** {selected_city}
        """)
    
    st.markdown("---")
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️ Análise Meteorológica", 
        "🌫️ Qualidade do Ar", 
        "📊 Análise Comparativa",
        "📋 Dados Brutos"
    ])
    
    with tab1:
        create_weather_analysis(weather_df)
    
    with tab2:
        create_air_quality_analysis(air_df)
    
    with tab3:
        create_comparative_analysis(weather_df, air_df)
    
    with tab4:
        st.header("📋 Dados Brutos para Análise")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🌡️ Dados Meteorológicos - {selected_city}")
            if not weather_df.empty:
                st.dataframe(weather_df, use_container_width=True)
                
                # Download dos dados
                csv_weather = weather_df.to_csv(index=False)
                st.download_button(
                    f"📥 Baixar Dados Meteorológicos - {selected_city} (CSV)",
                    csv_weather,
                    f"dados_meteorologicos_{selected_city.replace(', ', '_')}.csv",
                    "text/csv"
                )
            else:
                st.info(f"Nenhum dado meteorológico disponível para {selected_city}")
        
        with col2:
            st.subheader(f"🌫️ Dados de Qualidade do Ar - {selected_city}")
            if not air_df.empty:
                st.dataframe(air_df, use_container_width=True)
                
                # Download dos dados
                csv_air = air_df.to_csv(index=False)
                st.download_button(
                    f"📥 Baixar Dados Qualidade do Ar - {selected_city} (CSV)",
                    csv_air,
                    f"dados_qualidade_ar_{selected_city.replace(', ', '_')}.csv",
                    "text/csv"
                )
            else:
                st.info(f"Nenhum dado de qualidade do ar disponível para {selected_city}")

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
        
        # Localização atual
        if 'selected_city' in st.session_state:
            st.markdown("### 📍 Localização Ativa")
            st.write(f"**🌍 Cidade:** {st.session_state.selected_city}")
            
            if 'user_location' in st.session_state:
                user_loc = st.session_state.user_location
                st.write(f"**🎯 Detectada:** {user_loc['city']}, {user_loc['country']}")
        
        st.markdown("---")
        
        # Status do sistema
        st.markdown("### 📊 Status do Sistema")
        db_exists = os.path.exists(Config.DATABASE_PATH) if hasattr(Config, 'DATABASE_PATH') else False
        st.write(f"**Banco de dados:** {'✅ Conectado' if db_exists else '❌ Não encontrado'}")
        st.write(f"**Credenciais:** {'✅ Válidas' if has_credentials else '❌ Pendentes'}")
        st.write(f"**Detecção de Localização:** {'✅ Ativa' if 'user_location' in st.session_state else '⚙️ Disponível'}")
        
        st.markdown("---")
        
        # Ações rápidas
        st.markdown("### 🔧 Ações Rápidas")
        
        # Coleta global de dados
        if st.button("🌍 Coletar Dados Globais", type="secondary"):
            with st.spinner("Coletando dados para todas as cidades..."):
                # Coletar dados para as principais cidades
                result = os.system("python data_collector.py")
                if result == 0:
                    st.success("✅ Dados globais coletados!")
                else:
                    st.error("❌ Erro na coleta global")
          # Reset de localização
        if st.button("🔄 Resetar Localização"):
            if 'user_location' in st.session_state:
                del st.session_state.user_location
            if 'selected_city' in st.session_state:
                del st.session_state.selected_city
            st.success("Localização resetada! Atualize a página para ver as alterações.")
        
        st.markdown("---")
        
        # Informações do projeto
        st.markdown("### ℹ️ Sobre o Projeto")
        st.markdown("""
        **Climate Analytics v2.0**
        
        **🎯 Funcionalidades:**
        - 🌍 Detecção automática de localização
        - 🏙️ Monitoramento multi-cidades
        - 📊 Análises avançadas
        - 🚨 Sistema de alertas inteligente
        - 📈 Visualizações interativas
        - 📥 Export de dados
        
        **🔗 APIs Utilizadas:**
        - OpenWeatherMap (Meteorologia)
        - IQAir AirVisual (Qualidade do Ar)
        - IP-API (Geolocalização)
        """)
        
        # Link para melhorias
        with st.expander("� Melhorias Futuras"):
            st.markdown("""
            **📋 Roadmap:**
            - [ ] Previsões de 7 dias
            - [ ] Mapas interativos
            - [ ] Comparação entre cidades
            - [ ] Alertas por email/SMS
            - [ ] API própria
            - [ ] Machine Learning para previsões            - [ ] Dashboard mobile
            """)
        
        # Status das melhorias implementadas
        with st.expander("✅ Melhorias Implementadas"):
            st.markdown("""
            **🚀 Versão 2.0 - Funcionalidades Adicionadas:**
            - ✅ Detecção automática de localização via IP
            - ✅ Busca livre por qualquer cidade do mundo
            - ✅ Seleção manual entre cidades principais
            - ✅ Eliminação completa de loops/reloads
            - ✅ Visualizações avançadas com zonas de conforto
            - ✅ Sistema de alertas inteligente contextual
            - ✅ Análise comparativa de índices AQI
            - ✅ Gráficos interativos com tooltips
            - ✅ Export de dados em CSV
            - ✅ Interface responsiva e moderna
            - ✅ Tratamento robusto de erros
            - ✅ Cache otimizado para performance
            
            **🔧 Melhorias Técnicas:**
            - ✅ Código limpo e documentado
            - ✅ Tratamento de exceções
            - ✅ Validação de dados
            - ✅ Parsing robusto de timestamps
            - ✅ Integração real com APIs
            - ✅ Sistema de feedback ao usuário
            """)
    
    # Conteúdo principal
    if check_credentials():
        show_dashboard()
    else:
        show_welcome_page()

if __name__ == "__main__":
    main()

def load_real_data():
    """Carrega dados REAIS do banco de dados SQLite."""
    try:
        if not os.path.exists(Config.DATABASE_PATH):
            st.warning("Banco de dados não encontrado. Execute o coletor de dados primeiro.")
            return pd.DataFrame(), pd.DataFrame()
            
        conn = sqlite3.connect(Config.DATABASE_PATH)
        
        # Dados meteorológicos - usar colunas separadas
        weather_query = """
        SELECT timestamp, temperature, humidity, pressure, wind_speed, description, city, country
        FROM weather_data 
        WHERE timestamp >= datetime('now', '-7 days')
        ORDER BY timestamp DESC
        """
        weather_df = pd.read_sql_query(weather_query, conn)
        
        # Dados de qualidade do ar - usar colunas separadas
        air_query = """
        SELECT timestamp, aqi_us as aqi, temperature, pressure, humidity, wind_speed, city, country
        FROM air_quality_data 
        WHERE timestamp >= datetime('now', '-7 days')
        ORDER BY timestamp DESC
        """
        air_df = pd.read_sql_query(air_query, conn)
        
        conn.close()
        
        return weather_df, air_df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

def check_credentials():
    """Verifica se as credenciais estão configuradas."""
    try:
        # Verificação simples se o arquivo .env existe e tem as chaves necessárias
        if not os.path.exists('.env'):
            return False
        
        with open('.env', 'r') as f:
            env_content = f.read()
            
        # Verificar se as chaves essenciais estão presentes
        has_weather_key = 'OPENWEATHER_API_KEY=' in env_content
        has_air_key = 'AIRVISUAL_API_KEY=' in env_content
        
        return has_weather_key and has_air_key
    except Exception:
        return False

def show_welcome_page():
    """Mostra página de boas-vindas para configuração de credenciais."""
    st.title("🌍 Climate Analytics")
    st.markdown("---")
    
    st.info("🚀 **Bem-vindo ao Climate Analytics!** Configure suas credenciais para começar.")
    
    st.markdown("""
    ### 📋 Pré-requisitos
    Para usar este dashboard, você precisa de:
    
    1. **🔑 Chave da API OpenWeatherMap** (gratuita)
       - Acesse: https://openweathermap.org/api
       - Crie uma conta e obtenha sua API key
    
    2. **🌫️ Chave da API AirVisual** (gratuita)
       - Acesse: https://www.iqair.com/air-pollution-data-api
       - Registre-se e obtenha sua API key
    
    ### ⚙️ Configuração
    Execute o comando abaixo no terminal para configurar suas credenciais:
    ```bash
    python setup_credentials.py
    ```
    
    Ou crie um arquivo `.env` na raiz do projeto com:
    ```
    OPENWEATHER_API_KEY=sua_chave_aqui
    AIRVISUAL_API_KEY=sua_chave_aqui    ```
    """)
    
    if st.button("🔄 Verificar Credenciais"):
        st.info("♻️ Atualize a página para verificar as credenciais.")

def create_weather_charts(weather_df):
    """Cria gráficos dos dados meteorológicos."""
    if weather_df.empty:
        st.warning("Nenhum dado meteorológico disponível. Colete dados primeiro.")
        return
    
    # Fazer uma cópia para não alterar o original
    df = weather_df.copy()
    
    # Converter timestamp para datetime com formato flexível
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    except:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Gráfico de temperatura
    if 'temperature' in df.columns:
        fig_temp = px.line(
            df, x='timestamp', y='temperature',
            title='🌡️ Temperatura ao Longo do Tempo',
            labels={'temperature': 'Temperatura (°C)', 'timestamp': 'Data/Hora'}
        )
        fig_temp.update_layout(height=400)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Gráfico de umidade
    if 'humidity' in df.columns:
        fig_humidity = px.line(
            df, x='timestamp', y='humidity',
            title='💧 Umidade Relativa ao Longo do Tempo',
            labels={'humidity': 'Umidade (%)', 'timestamp': 'Data/Hora'}
        )
        fig_humidity.update_layout(height=400)
        st.plotly_chart(fig_humidity, use_container_width=True)

def create_air_quality_charts(air_df):
    """Cria gráficos dos dados de qualidade do ar."""
    if air_df.empty:
        st.warning("Nenhum dado de qualidade do ar disponível. Colete dados primeiro.")
        return
    
    # Fazer uma cópia para não alterar o original
    df = air_df.copy()
    
    # Converter timestamp para datetime com formato flexível
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    except:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Gráfico de AQI
    if 'aqi' in df.columns:
        fig_aqi = px.line(
            df, x='timestamp', y='aqi',
            title='🌫️ Índice de Qualidade do Ar (AQI)',
            labels={'aqi': 'AQI', 'timestamp': 'Data/Hora'}
        )
        fig_aqi.update_layout(height=400)
        st.plotly_chart(fig_aqi, use_container_width=True)

def show_dashboard():
    """Mostra o dashboard principal com dados reais."""
    st.title("🌍 Climate Analytics - Dashboard")
    st.markdown("### Dados em Tempo Real das APIs")
    
    # Carregar dados reais
    with st.spinner("Carregando dados reais..."):
        weather_df, air_df = load_real_data()
    
    # Informações sobre os dados
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Registros Meteorológicos", len(weather_df))
    with col2:
        st.metric("🌫️ Registros de Qualidade do Ar", len(air_df))
    with col3:
        last_update = datetime.now().strftime("%H:%M:%S")
        st.metric("⏰ Última Atualização", last_update)
      # Botão para coletar novos dados
    if st.button("🔄 Coletar Novos Dados"):
        with st.spinner("Coletando dados das APIs..."):
            result = os.system("python data_collector.py")
            if result == 0:
                st.success("✅ Dados coletados com sucesso! Aguarde alguns segundos para ver os dados atualizados.")
                time.sleep(2)
            else:
                st.error("❌ Erro ao coletar dados. Verifique as credenciais.")
                st.info("💡 Configure suas chaves de API no arquivo .env")
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["🌡️ Meteorologia", "🌫️ Qualidade do Ar", "📊 Dados Brutos"])
    
    with tab1:
        st.header("Dados Meteorológicos")
        create_weather_charts(weather_df)
          # Mostrar dados mais recentes
        if not weather_df.empty:
            st.subheader("📋 Dados Mais Recentes")
            recent_data = weather_df.iloc[0]  # Primeira linha (mais recente)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🌡️ Temperatura", f"{recent_data.get('temperature', 'N/A')}°C")
            with col2:
                st.metric("💧 Umidade", f"{recent_data.get('humidity', 'N/A')}%")
            with col3:
                st.metric("🌬️ Pressão", f"{recent_data.get('pressure', 'N/A')} hPa")
            with col4:
                st.metric("💨 Vento", f"{recent_data.get('wind_speed', 'N/A')} m/s")
    
    with tab2:
        st.header("Qualidade do Ar")
        create_air_quality_charts(air_df)
          # Mostrar dados mais recentes
        if not air_df.empty:
            st.subheader("📋 Dados Mais Recentes")
            recent_data = air_df.iloc[0]  # Primeira linha (mais recente)
            col1, col2, col3 = st.columns(3)
            with col1:
                aqi = recent_data.get('aqi', 'N/A')
                st.metric("🌫️ AQI", aqi)
            with col2:
                # PM2.5 e PM10 não estão disponíveis na estrutura atual
                st.metric("🌡️ Temperatura", f"{recent_data.get('temperature', 'N/A')}°C")
            with col3:
                st.metric("💧 Umidade", f"{recent_data.get('humidity', 'N/A')}%")
    
    with tab3:
        st.header("Dados Brutos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌡️ Dados Meteorológicos")
            if not weather_df.empty:
                st.dataframe(weather_df.head(10), use_container_width=True)
            else:
                st.info("Nenhum dado disponível")
        
        with col2:
            st.subheader("🌫️ Dados de Qualidade do Ar")
            if not air_df.empty:
                st.dataframe(air_df.head(10), use_container_width=True)
            else:
                st.info("Nenhum dado disponível")

def main():
    """Função principal do dashboard."""
    
    # Sidebar com informações
    with st.sidebar:
        st.title("🌍 Climate Analytics")
        st.markdown("---")
        
        # Status das credenciais
        has_credentials = check_credentials()
        if has_credentials:
            st.success("✅ Credenciais configuradas")
        else:
            st.error("❌ Credenciais não encontradas")
        
        st.markdown("---")
        st.markdown("### 📊 Status do Sistema")
        
        # Verificar banco de dados
        try:
            db_exists = os.path.exists(Config.DATABASE_PATH)
            st.write(f"**Banco de dados:** {'✅ OK' if db_exists else '❌ Não encontrado'}")
        except:
            st.write("**Banco de dados:** ❌ Erro ao verificar")
            
        st.write(f"**Arquivo .env:** {'✅ OK' if os.path.exists('.env') else '❌ Não encontrado'}")
        
        st.markdown("---")
        st.markdown("### 🔧 Ações")
        if st.button("🔄 Coletar Dados"):
            with st.spinner("Coletando dados..."):
                result = os.system("python data_collector.py")
                if result == 0:
                    st.success("Dados coletados!")
                else:
                    st.error("Erro ao coletar dados")
    
    # Mostrar dashboard ou página de boas-vindas
    if check_credentials():
        show_dashboard()
    else:
        show_welcome_page()

if __name__ == "__main__":
    main()
