"""
Sistema de automação e agendamento para Climate Analytics.
Executa coleta de dados e análises em horários programados.
"""
import schedule
import time
import subprocess
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional
import threading
import signal

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config

class AutomationScheduler:
    """Sistema de agendamento para automação de tarefas."""
    
    def __init__(self, config_file: str = "automation_config.json"):
        """
        Inicializa o agendador.
        
        Args:
            config_file: Arquivo de configuração para tarefas
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.running = False
        self.logger = self._setup_logging()
        
        # Para parar graciosamente
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self) -> logging.Logger:
        """Configura logging para automação."""
        Config.ensure_directories()
        
        logger = logging.getLogger('automation')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Handler para arquivo
            file_handler = logging.FileHandler(
                Config.LOGS_DIR / 'automation.log'
            )
            file_handler.setLevel(logging.INFO)
            
            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _load_config(self) -> Dict:
        """Carrega configuração de automação."""
        default_config = {
            "data_collection": {
                "enabled": True,
                "frequency": "hourly",  # hourly, daily, custom
                "custom_times": [],     # Para frequency = custom
                "locations": ["São Paulo", "Rio de Janeiro", "Brasília"]
            },
            "analysis": {
                "enabled": True,
                "daily_reports": True,
                "weekly_reports": True,
                "monthly_reports": True,
                "alert_checks": True,
                "correlation_analysis": True,
                "times": {
                    "daily_reports": "08:00",
                    "weekly_reports": "MON 09:00", 
                    "monthly_reports": "01 10:00",  # Dia 1 do mês
                    "alert_checks": "every_hour",
                    "correlation_analysis": "SUN 11:00"
                }
            },
            "maintenance": {
                "enabled": True,
                "cache_cleanup": "daily",
                "log_rotation": "weekly",
                "database_optimization": "monthly"
            },
            "notifications": {
                "enabled": False,
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipients": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "critical_alerts_only": True
                }
            }
        }
        
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Merge com configuração padrão
                return {**default_config, **config}
            else:
                # Cria arquivo de configuração padrão
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                return default_config
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração: {e}")
            return default_config
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de parada."""
        self.logger.info(f"Recebido sinal {signum}. Parando automação...")
        self.stop()
    
    def run_data_collection(self) -> bool:
        """Executa coleta de dados."""
        self.logger.info("🔄 Iniciando coleta de dados...")
        
        try:
            # Executa o coletor de dados
            result = subprocess.run(
                [sys.executable, "data_collector.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Coleta de dados concluída com sucesso")
                return True
            else:
                self.logger.error(f"❌ Erro na coleta de dados: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("⏰ Timeout na coleta de dados")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar coleta: {e}")
            return False
    
    def run_daily_analysis(self) -> bool:
        """Executa análise diária."""
        self.logger.info("📊 Iniciando análise diária...")
        
        try:
            result = subprocess.run(
                [sys.executable, "climate_analyzer.py", "--alerts", "--reports", 
                 "--correlation-days", "7", "--save-results"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos timeout
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Análise diária concluída")
                return True
            else:
                self.logger.error(f"❌ Erro na análise diária: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar análise diária: {e}")
            return False
    
    def run_weekly_analysis(self) -> bool:
        """Executa análise semanal."""
        self.logger.info("📈 Iniciando análise semanal...")
        
        try:
            result = subprocess.run(
                [sys.executable, "climate_analyzer.py", "--all", 
                 "--correlation-days", "30"],
                capture_output=True,
                text=True,
                timeout=900  # 15 minutos timeout
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Análise semanal concluída")
                return True
            else:
                self.logger.error(f"❌ Erro na análise semanal: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar análise semanal: {e}")
            return False
    
    def run_alert_check(self) -> bool:
        """Executa verificação de alertas."""
        self.logger.info("🚨 Verificando alertas...")
        
        try:
            result = subprocess.run(
                [sys.executable, "climate_analyzer.py", "--alerts"],
                capture_output=True,
                text=True,
                timeout=180  # 3 minutos timeout
            )
            
            if result.returncode == 0:
                # Verifica se há alertas críticos na saída
                if "ALERTAS CRÍTICOS:" in result.stdout:
                    self.logger.warning("⚠️ Alertas críticos detectados!")
                    self._send_notification("Alertas críticos detectados", result.stdout)
                
                return True
            else:
                self.logger.error(f"❌ Erro na verificação de alertas: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar alertas: {e}")
            return False
    
    def run_maintenance(self) -> bool:
        """Executa tarefas de manutenção."""
        self.logger.info("🧹 Executando manutenção...")
        
        try:
            # Limpeza de cache
            result = subprocess.run(
                [sys.executable, "climate_analyzer.py", "--clear-cache"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Rotação de logs (mantém últimos 30 dias)
            log_dir = Config.LOGS_DIR
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    self.logger.info(f"🗑️ Log removido: {log_file.name}")
            
            self.logger.info("✅ Manutenção concluída")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na manutenção: {e}")
            return False
    
    def _send_notification(self, subject: str, message: str):
        """Envia notificação se configurada."""
        if not self.config.get("notifications", {}).get("enabled", False):
            return
        
        try:
            # Webhook notification
            webhook_config = self.config["notifications"].get("webhook", {})
            if webhook_config.get("enabled", False):
                import requests
                
                payload = {
                    "subject": subject,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "source": "Climate Analytics Automation"
                }
                
                response = requests.post(
                    webhook_config["url"],
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.logger.info("📬 Notificação webhook enviada")
                else:
                    self.logger.warning(f"⚠️ Falha no webhook: {response.status_code}")
            
            # Email notification (implementação básica)
            email_config = self.config["notifications"].get("email", {})
            if email_config.get("enabled", False):
                self._send_email(subject, message, email_config)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar notificação: {e}")
    
    def _send_email(self, subject: str, message: str, email_config: Dict):
        """Envia email (implementação básica)."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = email_config["username"]
            msg['Subject'] = f"[Climate Analytics] {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            for recipient in email_config["recipients"]:
                msg['To'] = recipient
                server.send_message(msg)
            
            server.quit()
            self.logger.info("📧 Email enviado com sucesso")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar email: {e}")
    
    def setup_schedules(self):
        """Configura agendamentos baseados na configuração."""
        self.logger.info("⏰ Configurando agendamentos...")
        
        # Coleta de dados
        data_config = self.config.get("data_collection", {})
        if data_config.get("enabled", False):
            frequency = data_config.get("frequency", "hourly")
            
            if frequency == "hourly":
                schedule.every().hour.do(self.run_data_collection)
                self.logger.info("🔄 Coleta de dados agendada: a cada hora")
            elif frequency == "daily":
                schedule.every().day.at("06:00").do(self.run_data_collection)
                self.logger.info("🔄 Coleta de dados agendada: diariamente às 06:00")
            elif frequency == "custom":
                for time_str in data_config.get("custom_times", []):
                    schedule.every().day.at(time_str).do(self.run_data_collection)
                    self.logger.info(f"🔄 Coleta de dados agendada: {time_str}")
        
        # Análises
        analysis_config = self.config.get("analysis", {})
        if analysis_config.get("enabled", False):
            times = analysis_config.get("times", {})
            
            # Relatórios diários
            if analysis_config.get("daily_reports", False):
                daily_time = times.get("daily_reports", "08:00")
                schedule.every().day.at(daily_time).do(self.run_daily_analysis)
                self.logger.info(f"📊 Relatórios diários agendados: {daily_time}")
            
            # Relatórios semanais
            if analysis_config.get("weekly_reports", False):
                weekly_time = times.get("weekly_reports", "MON 09:00")
                day, time_part = weekly_time.split(" ")
                getattr(schedule.every(), day.lower()).at(time_part).do(self.run_weekly_analysis)
                self.logger.info(f"📈 Relatórios semanais agendados: {weekly_time}")
            
            # Verificação de alertas
            if analysis_config.get("alert_checks", False):
                alert_frequency = times.get("alert_checks", "every_hour")
                if alert_frequency == "every_hour":
                    schedule.every().hour.do(self.run_alert_check)
                    self.logger.info("🚨 Verificação de alertas agendada: a cada hora")
        
        # Manutenção
        maintenance_config = self.config.get("maintenance", {})
        if maintenance_config.get("enabled", False):
            cache_cleanup = maintenance_config.get("cache_cleanup", "daily")
            if cache_cleanup == "daily":
                schedule.every().day.at("02:00").do(self.run_maintenance)
                self.logger.info("🧹 Manutenção agendada: diariamente às 02:00")
    
    def start(self):
        """Inicia o sistema de automação."""
        self.logger.info("🚀 Iniciando sistema de automação Climate Analytics")
        
        self.setup_schedules()
        self.running = True
        
        self.logger.info(f"📅 {len(schedule.jobs)} tarefas agendadas")
        
        # Lista todas as tarefas agendadas
        for job in schedule.jobs:
            self.logger.info(f"   • {job}")
        
        self.logger.info("⏰ Sistema em execução. Pressione Ctrl+C para parar.")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Interrupção detectada")
        finally:
            self.stop()
    
    def stop(self):
        """Para o sistema de automação."""
        if self.running:
            self.logger.info("🛑 Parando sistema de automação...")
            self.running = False
            schedule.clear()
            self.logger.info("✅ Sistema de automação parado")
    
    def run_once(self, task: str):
        """Executa uma tarefa específica uma vez."""
        self.logger.info(f"▶️ Executando tarefa única: {task}")
        
        task_map = {
            "data_collection": self.run_data_collection,
            "daily_analysis": self.run_daily_analysis,
            "weekly_analysis": self.run_weekly_analysis,
            "alert_check": self.run_alert_check,
            "maintenance": self.run_maintenance
        }
        
        if task in task_map:
            return task_map[task]()
        else:
            self.logger.error(f"❌ Tarefa desconhecida: {task}")
            return False
    
    def status(self) -> Dict:
        """Retorna status do sistema de automação."""
        return {
            "running": self.running,
            "scheduled_jobs": len(schedule.jobs),
            "config_file": self.config_file,
            "last_check": datetime.now().isoformat(),
            "jobs": [str(job) for job in schedule.jobs]
        }

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Climate Analytics - Sistema de Automação",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python automation.py start                     # Inicia sistema completo
  python automation.py --run-once data_collection # Executa coleta uma vez
  python automation.py --run-once daily_analysis  # Executa análise diária
  python automation.py status                    # Mostra status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'status'],
        nargs='?',
        default='start',
        help='Comando a executar'
    )
    
    parser.add_argument(
        '--config',
        default='automation_config.json',
        help='Arquivo de configuração'
    )
    
    parser.add_argument(
        '--run-once',
        choices=['data_collection', 'daily_analysis', 'weekly_analysis', 
                'alert_check', 'maintenance'],
        help='Executa uma tarefa específica uma vez'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Cria arquivo de configuração padrão'
    )
    
    args = parser.parse_args()
    
    # Cria sistema de automação
    automation = AutomationScheduler(args.config)
    
    try:
        if args.create_config:
            print(f"✅ Arquivo de configuração criado: {args.config}")
            print("📝 Edite o arquivo para personalizar as configurações.")
            return
        
        if args.run_once:
            success = automation.run_once(args.run_once)
            exit_code = 0 if success else 1
            sys.exit(exit_code)
        
        if args.command == 'start':
            automation.start()
        elif args.command == 'status':
            status = automation.status()
            print("📊 STATUS DO SISTEMA DE AUTOMAÇÃO")
            print("=" * 40)
            print(f"Status: {'🟢 Executando' if status['running'] else '🔴 Parado'}")
            print(f"Tarefas agendadas: {status['scheduled_jobs']}")
            print(f"Última verificação: {status['last_check']}")
            
            if status['jobs']:
                print("\n📅 Tarefas agendadas:")
                for job in status['jobs']:
                    print(f"   • {job}")
            
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
        automation.stop()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
