# logic/workaholism_processor.py
# Responsabilidade: Processar e calcular os resultados da análise de Workaholism (DUWAS)

import hashlib
from datetime import datetime
from typing import Dict, Any

# CORREÇÃO: Importar do arquivo correto
from models.analysis import AnalysisResult
from models.enums import AnalysisType, RiskLevel

class WorkaholismProcessor:
    """Processador para análise de Workaholism usando DUWAS."""
    
    def __init__(self):
        self.duwas_response_values = {
            "(Quase) Nunca": 1,
            "Ocasionalmente": 2,
            "Frequentemente": 3,
            "(Quase) Sempre": 4
        }
        
        # Mapeamento das questões por dimensão
        self.dimensions = {
            "Trabalhar Excessivamente": ["TrabalharExcessivamente_0", "TrabalharExcessivamente_1", 
                                        "TrabalharExcessivamente_2", "TrabalharExcessivamente_3"],
            "Trabalhar Compulsivamente": ["TrabalharCompulsivamente_0", "TrabalharCompulsivamente_1",
                                         "TrabalharCompulsivamente_2", "TrabalharCompulsivamente_3"]
        }
    
    def process(self, name: str, responses: Dict[str, str]) -> AnalysisResult:
        """
        Processa as respostas do DUWAS e retorna uma análise completa.
        
        Args:
            name: Nome da análise
            responses: Dicionário com as respostas do formulário
            
        Returns:
            AnalysisResult: Objeto com os resultados da análise
        """
        # Calcula os scores por dimensão
        scores = self._calculate_scores(responses)
        
        # Calcula o score geral
        overall_score = sum(scores.values())
        
        # Determina o nível de risco
        risk_level = self._determine_risk_level(overall_score)
        
        # CORREÇÃO: Usar AnalysisResult em vez de Analysis
        analysis = AnalysisResult(
            id=hashlib.md5(f"duwas_{datetime.now()}".encode()).hexdigest()[:8],
            name=name,
            type=AnalysisType.WORKAHOLISM,
            timestamp=datetime.now(),
            data=scores,
            metadata={
                "overall_score": overall_score,
                "max_score": 32,
                "dimensions": {
                    "Trabalhar Excessivamente": {
                        "score": scores.get("Trabalhar Excessivamente", 0),
                        "max": 16,
                        "percentage": (scores.get("Trabalhar Excessivamente", 0) / 16) * 100
                    },
                    "Trabalhar Compulsivamente": {
                        "score": scores.get("Trabalhar Compulsivamente", 0),
                        "max": 16,
                        "percentage": (scores.get("Trabalhar Compulsivamente", 0) / 16) * 100
                    }
                },
                "interpretation": self._generate_interpretation(overall_score, scores)
            },
            risk_level=risk_level
        )
        
        return analysis
    
    def _calculate_scores(self, responses: Dict[str, str]) -> Dict[str, float]:
        """
        Calcula os scores para cada dimensão do DUWAS.
        
        Args:
            responses: Dicionário com as respostas
            
        Returns:
            Dict com os scores por dimensão
        """
        scores = {}
        
        # Processa cada dimensão
        for dimension, question_keys in self.dimensions.items():
            dimension_score = 0
            valid_questions = 0
            
            for key in question_keys:
                # Procura pela chave no formato esperado
                full_key = f"duwas_{key}"
                if full_key in responses:
                    response_text = responses[full_key]
                    dimension_score += self.duwas_response_values.get(response_text, 0)
                    valid_questions += 1
            
            # Garante que temos pelo menos uma questão válida
            if valid_questions > 0:
                scores[dimension] = dimension_score
        
        return scores
    
    def _determine_risk_level(self, overall_score: float) -> RiskLevel:
        """
        Determina o nível de risco baseado no score geral.
        
        Args:
            overall_score: Pontuação total do DUWAS
            
        Returns:
            RiskLevel: Nível de risco identificado
        """
        if overall_score >= 24:  # 75% do score máximo
            return RiskLevel.HIGH
        elif overall_score >= 16:  # 50% do score máximo
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _generate_interpretation(self, overall_score: float, scores: Dict[str, float]) -> str:
        """
        Gera uma interpretação textual dos resultados.
        
        Args:
            overall_score: Score geral
            scores: Scores por dimensão
            
        Returns:
            str: Interpretação dos resultados
        """
        risk_level = self._determine_risk_level(overall_score)
        
        interpretations = {
            RiskLevel.HIGH: "Os resultados indicam um alto nível de workaholism. É fortemente recomendado buscar suporte profissional para estabelecer limites saudáveis entre trabalho e vida pessoal.",
            RiskLevel.MODERATE: "Os resultados indicam um nível moderado de workaholism. É importante estar atento aos sinais e considerar estratégias para melhor equilíbrio entre trabalho e vida pessoal.",
            RiskLevel.LOW: "Os resultados indicam um baixo nível de workaholism. Continue mantendo um equilíbrio saudável entre trabalho e vida pessoal."
        }
        
        base_interpretation = interpretations[risk_level]
        
        # Adiciona análise específica das dimensões
        excessive_score = scores.get("Trabalhar Excessivamente", 0)
        compulsive_score = scores.get("Trabalhar Compulsivamente", 0)
        
        if excessive_score > compulsive_score:
            dimension_analysis = " A pontuação indica uma tendência maior para trabalhar excessivamente (longas horas) do que compulsivamente."
        elif compulsive_score > excessive_score:
            dimension_analysis = " A pontuação indica uma tendência maior para trabalhar compulsivamente (obsessão com o trabalho) do que excessivamente."
        else:
            dimension_analysis = " As pontuações nas duas dimensões estão equilibradas."
        
        return base_interpretation + dimension_analysis