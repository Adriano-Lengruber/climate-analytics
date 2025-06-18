"""
Script principal para análise automatizada do Climate Analytics.
Executa análises abrangentes e gera relatórios automáticos.
"""
import os
import sys
import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config
from src.analysis.alert_system import ClimateAlertSystem
from src.analysis.correlation_analyzer import CorrelationAnalyzer
from src.reports.report_generator import ReportGenerator, ReportConfig
from src.utils.cache_system import get_cache_instance, clear_all_cache

def setup_logging(log_level: str = "INFO"):
    """Configura sistema de logging."""
    Config.ensure_directories()
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOGS_DIR / 'analysis.log'),
            logging.StreamHandler()
        ]
    )

def check_database(db_path: str) -> dict:
    """Verifica estado do banco de dados."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verifica tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            stats = {'tables': tables, 'records': {}}
            
            for table in ['weather_data', 'air_quality_data']:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats['records'][table] = count
                    
                    # Data range
                    cursor.execute(f"SELECT MIN(timestamp), MAX(timestamp) FROM {table}")
                    date_range = cursor.fetchone()
                    stats[f'{table}_range'] = {
                        'start': date_range[0],
                        'end': date_range[1]
                    }
            
            return stats
            
    except Exception as e:
        return {'error': str(e)}

def run_alert_analysis(db_path: str, location: str = None) -> dict:
    """Executa análise de alertas."""
    print("\n🚨 EXECUTANDO ANÁLISE DE ALERTAS...")
    
    try:
        alert_system = ClimateAlertSystem(db_path)
        alerts = alert_system.analyze_current_conditions(location)
        
        summary = alert_system.get_alerts_summary()
        
        print(f"✅ Análise concluída: {summary['total']} alertas encontrados")
        
        if summary['critical_count'] > 0:
            print(f"⚠️  ALERTAS CRÍTICOS: {summary['critical_count']}")
        
        # Exibe principais alertas
        for alert in alerts[:3]:  # Top 3
            print(f"   • {alert.title} ({alert.location})")
        
        return {
            'success': True,
            'total_alerts': summary['total'],
            'critical_alerts': summary['critical_count'],
            'alerts': [
                {
                    'title': alert.title,
                    'level': alert.level.value,
                    'location': alert.location,
                    'description': alert.description
                }
                for alert in alerts
            ]
        }
        
    except Exception as e:
        print(f"❌ Erro na análise de alertas: {e}")
        return {'success': False, 'error': str(e)}

def run_correlation_analysis(db_path: str, days_back: int = 30) -> dict:
    """Executa análise de correlações."""
    print(f"\n🔗 EXECUTANDO ANÁLISE DE CORRELAÇÕES ({days_back} dias)...")
    
    try:
        analyzer = CorrelationAnalyzer(db_path)
        
        # Carrega dados
        df = analyzer.load_integrated_data(days_back)
        
        if df.empty:
            print("⚠️  Dados insuficientes para análise")
            return {'success': False, 'error': 'Dados insuficientes'}
        
        # Executa análise
        results = analyzer.analyze_correlations(df)
        
        # Gera relatório
        report = analyzer.generate_correlation_report(results)
        
        print(f"✅ Análise concluída: {len(df)} registros processados")
        
        # Mostra correlações principais
        strong_corrs = results.get('strong_correlations', [])
        if strong_corrs:
            print("   📊 Correlações mais fortes:")
            for corr in strong_corrs[:3]:
                print(f"   • {corr['var1']} × {corr['var2']}: {corr['correlation']:.3f}")
        
        return {
            'success': True,
            'records_analyzed': len(df),
            'strong_correlations': len(strong_corrs),
            'report': report
        }
        
    except Exception as e:
        print(f"❌ Erro na análise de correlações: {e}")
        return {'success': False, 'error': str(e)}

def generate_reports(db_path: str, output_dir: str = "reports") -> dict:
    """Gera relatórios automáticos."""
    print(f"\n📊 GERANDO RELATÓRIOS...")
    
    try:
        generator = ReportGenerator(db_path, output_dir)
        
        reports_generated = []
        
        # Relatório diário
        try:
            daily_config = ReportConfig(
                title="Resumo Diário Automatizado",
                period_days=1,
                include_charts=False,
                include_statistics=True,
                include_trends=False,
                include_alerts=True,
                format="json"
            )
            
            daily_report = generator.generate_comprehensive_report(daily_config)
            reports_generated.append("daily_summary.json")
            print("   ✅ Resumo diário gerado")
            
        except Exception as e:
            print(f"   ❌ Erro no relatório diário: {e}")
        
        # Relatório semanal
        try:
            weekly_config = ReportConfig(
                title="Relatório Semanal Automatizado",
                period_days=7,
                include_charts=True,
                include_statistics=True,
                include_trends=True,
                include_alerts=True,
                format="html"
            )
            
            weekly_report = generator.generate_comprehensive_report(weekly_config)
            reports_generated.append("weekly_report.html")
            print("   ✅ Relatório semanal gerado")
            
        except Exception as e:
            print(f"   ❌ Erro no relatório semanal: {e}")
        
        # Relatório mensal (se há dados suficientes)
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM weather_data WHERE datetime(timestamp) >= datetime('now', '-30 days')")
                monthly_records = cursor.fetchone()[0]
                
                if monthly_records > 100:  # Dados suficientes
                    monthly_config = ReportConfig(
                        title="Análise Mensal Automatizada",
                        period_days=30,
                        include_charts=True,
                        include_statistics=True,
                        include_trends=True,
                        include_alerts=True,
                        format="html"
                    )
                    
                    monthly_report = generator.generate_comprehensive_report(monthly_config)
                    reports_generated.append("monthly_analysis.html")
                    print("   ✅ Análise mensal gerada")
                else:
                    print("   ⏭️  Análise mensal pulada (dados insuficientes)")
        
        except Exception as e:
            print(f"   ❌ Erro no relatório mensal: {e}")
        
        print(f"📋 Relatórios salvos em: {Path(output_dir).absolute()}")
        
        return {
            'success': True,
            'reports_generated': reports_generated,
            'output_directory': str(Path(output_dir).absolute())
        }
        
    except Exception as e:
        print(f"❌ Erro na geração de relatórios: {e}")
        return {'success': False, 'error': str(e)}

def optimize_cache(clear_cache: bool = False) -> dict:
    """Otimiza sistema de cache."""
    print("\n🧹 OTIMIZANDO SISTEMA DE CACHE...")
    
    try:
        cache = get_cache_instance()
        
        if clear_cache:
            clear_all_cache()
            print("   🗑️  Cache limpo completamente")
        else:
            # Cleanup automático
            cache._cleanup_expired()
            print("   🧹 Limpeza automática executada")
        
        stats = cache.get_stats()
        print(f"   📊 Entradas em memória: {stats.get('memory_entries', 0)}")
        print(f"   💾 Entradas em disco: {stats.get('disk_entries', 0)}")
        print(f"   📁 Tamanho em disco: {stats.get('disk_size_mb', 0):.2f} MB")
        
        return {
            'success': True,
            'cache_cleared': clear_cache,
            'stats': stats
        }
        
    except Exception as e:
        print(f"❌ Erro na otimização do cache: {e}")
        return {'success': False, 'error': str(e)}

def run_comprehensive_analysis(args):
    """Executa análise abrangente completa."""
    print("🌍 CLIMATE ANALYTICS - ANÁLISE AUTOMATIZADA")
    print("=" * 50)
    
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Verifica banco de dados
    print("\n📊 VERIFICANDO BANCO DE DADOS...")
    db_stats = check_database(args.database)
    
    if 'error' in db_stats:
        print(f"❌ Erro no banco de dados: {db_stats['error']}")
        return False
    
    weather_records = db_stats.get('records', {}).get('weather_data', 0)
    air_records = db_stats.get('records', {}).get('air_quality_data', 0)
    
    print(f"   📈 Registros meteorológicos: {weather_records}")
    print(f"   💨 Registros de qualidade do ar: {air_records}")
    
    if weather_records < 10:
        print("⚠️  Poucos dados disponíveis. Execute o coletor de dados primeiro.")
        if not args.force:
            return False
    
    # Results container
    results = {
        'timestamp': datetime.now().isoformat(),
        'database_stats': db_stats,
        'analyses': {}
    }
    
    # Cache optimization
    if args.clear_cache or args.optimize_cache:
        cache_result = optimize_cache(args.clear_cache)
        results['cache_optimization'] = cache_result
    
    # Alert analysis
    if args.alerts:
        alert_result = run_alert_analysis(args.database, args.location)
        results['analyses']['alerts'] = alert_result
    
    # Correlation analysis
    if args.correlations:
        corr_result = run_correlation_analysis(args.database, args.correlation_days)
        results['analyses']['correlations'] = corr_result
    
    # Report generation
    if args.reports:
        report_result = generate_reports(args.database, args.output_dir)
        results['analyses']['reports'] = report_result
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📋 RESUMO DA ANÁLISE")
    print("=" * 50)
    
    success_count = sum(1 for analysis in results['analyses'].values() 
                       if analysis.get('success', False))
    total_analyses = len(results['analyses'])
    
    print(f"✅ Análises bem-sucedidas: {success_count}/{total_analyses}")
    
    if 'alerts' in results['analyses']:
        alert_data = results['analyses']['alerts']
        if alert_data.get('success'):
            critical = alert_data.get('critical_alerts', 0)
            total = alert_data.get('total_alerts', 0)
            print(f"🚨 Alertas encontrados: {total} (críticos: {critical})")
    
    if 'correlations' in results['analyses']:
        corr_data = results['analyses']['correlations']
        if corr_data.get('success'):
            records = corr_data.get('records_analyzed', 0)
            correlations = corr_data.get('strong_correlations', 0)
            print(f"🔗 Correlações analisadas: {correlations} significativas de {records} registros")
    
    if 'reports' in results['analyses']:
        report_data = results['analyses']['reports']
        if report_data.get('success'):
            report_count = len(report_data.get('reports_generated', []))
            print(f"📊 Relatórios gerados: {report_count}")
    
    # Salva resultado completo
    if args.save_results:
        results_file = Path(args.output_dir) / f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(args.output_dir).mkdir(exist_ok=True)
        
        import json
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Resultados salvos em: {results_file}")
    
    print(f"\n⏰ Análise concluída em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    return success_count == total_analyses

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Climate Analytics - Sistema de Análise Automatizada",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python climate_analyzer.py --all                    # Executa todas as análises
  python climate_analyzer.py --alerts --reports       # Apenas alertas e relatórios
  python climate_analyzer.py --correlations -d 60     # Correlações dos últimos 60 dias
  python climate_analyzer.py --clear-cache            # Limpa cache e executa análises básicas
        """
    )
    
    parser.add_argument(
        '--database', '-db',
        default=Config.DATABASE_PATH,
        help='Caminho para o banco de dados'
    )
    
    parser.add_argument(
        '--location', '-l',
        help='Filtrar análises por localização específica'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='reports',
        help='Diretório para salvar relatórios'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Nível de logging'
    )
    
    # Tipos de análise
    analysis_group = parser.add_argument_group('Tipos de Análise')
    analysis_group.add_argument(
        '--all', '-a',
        action='store_true',
        help='Executa todas as análises disponíveis'
    )
    
    analysis_group.add_argument(
        '--alerts',
        action='store_true',
        help='Executa análise de alertas'
    )
    
    analysis_group.add_argument(
        '--correlations',
        action='store_true',
        help='Executa análise de correlações'
    )
    
    analysis_group.add_argument(
        '--reports',
        action='store_true',
        help='Gera relatórios automáticos'
    )
    
    # Opções específicas
    options_group = parser.add_argument_group('Opções Específicas')
    options_group.add_argument(
        '--correlation-days', '-d',
        type=int,
        default=30,
        help='Número de dias para análise de correlações'
    )
    
    options_group.add_argument(
        '--clear-cache',
        action='store_true',
        help='Limpa todo o cache antes da análise'
    )
    
    options_group.add_argument(
        '--optimize-cache',
        action='store_true',
        help='Otimiza cache (limpeza automática)'
    )
    
    options_group.add_argument(
        '--force',
        action='store_true',
        help='Força execução mesmo com poucos dados'
    )
    
    options_group.add_argument(
        '--save-results',
        action='store_true',
        help='Salva resultados detalhados em JSON'
    )
    
    args = parser.parse_args()
    
    # Se --all foi especificado, ativa todas as análises
    if args.all:
        args.alerts = True
        args.correlations = True
        args.reports = True
        args.optimize_cache = True
        args.save_results = True
    
    # Se nenhuma análise foi especificada, executa básicas
    if not any([args.alerts, args.correlations, args.reports]):
        args.alerts = True
        args.reports = True
    
    # Executa análise
    try:
        success = run_comprehensive_analysis(args)
        exit_code = 0 if success else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Análise interrompida pelo usuário")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
