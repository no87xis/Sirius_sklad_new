import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from ..services.logger import logger


class PerformanceMonitor:
    """Упрощенный сервис мониторинга производительности без внешних зависимостей"""
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)  # Последние 1000 запросов
        self.error_counts = defaultdict(int)     # Счетчики ошибок
        self.database_query_times = deque(maxlen=500)  # Время запросов к БД
        self.start_time = datetime.now()
    
    def record_request_time(self, path: str, method: str, duration: float):
        """Запись времени выполнения запроса"""
        try:
            self.request_times.append({
                'timestamp': datetime.now(),
                'path': path,
                'method': method,
                'duration': duration
            })
            
            # Логируем медленные запросы
            if duration > 1.0:  # Больше 1 секунды
                logger.warning(f"Медленный запрос: {method} {path} - {duration:.2f}s")
        except Exception as e:
            logger.error(f"Ошибка при записи времени запроса: {e}")
    
    def record_error(self, error_type: str, path: str, error_message: str):
        """Запись ошибки"""
        try:
            self.error_counts[error_type] += 1
            logger.error(f"Ошибка {error_type} на {path}: {error_message}")
        except Exception as e:
            logger.error(f"Ошибка при записи ошибки: {e}")
    
    def record_database_query(self, table: str, operation: str, duration: float):
        """Запись времени выполнения запроса к БД"""
        try:
            self.database_query_times.append({
                'timestamp': datetime.now(),
                'table': table,
                'operation': operation,
                'duration': duration
            })
            
            # Логируем медленные запросы к БД
            if duration > 0.5:  # Больше 500ms
                logger.warning(f"Медленный запрос к БД: {operation} на {table} - {duration:.3f}s")
        except Exception as e:
            logger.error(f"Ошибка при записи времени БД: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        try:
            now = datetime.now()
            
            # Статистика запросов за последний час
            hour_ago = now - timedelta(hours=1)
            recent_requests = [r for r in self.request_times if r['timestamp'] > hour_ago]
            
            if recent_requests:
                avg_response_time = sum(r['duration'] for r in recent_requests) / len(recent_requests)
                max_response_time = max(r['duration'] for r in recent_requests)
                min_response_time = min(r['duration'] for r in recent_requests)
            else:
                avg_response_time = max_response_time = min_response_time = 0
            
            # Статистика ошибок
            total_errors = sum(self.error_counts.values())
            
            # Статистика БД
            recent_db_queries = [q for q in self.database_query_times if q['timestamp'] > hour_ago]
            if recent_db_queries:
                avg_db_time = sum(q['duration'] for q in recent_db_queries) / len(recent_db_queries)
            else:
                avg_db_time = 0
            
            return {
                'uptime': str(now - self.start_time),
                'requests': {
                    'total_last_hour': len(recent_requests),
                    'avg_response_time': round(avg_response_time, 3),
                    'max_response_time': round(max_response_time, 3),
                    'min_response_time': round(min_response_time, 3)
                },
                'errors': {
                    'total': total_errors,
                    'by_type': dict(self.error_counts)
                },
                'database': {
                    'queries_last_hour': len(recent_db_queries),
                    'avg_query_time': round(avg_db_time, 3)
                },
                'system': {
                    'memory_percent': 0,  # Упрощено
                    'memory_used_gb': 0,  # Упрощено
                    'cpu_percent': 0      # Упрощено
                },
                'timestamp': now.isoformat()
            }
        except Exception as e:
            logger.error(f"Ошибка при получении метрик: {e}")
            return {
                'uptime': '0:00:00',
                'requests': {'total_last_hour': 0, 'avg_response_time': 0, 'max_response_time': 0, 'min_response_time': 0},
                'errors': {'total': 0, 'by_type': {}},
                'database': {'queries_last_hour': 0, 'avg_query_time': 0},
                'system': {'memory_percent': 0, 'memory_used_gb': 0, 'cpu_percent': 0},
                'timestamp': datetime.now().isoformat()
            }
    
    def get_slow_queries(self, threshold: float = 1.0) -> list:
        """Получение медленных запросов"""
        try:
            return [r for r in self.request_times if r['duration'] > threshold]
        except Exception as e:
            logger.error(f"Ошибка при получении медленных запросов: {e}")
            return []
    
    def get_error_summary(self) -> Dict[str, int]:
        """Сводка по ошибкам"""
        try:
            return dict(self.error_counts)
        except Exception as e:
            logger.error(f"Ошибка при получении сводки ошибок: {e}")
            return {}
    
    def reset_metrics(self):
        """Сброс метрик"""
        try:
            self.request_times.clear()
            self.error_counts.clear()
            self.database_query_times.clear()
            self.start_time = datetime.now()
            logger.info("Метрики производительности сброшены")
        except Exception as e:
            logger.error(f"Ошибка при сбросе метрик: {e}")


# Глобальный экземпляр мониторинга
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware:
    """Упрощенный middleware для мониторинга запросов"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            start_time = time.time()
            path = scope.get('path', '')
            method = scope.get('method', '')
            
            try:
                await self.app(scope, receive, send)
                duration = time.time() - start_time
                performance_monitor.record_request_time(path, method, duration)
                
            except Exception as e:
                duration = time.time() - start_time
                performance_monitor.record_error('http_error', path, str(e))
                performance_monitor.record_request_time(path, method, duration)
                raise
        else:
            await self.app(scope, receive, send)

