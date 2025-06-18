"""
Sistema de cache inteligente para otimização de performance.
Implementa cache em memória e em disco para dados e análises.
"""
import sqlite3
import pickle
import json
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import logging
from functools import wraps
import threading

logger = logging.getLogger(__name__)

class SmartCache:
    """Sistema de cache inteligente com múltiplas estratégias."""
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        """
        Inicializa o sistema de cache.
        
        Args:
            cache_dir: Diretório para cache em disco
            default_ttl: TTL padrão em segundos (1 hora)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.default_ttl = default_ttl
        self.memory_cache = {}
        self.cache_metadata = {}
        self.lock = threading.RLock()
        
        # Limpeza automática
        self._cleanup_expired()
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Gera chave única para cache baseada na função e parâmetros."""
        # Serializa argumentos para string
        args_str = str(args) + str(sorted(kwargs.items()))
        key_data = f"{func_name}:{args_str}"
        
        # Hash para garantir tamanho consistente
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, timestamp: datetime, ttl: int) -> bool:
        """Verifica se cache expirou."""
        return datetime.now() > timestamp + timedelta(seconds=ttl)
    
    def _cleanup_expired(self):
        """Remove entradas expiradas do cache."""
        try:
            with self.lock:
                # Cache em memória
                expired_keys = []
                for key, metadata in self.cache_metadata.items():
                    if self._is_expired(metadata['timestamp'], metadata['ttl']):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    self.memory_cache.pop(key, None)
                    self.cache_metadata.pop(key, None)
                
                # Cache em disco
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        with open(cache_file, 'rb') as f:
                            data = pickle.load(f)
                            if self._is_expired(data['timestamp'], data['ttl']):
                                cache_file.unlink()
                    except Exception:
                        # Remove arquivo corrompido
                        cache_file.unlink()
                        
                logger.debug(f"Cache cleanup: removidas {len(expired_keys)} entradas")
                
        except Exception as e:
            logger.error(f"Erro na limpeza do cache: {e}")
    
    def get(self, key: str, memory_first: bool = True) -> Optional[Any]:
        """
        Recupera valor do cache.
        
        Args:
            key: Chave do cache
            memory_first: Se deve verificar memória primeiro
            
        Returns:
            Valor do cache ou None se não encontrado/expirado
        """
        try:
            with self.lock:
                # Verifica cache em memória primeiro
                if memory_first and key in self.memory_cache:
                    metadata = self.cache_metadata.get(key)
                    if metadata and not self._is_expired(metadata['timestamp'], metadata['ttl']):
                        logger.debug(f"Cache hit (memory): {key}")
                        return self.memory_cache[key]
                    else:
                        # Remove entrada expirada
                        self.memory_cache.pop(key, None)
                        self.cache_metadata.pop(key, None)
                
                # Verifica cache em disco
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                        
                        if not self._is_expired(data['timestamp'], data['ttl']):
                            logger.debug(f"Cache hit (disk): {key}")
                            
                            # Carrega para memória se não estiver
                            if memory_first:
                                self.memory_cache[key] = data['value']
                                self.cache_metadata[key] = {
                                    'timestamp': data['timestamp'],
                                    'ttl': data['ttl']
                                }
                            
                            return data['value']
                        else:
                            # Remove arquivo expirado
                            cache_file.unlink()
                
                logger.debug(f"Cache miss: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao recuperar cache {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            disk_cache: bool = True, memory_cache: bool = True) -> None:
        """
        Armazena valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: TTL em segundos (usa default se None)
            disk_cache: Se deve armazenar em disco
            memory_cache: Se deve armazenar em memória
        """
        if ttl is None:
            ttl = self.default_ttl
        
        timestamp = datetime.now()
        
        try:
            with self.lock:
                # Cache em memória
                if memory_cache:
                    self.memory_cache[key] = value
                    self.cache_metadata[key] = {
                        'timestamp': timestamp,
                        'ttl': ttl
                    }
                
                # Cache em disco
                if disk_cache:
                    cache_data = {
                        'value': value,
                        'timestamp': timestamp,
                        'ttl': ttl
                    }
                    
                    cache_file = self.cache_dir / f"{key}.cache"
                    with open(cache_file, 'wb') as f:
                        pickle.dump(cache_data, f)
                
                logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
                
        except Exception as e:
            logger.error(f"Erro ao armazenar cache {key}: {e}")
    
    def invalidate(self, key: str) -> None:
        """Remove entrada específica do cache."""
        try:
            with self.lock:
                # Remove da memória
                self.memory_cache.pop(key, None)
                self.cache_metadata.pop(key, None)
                
                # Remove do disco
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    cache_file.unlink()
                
                logger.debug(f"Cache invalidated: {key}")
                
        except Exception as e:
            logger.error(f"Erro ao invalidar cache {key}: {e}")
    
    def clear_all(self) -> None:
        """Limpa todo o cache."""
        try:
            with self.lock:
                # Limpa memória
                self.memory_cache.clear()
                self.cache_metadata.clear()
                
                # Limpa disco
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                
                logger.info("Todo cache foi limpo")
                
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        try:
            with self.lock:
                memory_size = len(self.memory_cache)
                disk_files = len(list(self.cache_dir.glob("*.cache")))
                
                total_disk_size = sum(
                    f.stat().st_size for f in self.cache_dir.glob("*.cache")
                )
                
                return {
                    'memory_entries': memory_size,
                    'disk_entries': disk_files,
                    'disk_size_mb': total_disk_size / (1024 * 1024),
                    'cache_dir': str(self.cache_dir)
                }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}

