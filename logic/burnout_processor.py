# logic/burnout_processor.py
# Responsabilidade: Conter a lógica de negócio para a análise de Esgotamento (CBI).

import numpy as np
import hashlib
from datetime import datetime
from typing import Dict

# Importa os modelos e enums da nossa nova arquitetura
from models.analysis import AnalysisResult
from models.enums import AnalysisType, RiskLevel

class BurnoutProcessor:
    """Processa os dados do questionário de Esgotamento (CBI)."""

    def process(self, name: str, responses: Dict) -> AnalysisResult:
        """Calcula os scores de burnout a partir das respostas do formulário."""
        # CORREÇÃO: Usar constantes locais
        cbi_questions = {
            "Burnout Pessoal": [
                {"question": "Com que frequência você se sente esgotado(a) física e emocionalmente?", "inverted": False},
                {"question": "Com que frequência você se sente exausto(a) ao final de um dia de trabalho?", "inverted": False},
                {"question": "Com que frequência você se sente cansado(a) pela manhã, só de pensar em mais um dia de trabalho?", "inverted": False},
                {"question": "Você tem energia para sua família e amigos durante seu tempo livre?", "inverted": True},
                {"question": "Com que frequência você se sente desgastado(a)?", "inverted": False},
                {"question": "Com que frequência você se sente fraco(a) e suscetível a doenças?", "inverted": False}
            ],
            "Burnout Relacionado ao Trabalho": [
                {"question": "Você se sente esgotado(a) pelo seu trabalho?", "inverted": False},
                {"question": "Você se sente frustrado(a) com seu trabalho?", "inverted": False},
                {"question": "O seu trabalho te cansa emocionalmente?", "inverted": False},
                {"question": "O seu trabalho te cansa fisicamente?", "inverted": False},
                {"question": "Você acha que está a trabalhar demais?", "inverted": False},
                {"question": "Você tem pique para trabalhar?", "inverted": True},
                {"question": "Você duvida que seu trabalho tenha algum significado?", "inverted": False}
            ],
            "Burnout Relacionado ao Cliente": [
                {"question": "Você acha desgastante trabalhar com clientes?", "inverted": False},
                {"question": "Você se sente farto(a) de trabalhar com clientes?", "inverted": False},
                {"question": "Você se pergunta por quanto tempo ainda conseguirá trabalhar com clientes?", "inverted": False},
                {"question": "Você acha que dá mais do que recebe ao trabalhar com clientes?", "inverted": False},
                {"question": "Você se sente esgotado(a) por ter que se relacionar com clientes no seu trabalho?", "inverted": False},
                {"question": "Você tem energia para trabalhar com clientes?", "inverted": True}
            ]
        }

        cbi_response_options = {
            "Sempre / Quase Sempre": 100, 
            "Frequentemente": 75, 
            "Às vezes": 50, 
            "Raramente": 25, 
            "Nunca / Quase Nunca": 0
        }

        cbi_inverted_options = {
            "Sempre / Quase Sempre": 0, 
            "Frequentemente": 25, 
            "Às vezes": 50, 
            "Raramente": 75, 
            "Nunca / Quase Nunca": 100
        }

        scores = {}
        for dimension, questions_data in cbi_questions.items():
            dim_scores = []
            for item in questions_data:
                q_hash = hashlib.md5(item['question'].encode()).hexdigest()[:8]
                key = f"cbi_{dimension.replace(' ', '')}_{q_hash}"
                
                if key in responses:  # CORREÇÃO: Verificar se a chave existe
                    # Seleciona o mapa de pontuação correto (normal ou invertido)
                    score_map = cbi_inverted_options if item['inverted'] else cbi_response_options
                    dim_scores.append(score_map[responses[key]])
            
            if dim_scores:  # CORREÇÃO: Evitar divisão por zero
                scores[dimension] = np.mean(dim_scores)
        
        if scores:  # CORREÇÃO: Verificar se há scores calculados
            overall = np.mean(list(scores.values()))
            risk = self._calculate_risk_level(overall)
        else:
            overall = 0
            risk = RiskLevel.LOW
        
        return AnalysisResult(
            id=hashlib.md5(f"cbi_{datetime.now()}".encode()).hexdigest()[:8],
            type=AnalysisType.BURNOUT_CBI,
            name=name,
            timestamp=datetime.now(),
            data=scores,
            metadata={'overall_score': overall},
            risk_level=risk
        )

    def _calculate_risk_level(self, overall_score: float) -> RiskLevel:
        """Determina o nível de risco com base na pontuação geral."""
        # CORREÇÃO: Retornar apenas o enum, não tuplas
        if overall_score >= 75:
            return RiskLevel.HIGH
        elif overall_score >= 50:
            return RiskLevel.MODERATE
        return RiskLevel.LOW