# utils/resource_limiter.py
"""
Limitador de recursos para prevenir sobrecarga do sistema.
Controla tamanho de arquivos, uso de memória e operações custosas.
"""
import logging
from typing import Optional, Callable
import functools
import time

logger = logging.getLogger(__name__)

# Configurações de limites
class ResourceLimits:
    MAX_FILE_SIZE_MB = 50
    MAX_MEMORY_MB = 1024
    MAX_DATAFRAME_ROWS = 100000
    MAX_DATAFRAME_COLS = 1000
    MAX_PROCESSING_TIME_SEC = 300  # 5 minutos


class ResourceLimiter:
    """Controla limites de recursos do sistema"""
    
    @staticmethod
    def check_file_size(file_obj, max_mb: int = None) -> bool:
        """
        Verifica se arquivo está dentro do limite de tamanho.
        
        Args:
            file_obj: Objeto de arquivo (deve ter atributo 'size')
            max_mb: Tamanho máximo em MB (usa padrão se None)
        
        Returns:
            True se válido
        
        Raises:
            ValueError: Se arquivo muito grande
        """
        max_mb = max_mb or ResourceLimits.MAX_FILE_SIZE_MB
        
        if hasattr(file_obj, 'size'):
            size_mb = file_obj.size / (1024 * 1024)
        elif hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell'):
            current_pos = file_obj.tell()
            file_obj.seek(0, 2)
            size_bytes = file_obj.tell()
            file_obj.seek(current_pos)
            size_mb = size_bytes / (1024 * 1024)
        else:
            logger.warning("Não foi possível verificar tamanho do arquivo")
            return True
        
        if size_mb > max_mb:
            raise ValueError(
                f"Arquivo muito grande: {size_mb:.1f}MB. "
                f"Máximo permitido: {max_mb}MB. "
                f"Considere dividir o arquivo ou usar uma amostra."
            )
        
        logger.debug(f"Arquivo OK: {size_mb:.1f}MB")
        return True
    
    @staticmethod
    def check_dataframe_size(df, max_rows: int = None, max_cols: int = None) -> bool:
        """
        Verifica dimensões do DataFrame.
        
        Raises:
            ValueError: Se DataFrame muito grande
        """
        max_rows = max_rows or ResourceLimits.MAX_DATAFRAME_ROWS
        max_cols = max_cols or ResourceLimits.MAX_DATAFRAME_COLS
        
        rows, cols = df.shape
        
        if rows > max_rows:
            raise ValueError(
                f"DataFrame com muitas linhas: {rows:,} "
                f"(máximo: {max_rows:,}). "
                f"Use uma amostra dos dados."
            )
        
        if cols > max_cols:
            raise ValueError(
                f"DataFrame com muitas colunas: {cols} "
                f"(máximo: {max_cols}). "
                f"Remova colunas desnecessárias."
            )
        
        logger.debug(f"DataFrame OK: {rows:,} × {cols}")
        return True
    
    @staticmethod
    def check_memory_usage(warn_threshold: float = 0.8) -> dict:
        """
        Verifica uso de memória do processo.
        
        Args:
            warn_threshold: Threshold para aviso (0-1)
        
        Returns:
            Dicionário com informações de memória
        """
        try:
            import psutil
            process = psutil.Process()
            mem_info = process.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            
            max_mem = ResourceLimits.MAX_MEMORY_MB
            usage_pct = mem_mb / max_mem
            
            status = {
                'used_mb': mem_mb,
                'max_mb': max_mem,
                'usage_pct': usage_pct * 100,
                'status': 'ok'
            }
            
            if usage_pct > 0.9:
                status['status'] = 'critical'
                logger.error(f"Memória crítica: {mem_mb:.0f}MB ({usage_pct*100:.0f}%)")
            elif usage_pct > warn_threshold:
                status['status'] = 'warning'
                logger.warning(f"Memória alta: {mem_mb:.0f}MB ({usage_pct*100:.0f}%)")
            else:
                logger.debug(f"Memória OK: {mem_mb:.0f}MB")
            
            return status
        
        except ImportError:
            logger.warning("psutil não disponível - verificação de memória desabilitada")
            return {'status': 'unknown'}
    
    @staticmethod
    def with_timeout(seconds: int):
        """
        Decorator para limitar tempo de execução de função.
        
        Args:
            seconds: Tempo máximo em segundos
        
        Example:
            @ResourceLimiter.with_timeout(60)
            def slow_function():
                ...
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(
                        f"Operação '{func.__name__}' excedeu o tempo limite de {seconds}s"
                    )
                
                # Apenas funciona em Unix/Linux
                if hasattr(signal, 'SIGALRM'):
                    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(seconds)
                    try:
                        result = func(*args, **kwargs)
                    finally:
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)
                    return result
                else:
                    # Windows - executa sem timeout
                    logger.warning(f"Timeout não suportado em Windows para {func.__name__}")
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def throttle(calls_per_second: float = 1.0):
        """
        Decorator para limitar taxa de chamadas de função.
        
        Args:
            calls_per_second: Máximo de chamadas por segundo
        
        Example:
            @ResourceLimiter.throttle(calls_per_second=2)
            def api_call():
                ...
        """
        min_interval = 1.0 / calls_per_second
        
        def decorator(func: Callable) -> Callable:
            last_called = [0.0]
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                elapsed = time.time() - last_called[0]
                if elapsed < min_interval:
                    sleep_time = min_interval - elapsed
                    logger.debug(f"Throttling {func.__name__}: aguardando {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                
                last_called[0] = time.time()
                return func(*args, **kwargs)
            
            return wrapper
        return decorator


class SafeExecutor:
    """Executa operações com proteções automáticas"""
    
    @staticmethod
    def safe_file_read(file_obj, reader_func: Callable, max_size_mb: int = None):
        """
        Lê arquivo com verificação de tamanho.
        
        Args:
            file_obj: Arquivo a ler
            reader_func: Função que lê o arquivo (ex: pd.read_csv)
            max_size_mb: Tamanho máximo
        
        Returns:
            Resultado da função reader_func
        
        Example:
            df = SafeExecutor.safe_file_read(
                uploaded_file,
                lambda f: pd.read_csv(f)
            )
        """
        ResourceLimiter.check_file_size(file_obj, max_size_mb)
        
        try:
            result = reader_func(file_obj)
            
            # Se resultado é DataFrame, valida tamanho
            import pandas as pd
            if isinstance(result, pd.DataFrame):
                ResourceLimiter.check_dataframe_size(result)
            
            return result
        
        except MemoryError:
            raise MemoryError(
                "Memória insuficiente para processar o arquivo. "
                "Tente com um arquivo menor ou aumente a memória disponível."
            )
    
    @staticmethod
    def safe_dataframe_operation(df, operation_func: Callable, operation_name: str = "Operação"):
        """
        Executa operação em DataFrame com verificações.
        
        Args:
            df: DataFrame
            operation_func: Função que opera no DataFrame
            operation_name: Nome da operação (para logs)
        
        Returns:
            Resultado da operação
        """
        # Verifica memória antes
        mem_status = ResourceLimiter.check_memory_usage(warn_threshold=0.7)
        if mem_status.get('status') == 'critical':
            raise MemoryError(f"Memória insuficiente para '{operation_name}'")
        
        # Verifica tamanho do DataFrame
        ResourceLimiter.check_dataframe_size(df)
        
        # Executa operação
        logger.info(f"Executando: {operation_name}")
        start_time = time.time()
        
        try:
            result = operation_func(df)
            elapsed = time.time() - start_time
            logger.info(f"'{operation_name}' concluída em {elapsed:.2f}s")
            return result
        
        except Exception as e:
            logger.error(f"Erro em '{operation_name}': {e}")
            raise