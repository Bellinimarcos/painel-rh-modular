# models/enums.py
# Responsabilidade: Definir todos os Enums usados no projeto.

from enum import Enum

class AnalysisType(Enum):
    COPSOQ_II = "COPSOQ II"
    COPSOQ_III = "COPSOQ III"
    BURNOUT_CBI = "Esgotamento (CBI)"
    WORKAHOLISM = "Workaholism (DUWAS)"
    ABSENTEEISM = "Absentismo"
    TURNOVER = "Turnover"
    ISO = "ISO - Saúde Organizacional"
    AI_ASSISTANT = "Assistente IA"
    PULSE_SURVEY = "Termómetro de Sentimento"
    PREDICTIVE_RISK = "Risco Preditivo"
    CLIMATE = "Clima Organizacional"

class RiskLevel(Enum):
    LOW = ("Baixo", "#10B981", "")
    MODERATE = ("Moderado", "#F59E0B", "️")
    HIGH = ("Alto", "#EF4444", "")
    CRITICAL = ("Crítico", "#7C3AED", "")

    def __init__(self, label: str, color: str, emoji: str):
        self.label = label
        self.color = color
        self.emoji = emoji

class DataQuality(Enum):
    EXCELLENT = ("Excelente", 95)
    GOOD = ("Boa", 80)
    ACCEPTABLE = ("Aceitável", 60)
    POOR = ("Pobre", 40)
    INVALID = ("Inválido", 0)

    def __init__(self, label: str, threshold: float):
        self.label = label
        self.threshold = threshold




