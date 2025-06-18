"""
Sistema avançado de análise de correlações entre fatores climáticos e qualidade do ar.
Identifica padrões complexos e relações entre diferentes variáveis ambientais.
"""
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CorrelationAnalyzer:
    """Analisador avançado de correlações climáticas."""
    
    def __init__(self, db_path: str):
        """
        Inicializa o analisador.
        
        Args:
            db_path: Caminho para o banco de dados
        """
        self.db_path = db_path
        self.scaler = StandardScaler()
    
    def load_integrated_data(self, days_back: int = 30) -> pd.DataFrame:
        """
        Carrega dados integrados de clima e qualidade do ar.
        
        Args:
            days_back: Número de dias para carregar
            
        Returns:
            DataFrame com dados integrados
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT 
                        w.timestamp,
                        w.city,
                        w.country,
                        w.temperature,
                        w.feels_like,
                        w.humidity,
                        w.pressure,
                        w.wind_speed,
                        w.wind_direction,
                        w.visibility,
                        w.clouds,
                        a.aqi_us,
                        a.aqi_cn,
                        a.main_pollutant_us,
                        strftime('%H', w.timestamp) as hour,
                        strftime('%w', w.timestamp) as day_of_week,
                        CASE 
                            WHEN CAST(strftime('%H', w.timestamp) AS INTEGER) BETWEEN 6 AND 18 
                            THEN 'day' 
                            ELSE 'night' 
                        END as time_period
                    FROM weather_data w
                    LEFT JOIN air_quality_data a ON 
                        w.city = a.city AND 
                        w.country = a.country AND
                        date(w.timestamp) = date(a.timestamp)
                    WHERE datetime(w.timestamp) >= ?
                    ORDER BY w.timestamp
                """
                
                df = pd.read_sql_query(query, conn, params=[cutoff_date.isoformat()])
                
                # Preprocessamento
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['hour'].astype(int)
                df['day_of_week'] = df['day_of_week'].astype(int)
                
                # Features derivadas
                df['temp_range'] = abs(df['temperature'] - df['feels_like'])
                df['comfort_index'] = self._calculate_comfort_index(df)
                df['weather_stability'] = self._calculate_stability_index(df)
                
                logger.info(f"Carregados {len(df)} registros para análise")
                return df
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados integrados: {e}")
            return pd.DataFrame()
    
    def _calculate_comfort_index(self, df: pd.DataFrame) -> pd.Series:
        """Calcula índice de conforto baseado em temperatura e umidade."""
        # Fórmula simplificada do Heat Index
        T = df['temperature']
        H = df['humidity']
        
        # Índice de conforto normalizado (0-100)
        comfort = 100 - abs(T - 22) * 2 - abs(H - 50) * 0.5
        return comfort.clip(0, 100)
    
    def _calculate_stability_index(self, df: pd.DataFrame) -> pd.Series:
        """Calcula índice de estabilidade atmosférica."""
        # Baseado em pressão e vento
        pressure_norm = (df['pressure'] - 1013.25) / 50  # Normaliza em torno da pressão padrão
        wind_factor = df['wind_speed'] / 20  # Normaliza vento
        
        stability = 50 + pressure_norm * 20 - wind_factor * 30
        return stability.clip(0, 100)
    
    def analyze_correlations(self, df: pd.DataFrame) -> Dict:
        """
        Analisa correlações entre variáveis.
        
        Args:
            df: DataFrame com dados para análise
            
        Returns:
            Dicionário com resultados das análises
        """
        results = {}
        
        # Seleciona colunas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col not in ['hour', 'day_of_week']]
        
        if len(numeric_cols) < 2:
            return {"error": "Dados insuficientes para análise"}
        
        # Matriz de correlação
        corr_matrix = df[numeric_cols].corr()
        results['correlation_matrix'] = corr_matrix
        
        # Correlações mais fortes
        strong_correlations = self._find_strong_correlations(corr_matrix)
        results['strong_correlations'] = strong_correlations
        
        # Análise específica AQI vs fatores meteorológicos
        if 'aqi_us' in df.columns:
            aqi_correlations = self._analyze_aqi_correlations(df)
            results['aqi_analysis'] = aqi_correlations
        
        # Análise temporal
        temporal_analysis = self._analyze_temporal_patterns(df)
        results['temporal_patterns'] = temporal_analysis
        
        # Clustering de condições ambientais
        if len(df) > 50:
            cluster_analysis = self._perform_clustering(df, numeric_cols)
            results['clustering'] = cluster_analysis
        
        # Análise de PCA
        if len(numeric_cols) > 3:
            pca_analysis = self._perform_pca(df, numeric_cols)
            results['pca'] = pca_analysis
        
        return results
    
    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
        """Encontra correlações fortes."""
        strong_corrs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_corrs.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': corr_value,
                        'strength': 'strong' if abs(corr_value) >= 0.8 else 'moderate',
                        'direction': 'positive' if corr_value > 0 else 'negative'
                    })
        
        # Ordena por força da correlação
        strong_corrs.sort(key=lambda x: abs(x['correlation']), reverse=True)
        return strong_corrs
    
    def _analyze_aqi_correlations(self, df: pd.DataFrame) -> Dict:
        """Analisa correlações específicas com AQI."""
        analysis = {}
        
        if 'aqi_us' not in df.columns or df['aqi_us'].isna().all():
            return {"error": "Dados de AQI não disponíveis"}
        
        # Remove NaN
        df_clean = df.dropna(subset=['aqi_us'])
        
        if len(df_clean) < 10:
            return {"error": "Dados insuficientes para análise de AQI"}
        
        # Correlações com fatores meteorológicos
        weather_factors = ['temperature', 'humidity', 'pressure', 'wind_speed', 'clouds']
        correlations = {}
        
        for factor in weather_factors:
            if factor in df_clean.columns:
                corr, p_value = stats.pearsonr(df_clean['aqi_us'], df_clean[factor])
                correlations[factor] = {
                    'correlation': corr,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
        
        analysis['weather_correlations'] = correlations
        
        # Análise por período do dia
        if 'time_period' in df_clean.columns:
            period_analysis = df_clean.groupby('time_period')['aqi_us'].agg(['mean', 'std', 'count'])
            analysis['by_time_period'] = period_analysis.to_dict('index')
        
        # Análise por faixa de temperatura
        if 'temperature' in df_clean.columns:
            df_clean['temp_range'] = pd.cut(df_clean['temperature'], 
                                          bins=[-np.inf, 10, 20, 30, np.inf], 
                                          labels=['Frio', 'Ameno', 'Quente', 'Muito Quente'])
            temp_analysis = df_clean.groupby('temp_range')['aqi_us'].agg(['mean', 'std', 'count'])
            analysis['by_temperature'] = temp_analysis.to_dict('index')
        
        # Fatores mais influentes
        correlations_sorted = sorted(correlations.items(), 
                                   key=lambda x: abs(x[1]['correlation']), 
                                   reverse=True)
        analysis['top_factors'] = correlations_sorted[:3]
        
        return analysis
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict:
        """Analisa padrões temporais."""
        patterns = {}
        
        if 'timestamp' not in df.columns:
            return patterns
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Padrões horários
        if 'hour' in df.columns:
            hourly_patterns = {}
            for col in ['temperature', 'humidity', 'aqi_us']:
                if col in df.columns:
                    hourly_stats = df.groupby('hour')[col].agg(['mean', 'std'])
                    hourly_patterns[col] = hourly_stats.to_dict('index')
            patterns['hourly'] = hourly_patterns
        
        # Padrões semanais
        if 'day_of_week' in df.columns:
            weekly_patterns = {}
            for col in ['temperature', 'humidity', 'aqi_us']:
                if col in df.columns:
                    weekly_stats = df.groupby('day_of_week')[col].agg(['mean', 'std'])
                    weekly_patterns[col] = weekly_stats.to_dict('index')
            patterns['weekly'] = weekly_patterns
        
        # Tendências ao longo do tempo
        if len(df) > 7:
            df_resampled = df.set_index('timestamp').resample('D').mean()
            trends = {}
            
            for col in ['temperature', 'humidity', 'pressure', 'aqi_us']:
                if col in df_resampled.columns:
                    values = df_resampled[col].dropna()
                    if len(values) > 3:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            range(len(values)), values
                        )
                        trends[col] = {
                            'slope': slope,
                            'r_squared': r_value**2,
                            'p_value': p_value,
                            'trend': 'increasing' if slope > 0 else 'decreasing',
                            'significant': p_value < 0.05
                        }
            
            patterns['trends'] = trends
        
        return patterns
    
    def _perform_clustering(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict:
        """Realiza análise de clustering."""
        try:
            # Prepara dados
            df_clean = df[numeric_cols].dropna()
            
            if len(df_clean) < 10:
                return {"error": "Dados insuficientes para clustering"}
            
            # Normaliza dados
            X_scaled = self.scaler.fit_transform(df_clean)
            
            # Determina número ótimo de clusters (método elbow)
            inertias = []
            K_range = range(2, min(8, len(df_clean)//2))
            
            for k in K_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(X_scaled)
                inertias.append(kmeans.inertia_)
            
            # Seleciona número de clusters (simplificado)
            optimal_k = 3 if len(K_range) >= 2 else 2
            
            # Executa clustering final
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Analisa clusters
            df_clustered = df_clean.copy()
            df_clustered['cluster'] = clusters
            
            cluster_stats = {}
            for i in range(optimal_k):
                cluster_data = df_clustered[df_clustered['cluster'] == i]
                cluster_stats[f'cluster_{i}'] = {
                    'size': len(cluster_data),
                    'percentage': len(cluster_data) / len(df_clustered) * 100,
                    'means': cluster_data[numeric_cols].mean().to_dict(),
                    'characteristics': self._describe_cluster(cluster_data, numeric_cols)
                }
            
            return {
                'n_clusters': optimal_k,
                'cluster_stats': cluster_stats,
                'silhouette_score': self._calculate_silhouette(X_scaled, clusters)
            }
            
        except Exception as e:
            logger.error(f"Erro no clustering: {e}")
            return {"error": f"Erro no clustering: {e}"}
    
    def _describe_cluster(self, cluster_data: pd.DataFrame, numeric_cols: List[str]) -> List[str]:
        """Descreve características principais de um cluster."""
        characteristics = []
        
        # Calcula percentis para identificar valores extremos
        overall_means = cluster_data[numeric_cols].mean()
        
        # Identifica características notáveis
        if 'temperature' in overall_means:
            temp = overall_means['temperature']
            if temp > 30:
                characteristics.append("Condições quentes")
            elif temp < 10:
                characteristics.append("Condições frias")
        
        if 'humidity' in overall_means:
            humidity = overall_means['humidity']
            if humidity > 80:
                characteristics.append("Alta umidade")
            elif humidity < 30:
                characteristics.append("Baixa umidade")
        
        if 'aqi_us' in overall_means:
            aqi = overall_means['aqi_us']
            if aqi > 100:
                characteristics.append("Qualidade do ar prejudicial")
            elif aqi < 50:
                characteristics.append("Boa qualidade do ar")
        
        if 'wind_speed' in overall_means:
            wind = overall_means['wind_speed']
            if wind > 10:
                characteristics.append("Ventos fortes")
            elif wind < 2:
                characteristics.append("Ventos calmos")
        
        return characteristics if characteristics else ["Condições normais"]
    
    def _calculate_silhouette(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calcula silhouette score simplificado."""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(X, labels)
        except:
            return 0.0
    
    def _perform_pca(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict:
        """Realiza análise de componentes principais."""
        try:
            # Prepara dados
            df_clean = df[numeric_cols].dropna()
            
            if len(df_clean) < 10 or len(numeric_cols) < 3:
                return {"error": "Dados insuficientes para PCA"}
            
            # Normaliza dados
            X_scaled = self.scaler.fit_transform(df_clean)
            
            # Executa PCA
            pca = PCA()
            X_pca = pca.fit_transform(X_scaled)
            
            # Calcula variância explicada
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(explained_variance)
            
            # Componentes principais
            components = pd.DataFrame(
                pca.components_[:3],  # Primeiros 3 componentes
                columns=numeric_cols,
                index=[f'PC{i+1}' for i in range(min(3, len(explained_variance)))]
            )
            
            return {
                'explained_variance': explained_variance[:5].tolist(),
                'cumulative_variance': cumulative_variance[:5].tolist(),
                'components': components.to_dict('index'),
                'n_components_90': int(np.argmax(cumulative_variance >= 0.9) + 1)
            }
            
        except Exception as e:
            logger.error(f"Erro no PCA: {e}")
            return {"error": f"Erro no PCA: {e}"}
    
    def generate_correlation_report(self, analysis_results: Dict) -> str:
        """Gera relatório textual das correlações."""
        report = []
        report.append("# 📊 RELATÓRIO DE ANÁLISE DE CORRELAÇÕES CLIMÁTICAS")
        report.append("=" * 60)
        
        # Correlações fortes
        if 'strong_correlations' in analysis_results:
            report.append("\n## 🔗 CORRELAÇÕES FORTES IDENTIFICADAS")
            strong_corrs = analysis_results['strong_correlations']
            
            if strong_corrs:
                for corr in strong_corrs[:5]:  # Top 5
                    direction = "positiva" if corr['direction'] == 'positive' else "negativa"
                    report.append(f"- **{corr['var1']}** vs **{corr['var2']}**: "
                                f"correlação {direction} de {corr['correlation']:.3f}")
            else:
                report.append("- Nenhuma correlação forte encontrada (>0.7)")
        
        # Análise de AQI
        if 'aqi_analysis' in analysis_results and 'weather_correlations' in analysis_results['aqi_analysis']:
            report.append("\n## 🌬️ FATORES QUE INFLUENCIAM A QUALIDADE DO AR")
            
            weather_corrs = analysis_results['aqi_analysis']['weather_correlations']
            top_factors = analysis_results['aqi_analysis'].get('top_factors', [])
            
            for factor, data in top_factors:
                corr = data['correlation']
                significant = data['significant']
                status = "significativa" if significant else "não significativa"
                
                if abs(corr) > 0.3:
                    if corr > 0:
                        relationship = "piora com o aumento"
                    else:
                        relationship = "melhora com o aumento"
                    
                    report.append(f"- **{factor.title()}**: {relationship} "
                                f"(correlação {corr:.3f}, {status})")
        
        # Padrões temporais
        if 'temporal_patterns' in analysis_results:
            report.append("\n## ⏰ PADRÕES TEMPORAIS IDENTIFICADOS")
            
            trends = analysis_results['temporal_patterns'].get('trends', {})
            for var, trend_data in trends.items():
                if trend_data['significant']:
                    direction = trend_data['trend']
                    r_squared = trend_data['r_squared']
                    
                    report.append(f"- **{var.title()}**: tendência {direction} "
                                f"(R² = {r_squared:.3f})")
        
        # Clustering
        if 'clustering' in analysis_results and 'cluster_stats' in analysis_results['clustering']:
            report.append("\n## 🎯 PERFIS DE CONDIÇÕES AMBIENTAIS")
            
            cluster_stats = analysis_results['clustering']['cluster_stats']
            for cluster_id, stats in cluster_stats.items():
                characteristics = ", ".join(stats['characteristics'])
                percentage = stats['percentage']
                
                report.append(f"- **Perfil {cluster_id.split('_')[1]}** ({percentage:.1f}%): "
                            f"{characteristics}")
        
        report.append("\n" + "=" * 60)
        report.append(f"📅 Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        return "\n".join(report)
