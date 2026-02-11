# logic/copsoq_processor.py
# Responsabilidade: Conter toda a lógica de negócio para processar e validar dados do COPSOQ.

import pandas as pd
import numpy as np
import hashlib
import unicodedata
from datetime import datetime

# Importa os modelos que criámos nos passos anteriores
from models.analysis import AnalysisResult, ValidationResult
from models.enums import AnalysisType, RiskLevel, DataQuality

class COPSOQProcessor:
    """Processa e analisa dados do questionário COPSOQ."""
    
    def __init__(self, version: str = "III"):
        self.version = version
        self._setup_scales()

    def _setup_scales(self):
        """Define as escalas e perguntas para a versão específica do COPSOQ."""
        if self.version == "III":
            self.scales = { "Exigências Quantitativas": ['P1', 'P2', 'P3'], "Ritmo de Trabalho": ['P4', 'P5'], "Exigências Cognitivas": ['P6', 'P7', 'P8', 'P9'], "Exigências Emocionais": ['P10', 'P11', 'P12'], "Influência no Trabalho": ['P13', 'P14', 'P15', 'P16'], "Possibilidades de Desenvolvimento": ['P17', 'P18', 'P19'], "Controlo sobre o Tempo de Trabalho": ['P20', 'P21', 'P22'], "Significado do Trabalho": ['P23', 'P24', 'P25'], "Compromisso face ao Local de Trabalho": ['P26', 'P27'], "Previsibilidade": ['P28', 'P29'], "Reconhecimento": ['P30', 'P31', 'P32'], "Transparência do Papel Laboral": ['P33', 'P34', 'P35'], "Conflitos de Papéis Laborais": ['P36', 'P37', 'P38'], "Qualidade da Liderança": ['P39', 'P40', 'P41', 'P42'], "Suporte Social de Colegas": ['P43', 'P44', 'P45'], "Suporte Social de Superiores": ['P46', 'P47', 'P48'], "Sentido de Pertença a Comunidade": ['P49', 'P50', 'P51'], "Insegurança Laboral": ['P52', 'P53'], "Insegurança com as Condições de Trabalho": ['P54', 'P55', 'P56'], "Qualidade do Trabalho": ['P57'], "Confiança Horizontal": ['P58', 'P59', 'P60'], "Confiança Vertical": ['P61', 'P62', 'P63'], "Justiça Organizacional": ['P64', 'P65', 'P66', 'P67'], "Conflito Trabalho-Família": ['P68', 'P69', 'P70'], "Satisfação com o trabalho": ['P71', 'P72', 'P73'], "Auto-Avaliação da Saúde": ['P74'], "Auto-Eficácia": ['P75', 'P76'], "Problemas de Sono": ['P77', 'P78'], "Burnout": ['P79', 'P80'], "Stress": ['P81', 'P82'], "Sintomas Depressivos": ['P83', 'P84'] }
            self.inverted_items = ['P59', 'P60']
            self.positive_scales = ["Influência no Trabalho", "Possibilidades de Desenvolvimento", "Controlo sobre o Tempo de Trabalho", "Significado do Trabalho", "Compromisso face ao Local de Trabalho", "Previsibilidade", "Reconhecimento", "Transparência do Papel Laboral", "Qualidade da Liderança", "Suporte Social de Colegas", "Suporte Social de Superiores", "Sentido de Pertença a Comunidade", "Qualidade do Trabalho", "Confiança Horizontal", "Confiança Vertical", "Justiça Organizacional", "Satisfação com o trabalho", "Auto-Avaliação da Saúde", "Auto-Eficácia"]
        else: # Versão II
            self.scales = {"Ritmo de Trabalho": ["P1", "P2"], "Exigências Cognitivas": ["P3", "P4"], "Exigências Emocionais": ["P5", "P6"], "Influência": ["P7", 'P8'], "Possibilidades de Desenvolvimento": ["P9", "P10"], "Sentido do Trabalho": ["P11", "P12"], "Comprometimento com o Local de Trabalho": ["P13", "P14"], "Previsibilidade": ["P15", "P16"], "Clareza de Papel": ["P17"], "Conflito de Papel": ["P18"], "Qualidade da Liderança": ["P19", "P20"], "Apoio Social do Superior": ["P21"], "Apoio Social dos Colegas": ["P22"], "Sentido de Comunidade": ["P23"], "Insegurança no Emprego": ["P24"], "Conflito Trabalho-Família": ["P25"], "Satisfação no Trabalho": ["P26"], "Saúde em Geral": ["P27"], "Burnout": ["P28"], "Estresse": ["P29"], "Problemas de Sono": ["P30"], "Sintomas Depressivos": ["P31"], "Assédio Moral": ["P32"]}
            self.inverted_items = []
            self.positive_scales = ["Influência", "Possibilidades de Desenvolvimento", "Sentido do Trabalho", "Comprometimento com o Local de Trabalho", "Previsibilidade", "Clareza de Papel", "Qualidade da Liderança", "Apoio Social do Superior", "Apoio Social dos Colegas", "Sentido de Comunidade", "Satisfação no Trabalho", "Saúde em Geral"]
        
        self.text_to_score = {"nunca": 1, "raramente": 2, "às vezes": 3, "frequentemente": 4, "sempre": 5, "nada": 1, "um pouco": 2, "moderadamente": 3, "muito": 4, "extremamente": 5, "discordo totalmente": 1, "discordo parcialmente": 2, "neutro": 3, "concordo parcialmente": 4, "concordo totalmente": 5}

    def _normalize_text(self, text: str) -> str:
        """Limpa e padroniza texto para comparação."""
        if not isinstance(text, str): return str(text).lower().strip()
        return ''.join(c for c in unicodedata.normalize('NFD', text.strip().lower()) if unicodedata.category(c) != 'Mn')

    def _detect_format(self, df: pd.DataFrame) -> str:
        """Deteta se as respostas são textuais ou numéricas."""
        p_cols = [col for col in df.columns if str(col).startswith('P') and str(col)[1:].isdigit()]
        if not p_cols: return "unknown"
        sample = df[p_cols[0]].dropna()
        if sample.empty: return "unknown"
        return "textual" if isinstance(sample.iloc[0], str) else "numeric"

    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """Valida os dados carregados antes do processamento."""
        errors, warnings = [], []
        p_cols = [col for col in data.columns if str(col).startswith('P') and str(col)[1:].isdigit()]
        if len(p_cols) < 10: errors.append(f"Poucas colunas de perguntas ({len(p_cols)}) detetadas.")
        
        coverage = sum(1 for _, items in self.scales.items() if any(item in data.columns for item in items)) / len(self.scales) * 100 if self.scales else 0
        if coverage < 50: warnings.append(f"Baixa cobertura de escalas ({coverage:.1f}%). A precisão pode ser afetada.")
        if coverage < 30: errors.append("Cobertura de escalas demasiado baixa para uma análise fiável.")
        
        null_pct = data.isnull().sum().sum() / data.size * 100 if data.size > 0 else 0
        if null_pct > 20: warnings.append(f"Elevado percentual de dados em falta ({null_pct:.1f}%).")
        
        quality_score = max(0, 100 - null_pct - (100 - coverage) / 2)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, suggestions=[], quality_score=quality_score)

    def process(self, data: pd.DataFrame, name: str) -> AnalysisResult:
        """Executa o processamento completo dos dados."""
        validation = self.validate(data)
        if not validation.is_valid:
            raise ValueError(f"Dados inválidos: {', '.join(validation.errors)}")

        fmt = self._detect_format(data)
        results = {}
        for scale, items in self.scales.items():
            vals = []
            for item in items:
                if item in data.columns:
                    # Converte resposta para valor numérico
                    num = pd.to_numeric(data[item], errors='coerce') if fmt == "numeric" else data[item].apply(self._normalize_text).map(self.text_to_score)
                    # Inverte a pontuação se necessário
                    if item in self.inverted_items: num = 6 - num
                    # Normaliza para uma escala de 0-100
                    vals.extend(((num - 1) * 25).dropna().tolist())
            
            if vals:
                results[scale] = np.mean(vals)
        
        risk = self._calculate_risk_level(results)

        return AnalysisResult(
            id=hashlib.md5(f"{datetime.now()}_{self.version}".encode()).hexdigest()[:8],
            type=AnalysisType.COPSOQ_III if self.version == "III" else AnalysisType.COPSOQ_II,
            name=name,
            timestamp=datetime.now(),
            data=results,
            metadata={'version': self.version, 'n_responses': len(data), 'coverage': validation.quality_score},
            quality=validation.quality,
            risk_level=risk
        )

    def _calculate_risk_level(self, results: dict) -> RiskLevel:
        """Calcula o nível de risco geral com base nos scores das escalas."""
        scores = [(100 - s) if scale in self.positive_scales else s for scale, s in results.items()]
        avg_risk = np.mean(scores) if scores else 0
        
        if avg_risk >= 75: return RiskLevel.CRITICAL
        if avg_risk >= 50: return RiskLevel.HIGH
        if avg_risk >= 25: return RiskLevel.MODERATE
        return RiskLevel.LOW

