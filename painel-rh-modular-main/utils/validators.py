# utils/validators.py
"""
Validadores de regras de negócio e dados do domínio RH.
Complementa o file_validators.py que foca na leitura de arquivos.
"""
from datetime import date, datetime
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Valida dados de negócio (não arquivos, mas sim o conteúdo).
    Para validação de arquivos, use FileValidator.
    """
    
    @staticmethod
    def validate_date_range(
        start: date, 
        end: date, 
        max_days: int = 730,
        field_name: str = "período"
    ) -> Tuple[bool, str]:
        """
        Valida intervalo de datas para análises de RH.
        
        Args:
            start: Data de início
            end: Data de fim
            max_days: Período máximo permitido em dias
            field_name: Nome do campo para mensagens de erro
        
        Returns:
            (is_valid, error_message)
        """
        # Converte datetime para date se necessário
        if isinstance(start, datetime):
            start = start.date()
        if isinstance(end, datetime):
            end = end.date()
        
        if not isinstance(start, date) or not isinstance(end, date):
            return False, f"{field_name}: Datas devem ser do tipo date"
        
        if start > end:
            return False, f"{field_name}: Data de início ({start}) não pode ser posterior à data de fim ({end})"
        
        period_days = (end - start).days
        if period_days > max_days:
            return False, f"{field_name}: Período muito longo ({period_days} dias). Máximo: {max_days} dias"
        
        if period_days < 0:
            return False, f"{field_name}: Período inválido"
        
        logger.debug(f"Validação de data OK: {start} a {end} ({period_days} dias)")
        return True, ""
    
    @staticmethod
    def validate_employee_count(
        count: int, 
        min_val: int = 1, 
        max_val: int = 100000,
        field_name: str = "número de colaboradores"
    ) -> Tuple[bool, str]:
        """
        Valida contagem de colaboradores.
        
        Args:
            count: Número a validar
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
            field_name: Nome do campo para mensagens
        
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(count, (int, float)):
            try:
                count = int(count)
            except (ValueError, TypeError):
                return False, f"{field_name}: Deve ser numérico (recebido: {type(count).__name__})"
        
        count = int(count)
        
        if not (min_val <= count <= max_val):
            return False, f"{field_name}: {count} fora do intervalo válido ({min_val} a {max_val})"
        
        logger.debug(f"Validação de contagem OK: {count}")
        return True, ""
    
    @staticmethod
    def validate_percentage(
        value: float, 
        allow_zero: bool = True,
        allow_negative: bool = False,
        field_name: str = "percentagem"
    ) -> Tuple[bool, str]:
        """
        Valida valores percentuais (0-100).
        
        Args:
            value: Valor a validar
            allow_zero: Se permite 0%
            allow_negative: Se permite valores negativos (útil para variações)
            field_name: Nome do campo
        
        Returns:
            (is_valid, error_message)
        """
        try:
            value = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name}: Deve ser numérico"
        
        min_val = 0 if allow_zero else 0.01
        if allow_negative:
            min_val = -100
        
        if not (min_val <= value <= 100):
            return False, f"{field_name}: {value}% fora do intervalo válido ({min_val} a 100)"
        
        return True, ""
    
    @staticmethod
    def validate_currency(
        value: float,
        min_val: float = 0,
        max_val: float = 1_000_000,
        field_name: str = "valor monetário"
    ) -> Tuple[bool, str]:
        """
        Valida valores monetários.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            value = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name}: Deve ser numérico"
        
        if not (min_val <= value <= max_val):
            return False, f"{field_name}: R$ {value:,.2f} fora do intervalo válido (R$ {min_val:,.2f} a R$ {max_val:,.2f})"
        
        if value < 0 and min_val >= 0:
            return False, f"{field_name}: Não pode ser negativo"
        
        return True, ""
    
    @staticmethod
    def validate_all(validations: list) -> Tuple[bool, list]:
        """
        Executa múltiplas validações e agrega os erros.
        
        Args:
            validations: Lista de tuplas (is_valid, error_message)
        
        Returns:
            (all_valid, list_of_errors)
        """
        errors = [msg for valid, msg in validations if not valid and msg]
        return len(errors) == 0, errors


