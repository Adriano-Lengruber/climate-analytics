"""
Sistema de geração de relatórios automáticos sobre dados climáticos.
Cria relatórios em PDF, HTML e JSON com análises detalhadas.
"""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

@dataclass
class ReportConfig:
    """Configuração para geração de relatórios."""
    title: str
    period_days: int = 30
    include_charts: bool = True
    include_statistics: bool = True
    include_trends: bool = True
    include_alerts: bool = True
    location_filter: Optional[str] = None
    format: str = "html"  # html, json, markdown

class ReportGenerator:
    """Gerador de relatórios climáticos automatizados."""
    
    def __init__(self, db_path: str, output_dir: str = "reports"):
        """
        Inicializa o gerador de relatórios.
        
        Args:
            db_path: Caminho para o banco de dados
            output_dir: Diretório para salvar relatórios
        """
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_comprehensive_report(self, config: ReportConfig) -> Dict[str, Any]:
        """
        Gera relatório abrangente baseado na configuração.
        
        Args:
            config: Configuração do relatório
            
        Returns:
            Dicionário com dados do relatório
        """
        logger.info(f"Gerando relatório: {config.title}")
        
        try:
            # Carrega dados
            data = self._load_data(config.period_days, config.location_filter)
            
            if data.empty:
                raise ValueError("Não há dados suficientes para o relatório")
            
            # Estrutura do relatório
            report = {
                'metadata': {
                    'title': config.title,
                    'generated_at': datetime.now().isoformat(),
                    'period': {
                        'days': config.period_days,
                        'start_date': data['timestamp'].min(),
                        'end_date': data['timestamp'].max()
                    },
                    'location_filter': config.location_filter,
                    'total_records': len(data)
                },
                'summary': {},
                'statistics': {},
                'trends': {},
                'alerts': {},
                'recommendations': []
            }
            
            # Análise de resumo
            report['summary'] = self._generate_summary(data)
            
            # Estatísticas detalhadas
            if config.include_statistics:
                report['statistics'] = self._generate_statistics(data)
            
            # Análise de tendências
            if config.include_trends:
                report['trends'] = self._generate_trends(data)
            
            # Alertas e anomalias
            if config.include_alerts:
                report['alerts'] = self._generate_alerts(data)
            
            # Recomendações
            report['recommendations'] = self._generate_recommendations(report)
            
            # Salva relatório
            self._save_report(report, config)
            
            logger.info(f"Relatório gerado com sucesso: {config.title}")
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            raise
    
    def _load_data(self, period_days: int, location_filter: Optional[str] = None) -> pd.DataFrame:
        """Carrega dados do banco para o período especificado."""
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
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
                        w.description,
                        a.aqi_us,
                        a.aqi_cn,
                        a.main_pollutant_us,
                        strftime('%H', w.timestamp) as hour,
                        strftime('%w', w.timestamp) as day_of_week
                    FROM weather_data w
                    LEFT JOIN air_quality_data a ON 
                        w.city = a.city AND 
                        w.country = a.country AND
                        date(w.timestamp) = date(a.timestamp)
                    WHERE datetime(w.timestamp) >= ?
                """
                
                params = [cutoff_date.isoformat()]
                
                if location_filter:
                    query += " AND w.city LIKE ?"
                    params.append(f"%{location_filter}%")
                
                query += " ORDER BY w.timestamp"
                
                df = pd.read_sql_query(query, conn, params=params)
                
                # Preprocessamento
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['hour'].astype(int)
                df['day_of_week'] = df['day_of_week'].astype(int)
                
                return df
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def _generate_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Gera resumo executivo dos dados."""
        summary = {
            'period_overview': {},
            'key_metrics': {},
            'data_quality': {}
        }
        
        try:
            # Visão geral do período
            summary['period_overview'] = {
                'total_days': (data['timestamp'].max() - data['timestamp'].min()).days,
                'total_records': len(data),
                'unique_locations': data['city'].nunique(),
                'data_coverage': len(data) / (24 * summary.get('total_days', 1)) * 100
            }
            
            # Métricas principais
            numeric_cols = ['temperature', 'humidity', 'pressure', 'wind_speed', 'aqi_us']
            
            for col in numeric_cols:
                if col in data.columns and not data[col].isna().all():
                    col_data = data[col].dropna()
                    summary['key_metrics'][col] = {
                        'mean': float(col_data.mean()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'std': float(col_data.std()),
                        'median': float(col_data.median())
                    }
            
            # Qualidade dos dados
            summary['data_quality'] = {
                'completeness': {},
                'missing_data_percentage': float(data.isnull().sum().sum() / (len(data) * len(data.columns)) * 100)
            }
            
            for col in numeric_cols:
                if col in data.columns:
                    completeness = (1 - data[col].isnull().sum() / len(data)) * 100
                    summary['data_quality']['completeness'][col] = float(completeness)
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
        
        return summary
    
    def _generate_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Gera estatísticas detalhadas."""
        stats = {
            'descriptive': {},
            'correlations': {},
            'distributions': {}
        }
        
        try:
            # Estatísticas descritivas
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            numeric_cols = [col for col in numeric_cols if col not in ['hour', 'day_of_week']]
            
            if numeric_cols:
                desc_stats = data[numeric_cols].describe()
                stats['descriptive'] = desc_stats.to_dict()
            
            # Matriz de correlação
            if len(numeric_cols) > 1:
                corr_matrix = data[numeric_cols].corr()
                stats['correlations'] = corr_matrix.to_dict()
            
            # Análise de distribuições
            for col in ['temperature', 'humidity', 'aqi_us']:
                if col in data.columns and not data[col].isna().all():
                    col_data = data[col].dropna()
                    
                    # Quartis e percentis
                    stats['distributions'][col] = {
                        'quartiles': {
                            'q25': float(col_data.quantile(0.25)),
                            'q50': float(col_data.quantile(0.50)),
                            'q75': float(col_data.quantile(0.75))
                        },
                        'percentiles': {
                            'p10': float(col_data.quantile(0.10)),
                            'p90': float(col_data.quantile(0.90)),
                            'p95': float(col_data.quantile(0.95)),
                            'p99': float(col_data.quantile(0.99))
                        },
                        'outliers_count': int(self._count_outliers(col_data))
                    }
            
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {e}")
        
        return stats
    
    def _count_outliers(self, series: pd.Series) -> int:
        """Conta outliers usando método IQR."""
        try:
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            return len(outliers)
        except:
            return 0
    
    def _generate_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa tendências temporais."""
        trends = {
            'linear_trends': {},
            'seasonal_patterns': {},
            'recent_changes': {}
        }
        
        try:
            from scipy import stats
            
            # Tendências lineares
            for col in ['temperature', 'humidity', 'pressure', 'aqi_us']:
                if col in data.columns and not data[col].isna().all():
                    col_data = data[col].dropna()
                    
                    if len(col_data) > 3:
                        x = np.arange(len(col_data))
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x, col_data)
                        
                        trends['linear_trends'][col] = {
                            'slope': float(slope),
                            'r_squared': float(r_value**2),
                            'p_value': float(p_value),
                            'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                            'significant': p_value < 0.05,
                            'daily_change': float(slope * 24)  # Assumindo dados horários
                        }
            
            # Padrões horários
            if 'hour' in data.columns:
                hourly_patterns = {}
                for col in ['temperature', 'humidity', 'aqi_us']:
                    if col in data.columns:
                        hourly_stats = data.groupby('hour')[col].agg(['mean', 'std']).fillna(0)
                        hourly_patterns[col] = {
                            'peak_hour': int(hourly_stats['mean'].idxmax()),
                            'lowest_hour': int(hourly_stats['mean'].idxmin()),
                            'variation_coefficient': float(hourly_stats['mean'].std() / hourly_stats['mean'].mean()) if hourly_stats['mean'].mean() > 0 else 0
                        }
                
                trends['seasonal_patterns']['hourly'] = hourly_patterns
            
            # Mudanças recentes (últimos 7 dias vs anteriores)
            if len(data) > 14:
                recent_data = data.tail(len(data) // 2)
                older_data = data.head(len(data) // 2)
                
                for col in ['temperature', 'humidity', 'aqi_us']:
                    if col in data.columns and not data[col].isna().all():
                        recent_mean = recent_data[col].mean()
                        older_mean = older_data[col].mean()
                        
                        if not pd.isna(recent_mean) and not pd.isna(older_mean) and older_mean != 0:
                            change_percent = ((recent_mean - older_mean) / older_mean) * 100
                            
                            trends['recent_changes'][col] = {
                                'recent_mean': float(recent_mean),
                                'older_mean': float(older_mean),
                                'change_percent': float(change_percent),
                                'change_direction': 'improvement' if change_percent < 0 and col == 'aqi_us' else 'increase' if change_percent > 0 else 'decrease'
                            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar tendências: {e}")
        
        return trends
    
    def _generate_alerts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identifica alertas e anomalias."""
        alerts = {
            'critical_values': [],
            'anomalies': [],
            'data_quality_issues': []
        }
        
        try:
            # Valores críticos
            if 'aqi_us' in data.columns:
                high_aqi = data[data['aqi_us'] > 100]
                if not high_aqi.empty:
                    alerts['critical_values'].append({
                        'type': 'high_aqi',
                        'description': f'{len(high_aqi)} registros com AQI > 100',
                        'max_value': float(high_aqi['aqi_us'].max()),
                        'dates': high_aqi['timestamp'].dt.date.unique().tolist()[:5]  # Primeiras 5 datas
                    })
            
            if 'temperature' in data.columns:
                extreme_temps = data[(data['temperature'] > 35) | (data['temperature'] < 0)]
                if not extreme_temps.empty:
                    alerts['critical_values'].append({
                        'type': 'extreme_temperature',
                        'description': f'{len(extreme_temps)} registros com temperatura extrema',
                        'max_temp': float(extreme_temps['temperature'].max()),
                        'min_temp': float(extreme_temps['temperature'].min())
                    })
            
            # Anomalias estatísticas
            for col in ['temperature', 'humidity', 'pressure', 'aqi_us']:
                if col in data.columns and not data[col].isna().all():
                    col_data = data[col].dropna()
                    
                    if len(col_data) > 10:
                        # Outliers usando Z-score
                        z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
                        outliers = col_data[z_scores > 3]
                        
                        if len(outliers) > 0:
                            alerts['anomalies'].append({
                                'variable': col,
                                'outlier_count': len(outliers),
                                'percentage': float(len(outliers) / len(col_data) * 100),
                                'extreme_values': outliers.tolist()[:5]  # Primeiros 5 valores
                            })
            
            # Problemas de qualidade de dados
            total_records = len(data)
            for col in data.columns:
                missing_count = data[col].isnull().sum()
                missing_percent = (missing_count / total_records) * 100
                
                if missing_percent > 20:  # Mais de 20% faltando
                    alerts['data_quality_issues'].append({
                        'variable': col,
                        'missing_count': int(missing_count),
                        'missing_percentage': float(missing_percent),
                        'severity': 'high' if missing_percent > 50 else 'medium'
                    })
            
        except Exception as e:
            logger.error(f"Erro ao gerar alertas: {e}")
        
        return alerts
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas no relatório."""
        recommendations = []
        
        try:
            # Baseado na qualidade dos dados
            data_quality = report.get('summary', {}).get('data_quality', {})
            missing_percentage = data_quality.get('missing_data_percentage', 0)
            
            if missing_percentage > 15:
                recommendations.append(
                    f"⚠️ Qualidade dos dados: {missing_percentage:.1f}% dos dados estão faltando. "
                    "Considere verificar as conexões das APIs e a frequência de coleta."
                )
            
            # Baseado em alertas críticos
            alerts = report.get('alerts', {})
            critical_values = alerts.get('critical_values', [])
            
            for alert in critical_values:
                if alert['type'] == 'high_aqi':
                    recommendations.append(
                        f"🌬️ Qualidade do ar crítica detectada (AQI máximo: {alert['max_value']:.0f}). "
                        "Monitore mais frequentemente e considere alertas automáticos."
                    )
                elif alert['type'] == 'extreme_temperature':
                    recommendations.append(
                        f"🌡️ Temperaturas extremas registradas ({alert['min_temp']:.1f}°C a {alert['max_temp']:.1f}°C). "
                        "Verifique sistemas de alerta para condições climáticas extremas."
                    )
            
            # Baseado em tendências
            trends = report.get('trends', {}).get('linear_trends', {})
            
            for var, trend_data in trends.items():
                if trend_data.get('significant', False):
                    direction = trend_data['trend_direction']
                    daily_change = abs(trend_data.get('daily_change', 0))
                    
                    if var == 'aqi_us' and direction == 'increasing':
                        recommendations.append(
                            f"📈 Tendência de piora na qualidade do ar detectada "
                            f"(+{daily_change:.2f} pontos/dia). Investigue possíveis causas."
                        )
                    elif var == 'temperature' and daily_change > 1:
                        recommendations.append(
                            f"🌡️ Variação significativa de temperatura detectada "
                            f"({daily_change:.2f}°C/dia). Monitore padrões climáticos."
                        )
            
            # Recomendações gerais
            total_records = report.get('metadata', {}).get('total_records', 0)
            period_days = report.get('metadata', {}).get('period', {}).get('days', 0)
            
            if total_records < period_days * 12:  # Menos de 12 registros por dia
                recommendations.append(
                    "📊 Frequência de coleta baixa detectada. "
                    "Considere aumentar a frequência para obter análises mais precisas."
                )
            
            # Recomendações específicas se não houver dados de qualidade do ar
            if not any('aqi' in col for col in ['aqi_us', 'aqi_cn'] if col in report.get('summary', {}).get('key_metrics', {})):
                recommendations.append(
                    "🌬️ Dados de qualidade do ar limitados. "
                    "Configure APIs de qualidade do ar para análises mais completas."
                )
            
            if not recommendations:
                recommendations.append(
                    "✅ Sistema funcionando adequadamente. "
                    "Continue monitorando e coletando dados regularmente."
                )
        
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            recommendations.append("❌ Erro ao gerar recomendações automáticas.")
        
        return recommendations
    
    def _save_report(self, report: Dict[str, Any], config: ReportConfig) -> None:
        """Salva relatório no formato especificado."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"{config.title.replace(' ', '_')}_{timestamp}"
            
            if config.format.lower() == "json":
                filepath = self.output_dir / f"{filename_base}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Converte datetime para string para serialização JSON
                    report_copy = self._serialize_for_json(report)
                    json.dump(report_copy, f, indent=2, ensure_ascii=False, default=str)
            
            elif config.format.lower() == "html":
                filepath = self.output_dir / f"{filename_base}.html"
                html_content = self._generate_html_report(report)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            elif config.format.lower() == "markdown":
                filepath = self.output_dir / f"{filename_base}.md"
                markdown_content = self._generate_markdown_report(report)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            logger.info(f"Relatório salvo em: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
    
    def _serialize_for_json(self, obj: Any) -> Any:
        """Serializa objetos para JSON, convertendo tipos não serializáveis."""
        if isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Gera relatório em formato HTML."""
        metadata = report.get('metadata', {})
        summary = report.get('summary', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('title', 'Relatório Climático')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
        .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
        .recommendation {{ background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 10px; margin: 5px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 {metadata.get('title', 'Relatório Climático')}</h1>
        <p>📅 Gerado em: {metadata.get('generated_at', 'N/A')}</p>
        <p>📊 Período: {metadata.get('period', {}).get('days', 'N/A')} dias | 
           📍 Local: {metadata.get('location_filter', 'Geral')} | 
           📈 Registros: {metadata.get('total_records', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>📋 Resumo Executivo</h2>
        <div class="metric">
            <strong>📅 Período Total:</strong> {summary.get('period_overview', {}).get('total_days', 'N/A')} dias
        </div>
        <div class="metric">
            <strong>📍 Localizações:</strong> {summary.get('period_overview', {}).get('unique_locations', 'N/A')}
        </div>
        <div class="metric">
            <strong>📊 Cobertura de Dados:</strong> {summary.get('period_overview', {}).get('data_coverage', 0):.1f}%
        </div>
        <div class="metric">
            <strong>🎯 Qualidade:</strong> {100 - summary.get('data_quality', {}).get('missing_data_percentage', 0):.1f}%
        </div>
    </div>
        """
        
        # Adiciona métricas principais
        key_metrics = summary.get('key_metrics', {})
        if key_metrics:
            html += '<div class="section"><h2>📊 Métricas Principais</h2><table><tr><th>Variável</th><th>Média</th><th>Mínimo</th><th>Máximo</th><th>Desvio Padrão</th></tr>'
            
            for var, metrics in key_metrics.items():
                var_name = var.replace('_', ' ').title()
                html += f"""
                <tr>
                    <td>{var_name}</td>
                    <td>{metrics.get('mean', 0):.2f}</td>
                    <td>{metrics.get('min', 0):.2f}</td>
                    <td>{metrics.get('max', 0):.2f}</td>
                    <td>{metrics.get('std', 0):.2f}</td>
                </tr>
                """
            html += '</table></div>'
        
        # Adiciona alertas
        alerts = report.get('alerts', {})
        critical_values = alerts.get('critical_values', [])
        if critical_values:
            html += '<div class="section"><h2>⚠️ Alertas Críticos</h2>'
            for alert in critical_values:
                html += f'<div class="alert">🚨 <strong>{alert.get("type", "").replace("_", " ").title()}:</strong> {alert.get("description", "")}</div>'
            html += '</div>'
        
        # Adiciona recomendações
        recommendations = report.get('recommendations', [])
        if recommendations:
            html += '<div class="section"><h2>💡 Recomendações</h2>'
            for rec in recommendations:
                html += f'<div class="recommendation">{rec}</div>'
            html += '</div>'
        
        html += """
    <div class="section">
        <h2>ℹ️ Informações Técnicas</h2>
        <p><strong>Sistema:</strong> Climate Analytics - Sistema de Monitoramento Climático</p>
        <p><strong>Versão:</strong> 1.0</p>
        <p><strong>Contato:</strong> github.com/Adriano-Lengruber/climate-analytics</p>
    </div>
</body>
</html>
        """
        
        return html
    
    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Gera relatório em formato Markdown."""
        metadata = report.get('metadata', {})
        summary = report.get('summary', {})
        
        md = f"""# 🌍 {metadata.get('title', 'Relatório Climático')}

**📅 Gerado em:** {metadata.get('generated_at', 'N/A')}  
**📊 Período:** {metadata.get('period', {}).get('days', 'N/A')} dias  
**📍 Local:** {metadata.get('location_filter', 'Geral')}  
**📈 Total de Registros:** {metadata.get('total_records', 'N/A')}

---

## 📋 Resumo Executivo

- **📅 Período Analisado:** {summary.get('period_overview', {}).get('total_days', 'N/A')} dias
- **📍 Localizações Únicas:** {summary.get('period_overview', {}).get('unique_locations', 'N/A')}
- **📊 Cobertura de Dados:** {summary.get('period_overview', {}).get('data_coverage', 0):.1f}%
- **🎯 Qualidade dos Dados:** {100 - summary.get('data_quality', {}).get('missing_data_percentage', 0):.1f}%

"""
        
        # Métricas principais
        key_metrics = summary.get('key_metrics', {})
        if key_metrics:
            md += "## 📊 Métricas Principais\n\n"
            md += "| Variável | Média | Mínimo | Máximo | Desvio Padrão |\n"
            md += "|----------|-------|--------|--------|---------------|\n"
            
            for var, metrics in key_metrics.items():
                var_name = var.replace('_', ' ').title()
                md += f"| {var_name} | {metrics.get('mean', 0):.2f} | {metrics.get('min', 0):.2f} | {metrics.get('max', 0):.2f} | {metrics.get('std', 0):.2f} |\n"
            
            md += "\n"
        
        # Alertas
        alerts = report.get('alerts', {})
        critical_values = alerts.get('critical_values', [])
        if critical_values:
            md += "## ⚠️ Alertas Críticos\n\n"
            for alert in critical_values:
                md += f"- 🚨 **{alert.get('type', '').replace('_', ' ').title()}:** {alert.get('description', '')}\n"
            md += "\n"
        
        # Recomendações
        recommendations = report.get('recommendations', [])
        if recommendations:
            md += "## 💡 Recomendações\n\n"
            for rec in recommendations:
                md += f"- {rec}\n"
            md += "\n"
        
        md += """---

## ℹ️ Informações Técnicas

**Sistema:** Climate Analytics - Sistema de Monitoramento Climático  
**Versão:** 1.0  
**Repositório:** [github.com/Adriano-Lengruber/climate-analytics](https://github.com/Adriano-Lengruber/climate-analytics)
"""
        
        return md
    
    def generate_daily_summary(self, location: str = None) -> Dict[str, Any]:
        """Gera resumo diário automatizado."""
        config = ReportConfig(
            title=f"Resumo Diário - {location or 'Geral'}",
            period_days=1,
            include_charts=False,
            include_statistics=False,
            include_trends=False,
            include_alerts=True,
            location_filter=location,
            format="json"
        )
        
        return self.generate_comprehensive_report(config)
    
    def generate_weekly_report(self, location: str = None) -> Dict[str, Any]:
        """Gera relatório semanal completo."""
        config = ReportConfig(
            title=f"Relatório Semanal - {location or 'Geral'}",
            period_days=7,
            include_charts=True,
            include_statistics=True,
            include_trends=True,
            include_alerts=True,
            location_filter=location,
            format="html"
        )
        
        return self.generate_comprehensive_report(config)
    
    def generate_monthly_analysis(self, location: str = None) -> Dict[str, Any]:
        """Gera análise mensal detalhada."""
        config = ReportConfig(
            title=f"Análise Mensal - {location or 'Geral'}",
            period_days=30,
            include_charts=True,
            include_statistics=True,
            include_trends=True,
            include_alerts=True,
            location_filter=location,
            format="html"
        )
        
        return self.generate_comprehensive_report(config)