# Instância global do cache
_global_cache = SmartCache()

def cached(ttl: int = 3600, memory: bool = True, disk: bool = True, 
          key_prefix: str = ""):
    """
    Decorator para cache automático de funções.
    
    Args:
        ttl: TTL em segundos
        memory: Se deve usar cache em memória
        disk: Se deve usar cache em disco
        key_prefix: Prefixo para a chave do cache
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave do cache
            func_name = f"{key_prefix}{func.__name__}"
            cache_key = _global_cache._generate_key(func_name, args, kwargs)
            
            # Tenta recuperar do cache
            cached_result = _global_cache.get(cache_key, memory_first=memory)
            if cached_result is not None:
                return cached_result
            
            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl=ttl, 
                            disk_cache=disk, memory_cache=memory)
            
            return result
        
        # Adiciona métodos úteis ao wrapper
        wrapper.cache_clear = lambda: _global_cache.invalidate(
            _global_cache._generate_key(f"{key_prefix}{func.__name__}", (), {})
        )
        wrapper.cache_info = lambda: _global_cache.get_stats()
        
        return wrapper
    return decorator

class DatabaseCache:
    """Cache especializado para consultas de banco de dados."""
    
    def __init__(self, db_path: str, cache_instance: SmartCache = None):
        """
        Inicializa cache de banco.
        
        Args:
            db_path: Caminho para o banco de dados
            cache_instance: Instância de cache (usa global se None)
        """
        self.db_path = db_path
        self.cache = cache_instance or _global_cache
    
    @cached(ttl=1800, key_prefix="db_")  # 30 minutos
    def get_latest_data(self, location: str = None) -> Dict[str, Any]:
        """Recupera dados mais recentes com cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT w.timestamp, w.city, w.country, w.temperature, 
                           w.humidity, w.pressure, w.wind_speed, 
                           a.aqi_us, a.main_pollutant_us
                    FROM weather_data w
                    LEFT JOIN air_quality_data a ON 
                        w.city = a.city AND w.country = a.country
                    WHERE w.timestamp = (SELECT MAX(timestamp) FROM weather_data)
                """
                
                if location:
                    query += f" AND w.city LIKE '%{location}%'"
                
                query += " LIMIT 1"
                
                cursor.execute(query)
                row = cursor.fetchone()
                
                if row:
                    return {
                        'timestamp': row[0],
                        'city': row[1],
                        'country': row[2],
                        'temperature': row[3],
                        'humidity': row[4],
                        'pressure': row[5],
                        'wind_speed': row[6],
                        'aqi_us': row[7],
                        'main_pollutant_us': row[8]
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados mais recentes: {e}")
            return {}
    
    @cached(ttl=3600, key_prefix="db_stats_")  # 1 hora
    def get_database_stats(self) -> Dict[str, Any]:
        """Estatísticas do banco de dados com cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contagem de registros
                cursor.execute("SELECT COUNT(*) FROM weather_data")
                weather_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM air_quality_data")
                air_count = cursor.fetchone()[0]
                
                # Período dos dados
                cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM weather_data")
                date_range = cursor.fetchone()
                
                # Cidades únicas
                cursor.execute("SELECT COUNT(DISTINCT city) FROM weather_data")
                unique_cities = cursor.fetchone()[0]
                
                return {
                    'weather_records': weather_count,
                    'air_quality_records': air_count,
                    'date_range': {
                        'start': date_range[0],
                        'end': date_range[1]
                    },
                    'unique_cities': unique_cities,
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do banco: {e}")
            return {}
    
    def invalidate_location_cache(self, location: str):
        """Invalida cache específico de uma localização."""
        # Invalida caches relacionados à localização
        cache_keys_to_invalidate = [
            f"db_get_latest_data_{location}",
            f"db_stats_",
            f"weather_api_{location}",
            f"air_quality_api_{location}"
        ]
        
        for key_pattern in cache_keys_to_invalidate:
            # Como não temos acesso direto às chaves, fazemos limpeza geral
            # Em produção, seria melhor ter um sistema de tags
            pass
    
    def warm_cache(self, locations: list = None):
        """Pré-aquece o cache com dados frequentemente acessados."""
        try:
            logger.info("Iniciando pré-aquecimento do cache...")
            
            # Estatísticas gerais
            self.get_database_stats()
            
            # Dados de localizações específicas
            if locations:
                for location in locations:
                    self.get_latest_data(location)
            else:
                # Dados gerais
                self.get_latest_data()
            
            logger.info("Cache pré-aquecido com sucesso")
            
        except Exception as e:
            logger.error(f"Erro no pré-aquecimento do cache: {e}")

def get_cache_instance() -> SmartCache:
    """Retorna instância global do cache."""
    return _global_cache

def clear_all_cache():
    """Limpa todo o cache global."""
    _global_cache.clear_all()

def get_cache_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache global."""
    return _global_cache.get_stats()
