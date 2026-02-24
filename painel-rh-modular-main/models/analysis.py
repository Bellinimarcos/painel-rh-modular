# models/analysis.py
# Responsabilidade: Definir as estruturas de dados (dataclasses) do projeto.

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from .enums import AnalysisType, RiskLevel, DataQuality

@dataclass
class AnalysisResult:
    id: str
    type: AnalysisType
    name: str
    timestamp: datetime
    data: Dict[str, Union[float, pd.DataFrame, List[str], Dict]]
    metadata: Dict[str, Any]
    quality: Optional[DataQuality] = None
    risk_level: Optional[RiskLevel] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    quality_score: float

    @property
    def quality(self) -> DataQuality:
        for quality_level in DataQuality:
            if self.quality_score >= quality_level.threshold:
                return quality_level
        return DataQuality.INVALID




