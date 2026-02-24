# logic/copsoq_processor.py
# Responsabilidade: Conter toda a lógica de negócio para processar e validar dados do COPSOQ.
# Versão: Atualizada com suporte flexível a prefixos (P, Q, Resp_Q) e limpeza de dados.

import pandas as pd
import numpy as np
import hashlib
import unicodedata
from datetime import datetime

# Importa os modelos de dados
from models.analysis import AnalysisResult, ValidationResult
from models.enums import AnalysisType, RiskLevel, DataQuality

class COPSOQProcessor:
    """Processa e analisa dados do questionário COPSOQ com alta tolerância a formatos de entrada."""
    
    def __init__(self, version: str = "III"):
        self.version = version
        self._setup_scales()

    def _setup_scales(self):
        """Define os índices das perguntas por escala para permitir mapeamento dinâmico de prefixos."""
        if self.version == "III":
            # Mapeamento numérico das 84 questões do COPSOQ III
            self.scale_map = {
                "Exigências Quantitativas": [1, 2, 3],
                "Ritmo de Trabalho": [4, 5],
                "Exigências Cognitivas": [6, 7, 8, 9],
                "Exigências Emocionais": [10, 11, 12],
                "Influência no Trabalho": [13, 14, 15, 16],
                "Possibilidades de Desenvolvimento": [17, 18, 19],
                "Controlo sobre o Tempo de Trabalho": [20, 21, 22],
                "Significado do Trabalho": [23, 24, 25],
                "Compromisso face ao Local de Trabalho": [26, 27],
                "Previsibilidade": [28, 29],
                "Reconhecimento": [30, 31, 32],
                "Transparência do Papel Laboral": [33, 34, 35],
                "Conflitos de Papéis Laborais": [36, 37, 38],
                "Qualidade da Liderança": [39, 40, 41, 42],
                "Suporte Social de Colegas": [43, 44, 45],
                "Suporte Social de Superiores": [46, 47, 48],
                "Sentido de Pertença a Comunidade": [49, 50, 51],
                "Insegurança Laboral": [52, 53],
                "Insegurança com as Condições de Trabalho": [54, 55, 56],
                "Qualidade do Trabalho": [57],
                "Confiança Horizontal": [58, 59, 60],
                "Confiança Vertical": [61, 62, 63],
                "Justiça Organizacional": [64, 65, 66, 67],
                "Conflito Trabalho-Família": [68, 69, 70],
                "Satisfação com o trabalho": [71, 72, 73],
                "Auto-Avaliação da Saúde": [74],
                "Auto-Eficácia": [75, 76],
                "Problemas de Sono": [77, 78],
                "Burnout": [79, 80],
                "Stress": [81, 82],
                "Sintomas Depressivos": [83, 84]
            }
            self.inverted_idx = [59, 60]
            self.positive_scales = [
                "Influência no Trabalho", "Possibilidades de Desenvolvimento", 
                "Controlo sobre o Tempo de Trabalho", "Significado do Trabalho", 
                "Compromisso face ao Local de Trabalho", "Previsibilidade", 
                "Reconhecimento", "Transparência do Papel Laboral", "Qualidade da Liderança", 
                "Suporte Social de Colegas", "Suporte Social de Superiores", 
                "Sentido de Pertença a Comunidade", "Qualidade do Trabalho", 
                "Confiança Horizontal", "Confiança Vertical", "Justiça Organizacional", 
                "Satisfação com o trabalho", "Auto-Avaliação da Saúde", "Auto-Eficácia"
            ]
        else: # Versão II simplificada para compatibilidade
            self.scale_map = {"Ritmo de Trabalho": [1, 2], "Exigências Cognitivas": [3, 4]}
            self.inverted_idx = []
            self.positive_scales = ["Influência"]
        
        self.text_to_score = {
            "nunca": 1, "raramente": 2, "às vezes": 3, "frequentemente": 4, "sempre": 5,
            "nada": 1, "um pouco": 2, "moderadamente": 3, "muito": 4, "extremamente": 5,
            "discordo totalmente": 1, "discordo parcialmente": 2, "neutro": 3, 
            "concordo parcialmente": 4, "concordo totalmente": 5
        }

    def _normalize_text(self, text: str) -> str:
        if not isinstance(text, str): return str(text).lower().strip()
        return ''.join(c for c in unicodedata.normalize('NFD', text.strip().lower()) if unicodedata.category(c) != 'Mn')

    def _get_question_cols(self, columns):
        """Detecta colunas que seguem os padrões conhecidos (P1, Q1, Resp_Q1)."""
        valid_cols = []
        for col in columns:
            c = str(col).strip()
            if (c.startswith('P') or c.startswith('Q')) and c[1:].isdigit():
                valid_cols.append(col)
            elif c.startswith('Resp_Q') and c[6:].isdigit():
                valid_cols.append(col)
        return valid_cols

    def _detect_format(self, df: pd.DataFrame) -> str:
        cols = self._get_question_cols(df.columns)
        if not cols: return "unknown"
        sample = df[cols[0]].dropna()
        if sample.empty: return "unknown"
        return "textual" if isinstance(sample.iloc[0], str) else "numeric"

    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """Valida os dados e prepara o mapeamento de escalas dinamicamente."""
        errors, warnings = [], []
        
        # Limpeza preventiva de nomes de colunas
        data.columns = [str(c).strip() for c in data.columns]
        
        p_cols = self._get_question_cols(data.columns)
        
        if len(data) < 5:
            errors.append(f"Volume insuficiente ({len(data)} respostas). Mínimo de 5 exigido.")
        
        if len(p_cols) < 10:
            errors.append(f"Poucas colunas de perguntas ({len(p_cols)}) detectadas.")
            
        # Detecta o prefixo utilizado (Resp_Q ou P) para montar as escalas
        prefix = "Resp_Q" if any(str(c).startswith("Resp_Q") for c in data.columns) else "P"
        self.scales = {s: [f"{prefix}{i}" for i in idx] for s, idx in self.scale_map.items()}
        self.inverted_items = [f"{prefix}{i}" for i in self.inverted_idx]
        
        coverage = sum(1 for _, items in self.scales.items() if any(item in data.columns for item in items)) / len(self.scales) * 100 if self.scales else 0
        
        if coverage < 30:
            errors.append(f"Cobertura de escalas crítica ({coverage:.1f}%). Verifique os nomes das colunas.")
        
        null_pct = data.isnull().sum().sum() / data.size * 100 if data.size > 0 else 0
        quality_score = max(0, 100 - null_pct - (100 - coverage) / 2)
        
        # No logic/copsoq_processor.py
        return ValidationResult(
    is_valid=len(errors) == 0, 
    errors=errors, 
    warnings=warnings, 
    suggestions=[],  # Adicionamos este argumento que estava faltando
    quality_score=quality_score
)
    def process(self, data: pd.DataFrame, name: str) -> AnalysisResult:
        # Garante limpeza de espaços nos cabeçalhos antes de qualquer ação
        data.columns = [str(c).strip() for c in data.columns]
        
        validation = self.validate(data)
        if not validation.is_valid:
            raise ValueError(f"Falha na validação: {', '.join(validation.errors)}")

        fmt = self._detect_format(data)
        results = {}
        for scale, items in self.scales.items():
            vals = []
            for item in items:
                if item in data.columns:
                    # Converte para numérico (0-5)
                    num = pd.to_numeric(data[item], errors='coerce') if fmt == "numeric" else data[item].apply(self._normalize_text).map(self.text_to_score)
                    
                    if item in self.inverted_items: 
                        num = 6 - num # Inverte a lógica (5 vira 1, 1 vira 5)
                    
                    # Normaliza para escala 0-100
                    vals.extend(((num - 1) * 25).dropna().tolist())
            
            if vals:
                results[scale] = np.mean(vals)
        
        risk = self._calculate_risk_level(results)
        return AnalysisResult(
            id=hashlib.md5(f"{datetime.now()}".encode()).hexdigest()[:8],
            type=AnalysisType.COPSOQ_III if self.version == "III" else AnalysisType.COPSOQ_II,
            name=name,
            timestamp=datetime.now(),
            data=results,
            metadata={'version': self.version, 'n_responses': len(data), 'coverage': validation.quality_score},
            risk_level=risk
        )

    def _calculate_risk_level(self, results: dict) -> RiskLevel:
        # Para escalas positivas, quanto maior o score, menor o risco (100 - score)
        # Para escalas negativas (ex: Burnout), o score já representa o risco
        scores = [(100 - s) if scale in self.positive_scales else s for scale, s in results.items()]
        avg_risk = np.mean(scores) if scores else 0
        
        if avg_risk >= 75: return RiskLevel.CRITICAL
        if avg_risk >= 50: return RiskLevel.HIGH
        if avg_risk >= 25: return RiskLevel.MODERATE
        return RiskLevel.LOW