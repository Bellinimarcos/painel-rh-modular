"""
Módulo de modelos de dados para o Painel de RH
"""
from .enums import AnalysisType, RiskLevel, DataQuality
from .analysis import AnalysisResult, ValidationResult

__all__ = [
    'AnalysisType',
    'RiskLevel', 
    'DataQuality',
    'AnalysisResult',
    'ValidationResult'
]