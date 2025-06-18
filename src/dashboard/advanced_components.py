"""
Componentes avançados para o dashboard Climate Analytics.
Inclui widgets interativos, métricas avançadas e visualizações inteligentes.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys
import os

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analysis.alert_system import ClimateAlertSystem, AlertLevel, AlertType
from src.analysis.correlation_analyzer import CorrelationAnalyzer

class DashboardComponents:
    """Componentes avançados para o dashboard."""
    
    @staticmethod
    def render_alert_panel(db_path: str):
        """Renderiza painel de alertas inteligentes."""
        st.subheader("🚨 Sistema de Alertas Inteligentes")
        
        try:
            alert_system = ClimateAlertSystem(db_path)
            alerts = alert_system.analyze_current_conditions()
            
            if not alerts:
                st.success("✅ Nenhum alerta ativo no momento")
                return
            
            # Resumo dos alertas
            summary = alert_system.get_alerts_summary()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Alertas", summary["total"])
            with col2:
                st.metric("Críticos", summary["critical_count"])
            with col3:
                emergency_count = summary["by_level"].get("emergency", 0)
                st.metric("Emergência", emergency_count)
            with col4:
                warning_count = summary["by_level"].get("warning", 0)
                st.metric("Avisos", warning_count)
            
            # Lista de alertas
            st.subheader("📋 Alertas Ativos")
            
            # Ordena alertas por prioridade
            priority_order = {
                AlertLevel.EMERGENCY: 4,
                AlertLevel.CRITICAL: 3,
                AlertLevel.WARNING: 2,
                AlertLevel.INFO: 1
            }
            
            alerts_sorted = sorted(alerts, key=lambda x: priority_order[x.level], reverse=True)
            
            for alert in alerts_sorted:
                # Cor baseada no nível
                color_map = {
                    AlertLevel.EMERGENCY: "🔴",
                    AlertLevel.CRITICAL: "🟠", 
                    AlertLevel.WARNING: "🟡",
                    AlertLevel.INFO: "🔵"
                }
                
                with st.expander(f"{color_map[alert.level]} {alert.title}", expanded=alert.level in [AlertLevel.EMERGENCY, AlertLevel.CRITICAL]):
                    st.write(f"**📍 Local:** {alert.location}")
                    st.write(f"**📊 Valor:** {alert.value}")
                    st.write(f"**⚠️ Limite:** {alert.threshold}")
                    st.write(f"**📝 Descrição:** {alert.description}")
                    
                    st.write("**💡 Recomendações:**")
                    for rec in alert.recommendations:
                        st.write(f"• {rec}")
                    
                    st.caption(f"⏰ {alert.timestamp.strftime('%d/%m/%Y %H:%M')}")
        
        except Exception as e:
            st.error(f"Erro ao carregar alertas: {e}")
    
    @staticmethod
    def render_correlation_analysis(db_path: str):
        """Renderiza análise de correlações avançada."""
        st.subheader("🔗 Análise de Correlações Avançada")
        
        try:
            analyzer = CorrelationAnalyzer(db_path)
            
            # Seletor de período
            col1, col2 = st.columns(2)
            with col1:
                days_back = st.selectbox(
                    "Período de análise",
                    [7, 15, 30, 60, 90],
                    index=2,
                    help="Número de dias para análise"
                )
            
            with col2:
                analysis_type = st.selectbox(
                    "Tipo de análise",
                    ["Completa", "Qualidade do Ar", "Padrões Temporais", "Clustering"],
                    help="Foco da análise"
                )
            
            # Carrega e analisa dados
            with st.spinner("Analisando correlações..."):
                df = analyzer.load_integrated_data(days_back)
                
                if df.empty:
                    st.warning("Dados insuficientes para análise")
                    return
                
                results = analyzer.analyze_correlations(df)
            
            # Exibe resultados baseados no tipo selecionado
            if analysis_type == "Completa" or analysis_type == "Qualidade do Ar":
                DashboardComponents._render_correlation_matrix(results)
                DashboardComponents._render_aqi_analysis(results)
            
            if analysis_type == "Completa" or analysis_type == "Padrões Temporais":
                DashboardComponents._render_temporal_patterns(results)
            
            if analysis_type == "Completa" or analysis_type == "Clustering":
                DashboardComponents._render_clustering_results(results)
            
            # Relatório textual
            if st.checkbox("📄 Gerar Relatório Detalhado"):
                report = analyzer.generate_correlation_report(results)
                st.markdown(report)
        
        except Exception as e:
            st.error(f"Erro na análise de correlações: {e}")
    
    @staticmethod
    def _render_correlation_matrix(results: Dict):
        """Renderiza matriz de correlação."""
        if 'correlation_matrix' not in results:
            return
        
        st.subheader("🎯 Matriz de Correlação")
        
        corr_matrix = results['correlation_matrix']
        
        # Heatmap de correlação
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Matriz de Correlação entre Variáveis Climáticas"
        )
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlações mais fortes
        if 'strong_correlations' in results and results['strong_correlations']:
            st.subheader("💪 Correlações Mais Fortes")
            
            strong_corrs = results['strong_correlations'][:10]  # Top 10
            
            corr_df = pd.DataFrame(strong_corrs)
            corr_df['correlation_abs'] = abs(corr_df['correlation'])
            
            # Gráfico de barras das correlações
            fig = px.bar(
                corr_df,
                x='correlation',
                y=[f"{row['var1']} × {row['var2']}" for _, row in corr_df.iterrows()],
                orientation='h',
                color='correlation',
                color_continuous_scale='RdBu_r',
                title="Top 10 Correlações Mais Fortes"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_aqi_analysis(results: Dict):
        """Renderiza análise específica de AQI."""
        if 'aqi_analysis' not in results:
            return
        
        aqi_data = results['aqi_analysis']
        
        if 'error' in aqi_data:
            st.warning(f"Análise de AQI: {aqi_data['error']}")
            return
        
        st.subheader("🌬️ Fatores que Influenciam a Qualidade do Ar")
        
        # Correlações com fatores meteorológicos
        if 'weather_correlations' in aqi_data:
            weather_corrs = aqi_data['weather_correlations']
            
            # Prepara dados para visualização
            factors = []
            correlations = []
            significances = []
            
            for factor, data in weather_corrs.items():
                factors.append(factor.replace('_', ' ').title())
                correlations.append(data['correlation'])
                significances.append("Significativo" if data['significant'] else "Não significativo")
            
            corr_df = pd.DataFrame({
                'Fator': factors,
                'Correlação': correlations,
                'Significância': significances
            })
            
            # Gráfico de correlações
            fig = px.bar(
                corr_df,
                x='Correlação',
                y='Fator',
                orientation='h',
                color='Correlação',
                color_continuous_scale='RdBu_r',
                title="Correlação entre Fatores Meteorológicos e Qualidade do Ar"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights textuais
            st.write("**💡 Principais Insights:**")
            
            top_factors = aqi_data.get('top_factors', [])
            for factor, data in top_factors[:3]:
                corr = data['correlation']
                if abs(corr) > 0.3:
                    if corr > 0:
                        relationship = "piora quando aumenta"
                    else:
                        relationship = "melhora quando aumenta"
                    
                    st.write(f"• **{factor.replace('_', ' ').title()}**: "
                           f"A qualidade do ar {relationship} (correlação: {corr:.3f})")
        
        # Análise por período do dia
        if 'by_time_period' in aqi_data:
            st.subheader("🕐 Qualidade do Ar por Período")
            
            period_data = aqi_data['by_time_period']
            periods = list(period_data.keys())
            means = [period_data[p]['mean'] for p in periods]
            
            fig = px.bar(
                x=periods,
                y=means,
                title="AQI Médio por Período do Dia",
                labels={'x': 'Período', 'y': 'AQI Médio'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_temporal_patterns(results: Dict):
        """Renderiza padrões temporais."""
        if 'temporal_patterns' not in results:
            return
        
        patterns = results['temporal_patterns']
        
        st.subheader("⏰ Padrões Temporais")
        
        # Padrões horários
        if 'hourly' in patterns:
            st.write("**📊 Variação por Hora do Dia**")
            
            hourly_data = patterns['hourly']
            
            # Seleciona variável para visualização
            available_vars = list(hourly_data.keys())
            if available_vars:
                selected_var = st.selectbox(
                    "Variável para análise horária",
                    available_vars,
                    key="hourly_var"
                )
                
                if selected_var in hourly_data:
                    hours = list(range(24))
                    means = [hourly_data[selected_var].get(str(h), {}).get('mean', 0) for h in hours]
                    
                    fig = px.line(
                        x=hours,
                        y=means,
                        title=f"{selected_var.replace('_', ' ').title()} - Variação Horária",
                        labels={'x': 'Hora do Dia', 'y': selected_var.replace('_', ' ').title()}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # Tendências
        if 'trends' in patterns:
            st.write("**📈 Tendências Identificadas**")
            
            trends = patterns['trends']
            
            for var, trend_data in trends.items():
                if trend_data['significant']:
                    direction = "📈 Crescente" if trend_data['slope'] > 0 else "📉 Decrescente"
                    r_squared = trend_data['r_squared']
                    
                    st.write(f"• **{var.replace('_', ' ').title()}**: {direction} "
                           f"(R² = {r_squared:.3f})")
    
    @staticmethod
    def _render_clustering_results(results: Dict):
        """Renderiza resultados do clustering."""
        if 'clustering' not in results or 'error' in results['clustering']:
            return
        
        clustering = results['clustering']
        
        st.subheader("🎯 Perfis de Condições Ambientais")
        
        cluster_stats = clustering['cluster_stats']
        
        # Visão geral dos clusters
        st.write("**📊 Distribuição dos Perfis**")
        
        cluster_names = []
        cluster_sizes = []
        cluster_descriptions = []
        
        for cluster_id, stats in cluster_stats.items():
            cluster_names.append(f"Perfil {cluster_id.split('_')[1]}")
            cluster_sizes.append(stats['percentage'])
            cluster_descriptions.append(", ".join(stats['characteristics']))
        
        # Gráfico de pizza
        fig = px.pie(
            values=cluster_sizes,
            names=cluster_names,
            title="Distribuição dos Perfis de Condições Ambientais"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detalhes dos clusters
        st.write("**🔍 Detalhes dos Perfis**")
        
        for i, (cluster_id, stats) in enumerate(cluster_stats.items()):
            with st.expander(f"Perfil {i+1} - {', '.join(stats['characteristics'])} ({stats['percentage']:.1f}%)"):
                st.write(f"**Tamanho:** {stats['size']} registros ({stats['percentage']:.1f}%)")
                
                st.write("**Características médias:**")
                means = stats['means']
                for var, value in means.items():
                    if isinstance(value, (int, float)):
                        st.write(f"• {var.replace('_', ' ').title()}: {value:.2f}")
    
    @staticmethod
    def render_environmental_health_index(db_path: str):
        """Renderiza índice de saúde ambiental personalizado."""
        st.subheader("🌿 Índice de Saúde Ambiental")
        
        try:
            # Busca dados mais recentes
            import sqlite3
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT w.city, w.country, w.temperature, w.humidity, 
                           w.pressure, w.wind_speed, a.aqi_us
                    FROM weather_data w
                    LEFT JOIN air_quality_data a ON w.city = a.city AND w.country = a.country
                    WHERE w.timestamp = (SELECT MAX(timestamp) FROM weather_data)
                    LIMIT 1
                """
                
                cursor.execute(query)
                row = cursor.fetchone()
                
                if not row:
                    st.warning("Dados não disponíveis")
                    return
                
                # Calcula índice personalizado
                temp = row[2] or 20
                humidity = row[3] or 50
                pressure = row[4] or 1013
                wind = row[5] or 5
                aqi = row[6] or 50
                
                # Componentes do índice (0-100)
                temp_score = max(0, 100 - abs(temp - 22) * 3)  # Ótimo em ~22°C
                humidity_score = max(0, 100 - abs(humidity - 50) * 1.5)  # Ótimo em ~50%
                pressure_score = max(0, 100 - abs(pressure - 1013) * 0.2)  # Pressão padrão
                wind_score = min(100, max(0, 100 - (wind - 3) * 8))  # Brisa suave ideal
                air_score = max(0, 100 - aqi * 1.5)  # Quanto menor AQI, melhor
                
                # Índice geral (média ponderada)
                overall_index = (
                    temp_score * 0.2 +
                    humidity_score * 0.15 +
                    pressure_score * 0.1 +
                    wind_score * 0.15 +
                    air_score * 0.4  # Qualidade do ar tem maior peso
                )
                
                # Classificação
                if overall_index >= 80:
                    classification = "🌟 Excelente"
                    color = "green"
                elif overall_index >= 60:
                    classification = "😊 Bom"
                    color = "lightgreen"
                elif overall_index >= 40:
                    classification = "😐 Regular"
                    color = "yellow"
                elif overall_index >= 20:
                    classification = "😷 Ruim"
                    color = "orange"
                else:
                    classification = "🚨 Crítico"
                    color = "red"
                
                # Display principal
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.metric(
                        "Índice de Saúde Ambiental",
                        f"{overall_index:.1f}/100",
                        classification
                    )
                
                with col2:
                    # Gauge chart
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = overall_index,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "ISA"},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': color},
                            'steps': [
                                {'range': [0, 20], 'color': "red"},
                                {'range': [20, 40], 'color': "orange"},
                                {'range': [40, 60], 'color': "yellow"},
                                {'range': [60, 80], 'color': "lightgreen"},
                                {'range': [80, 100], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': overall_index
                            }
                        }
                    ))
                    
                    fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                
                # Componentes detalhados
                st.subheader("📊 Componentes do Índice")
                
                components = [
                    ("🌡️ Temperatura", temp_score, f"{temp}°C"),
                    ("💧 Umidade", humidity_score, f"{humidity}%"),
                    ("📊 Pressão", pressure_score, f"{pressure} hPa"),
                    ("💨 Vento", wind_score, f"{wind} m/s"),
                    ("🌬️ Qualidade do Ar", air_score, f"AQI {aqi}")
                ]
                
                for name, score, value in components:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(name)
                    with col2:
                        st.write(f"{score:.1f}/100")
                    with col3:
                        st.write(value)
                    
                    # Barra de progresso
                    st.progress(score / 100)
                
                # Recomendações baseadas no índice
                st.subheader("💡 Recomendações")
                
                if overall_index >= 80:
                    st.success("Condições excelentes para atividades ao ar livre!")
                elif overall_index >= 60:
                    st.success("Boas condições. Aproveite para atividades externas.")
                elif overall_index >= 40:
                    st.warning("Condições regulares. Atividades moderadas são recomendadas.")
                elif overall_index >= 20:
                    st.warning("Condições ruins. Limite atividades ao ar livre.")
                else:
                    st.error("Condições críticas. Evite exposição externa.")
                
        except Exception as e:
            st.error(f"Erro ao calcular índice: {e}")
    
    @staticmethod
    def render_forecast_panel(db_path: str):
        """Renderiza painel de previsões inteligentes."""
        st.subheader("🔮 Previsões Inteligentes")
        
        try:
            # Por enquanto, simulação de previsão baseada em tendências
            import sqlite3
            
            with sqlite3.connect(db_path) as conn:
                query = """
                    SELECT temperature, humidity, aqi_us, timestamp
                    FROM weather_data w
                    LEFT JOIN air_quality_data a ON w.city = a.city AND w.country = a.country
                    WHERE datetime(w.timestamp) >= datetime('now', '-7 days')
                    ORDER BY w.timestamp
                """
                
                df = pd.read_sql_query(query, conn)
                
                if len(df) < 5:
                    st.warning("Dados insuficientes para previsão")
                    return
                
                # Previsão simples baseada em tendência linear
                from scipy import stats
                
                # Prepara dados
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.dropna()
                
                if len(df) < 3:
                    st.warning("Dados insuficientes para previsão")
                    return
                
                # Converte timestamp para número para regressão
                df['time_numeric'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()
                
                # Previsões para as próximas 24 horas
                future_times = []
                future_temps = []
                future_humidity = []
                future_aqi = []
                
                for i in range(24):  # 24 horas
                    future_time = df['timestamp'].max() + timedelta(hours=i+1)
                    future_times.append(future_time)
                    
                    future_numeric = (future_time - df['timestamp'].min()).total_seconds()
                    
                    # Previsão de temperatura
                    if 'temperature' in df.columns and not df['temperature'].isna().all():
                        slope, intercept, _, _, _ = stats.linregress(df['time_numeric'], df['temperature'])
                        future_temp = slope * future_numeric + intercept
                        future_temps.append(future_temp)
                    
                    # Previsão de umidade
                    if 'humidity' in df.columns and not df['humidity'].isna().all():
                        slope, intercept, _, _, _ = stats.linregress(df['time_numeric'], df['humidity'])
                        future_hum = slope * future_numeric + intercept
                        future_humidity.append(max(0, min(100, future_hum)))  # Limita entre 0-100
                    
                    # Previsão de AQI
                    if 'aqi_us' in df.columns and not df['aqi_us'].isna().all():
                        slope, intercept, _, _, _ = stats.linregress(df['time_numeric'], df['aqi_us'].dropna())
                        future_aqi_val = slope * future_numeric + intercept
                        future_aqi.append(max(0, future_aqi_val))  # AQI não pode ser negativo
                
                # Visualização das previsões
                fig = make_subplots(
                    rows=3, cols=1,
                    subplot_titles=('Temperatura', 'Umidade', 'Qualidade do Ar (AQI)'),
                    vertical_spacing=0.1
                )
                
                # Histórico + Previsão Temperatura
                if future_temps:
                    # Dados históricos
                    fig.add_trace(
                        go.Scatter(
                            x=df['timestamp'],
                            y=df['temperature'],
                            mode='lines+markers',
                            name='Temperatura (Histórico)',
                            line=dict(color='blue')
                        ),
                        row=1, col=1
                    )
                    
                    # Previsão
                    fig.add_trace(
                        go.Scatter(
                            x=future_times,
                            y=future_temps,
                            mode='lines+markers',
                            name='Temperatura (Previsão)',
                            line=dict(color='lightblue', dash='dash')
                        ),
                        row=1, col=1
                    )
                
                # Umidade
                if future_humidity:
                    fig.add_trace(
                        go.Scatter(
                            x=df['timestamp'],
                            y=df['humidity'],
                            mode='lines+markers',
                            name='Umidade (Histórico)',
                            line=dict(color='green'),
                            showlegend=False
                        ),
                        row=2, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=future_times,
                            y=future_humidity,
                            mode='lines+markers',
                            name='Umidade (Previsão)',
                            line=dict(color='lightgreen', dash='dash'),
                            showlegend=False
                        ),
                        row=2, col=1
                    )
                
                # AQI
                if future_aqi:
                    fig.add_trace(
                        go.Scatter(
                            x=df['timestamp'],
                            y=df['aqi_us'],
                            mode='lines+markers',
                            name='AQI (Histórico)',
                            line=dict(color='red'),
                            showlegend=False
                        ),
                        row=3, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=future_times,
                            y=future_aqi,
                            mode='lines+markers',
                            name='AQI (Previsão)',
                            line=dict(color='pink', dash='dash'),
                            showlegend=False
                        ),
                        row=3, col=1
                    )
                
                fig.update_layout(height=800, title_text="Previsões para as Próximas 24 Horas")
                st.plotly_chart(fig, use_container_width=True)
                
                # Alertas de previsão
                if future_aqi:
                    max_aqi_forecast = max(future_aqi)
                    if max_aqi_forecast > 100:
                        st.warning(f"⚠️ Previsão: Qualidade do ar pode piorar (AQI até {max_aqi_forecast:.0f})")
                    elif max_aqi_forecast < 50:
                        st.success("✅ Previsão: Boa qualidade do ar esperada")
                
                st.info("💡 **Nota:** Previsões baseadas em tendências dos últimos 7 dias. Para previsões mais precisas, considere integrar APIs meteorológicas especializadas.")
        
        except Exception as e:
            st.error(f"Erro ao gerar previsões: {e}")
            import traceback
            st.text(traceback.format_exc())
