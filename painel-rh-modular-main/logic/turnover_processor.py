# logic/turnover_processor.py
# Responsabilidade: Processar e analisar dados de rotatividade (turnover) de colaboradores.

import hashlib
from datetime import datetime
from typing import Dict, List
import logging

from models.analysis import AnalysisResult, ValidationResult
from models.enums import AnalysisType, RiskLevel, DataQuality
from config.settings import AppConfig

logger = logging.getLogger(__name__)



# BENCHMARK DE TURNOVER
BENCHMARK_TURNOVER = {
    'Indústria': 3.5,
    'Comércio': 5.0,
    'Serviços': 4.0,
    'Saúde': 3.0,
    'Educação': 2.5,
    'TI': 4.5,
    'Outros': 4.0
}

class TurnoverProcessor:
    """
    Processa dados de turnover e calcula métricas chave:
    - Taxa de turnover (mensal e anualizada)
    - Impacto financeiro total
    - Análise de custos por tipo (demissão, contratação, produtividade)
    """
    
    def __init__(self):
        self.config = AppConfig()
    
    def validate(
        self,
        func_inicio: int,
        func_fim: int,
        admissoes: int,
        demissoes: int,
        periodo_meses: int
    ) -> ValidationResult:
        """
        Valida os dados de entrada antes do processamento.
        
        Args:
            func_inicio: Número de funcionários no início do período
            func_fim: Número de funcionários no fim do período
            admissoes: Número de admissões no período
            demissoes: Número de demissões no período
            periodo_meses: Duração do período em meses
        
        Returns:
            ValidationResult com status da validação
        """
        errors = []
        warnings = []
        suggestions = []
        
        # Validações básicas
        if func_inicio <= 0:
            errors.append("Número de funcionários no início deve ser maior que zero")
        
        if func_fim < 0:
            errors.append("Número de funcionários no fim não pode ser negativo")
        
        if admissoes < 0:
            errors.append("Número de admissões não pode ser negativo")
        
        if demissoes < 0:
            errors.append("Número de demissões não pode ser negativo")
        
        if periodo_meses <= 0:
            errors.append("Período deve ser maior que zero")
        elif periodo_meses > 24:
            warnings.append("Período muito longo (>24 meses) - considere análises anuais")
        
        # Validação de coerência dos dados
        if func_inicio > 0:
            expected_func_fim = func_inicio + admissoes - demissoes
            if func_fim != expected_func_fim:
                diff = abs(func_fim - expected_func_fim)
                warnings.append(
                    f"Inconsistência detectada: Funcionários fim ({func_fim}) "
                    f"difere do esperado ({expected_func_fim}) por {diff} colaboradores. "
                    f"Verifique se todos os movimentos foram contabilizados."
                )
        
        # Avisos sobre movimentação excessiva
        if func_inicio > 0:
            movimento_total = admissoes + demissoes
            taxa_movimento = (movimento_total / func_inicio) * 100
            
            if taxa_movimento > 50:
                warnings.append(
                    f"Alta movimentação detectada ({taxa_movimento:.1f}% do quadro inicial)"
                )
        
        # Sugestões
        if admissoes == 0 and demissoes == 0:
            suggestions.append("Nenhuma movimentação no período - verifique se os dados estão completos")
        
        # Calcula score de qualidade
        quality_score = 100
        if errors:
            quality_score = 0
        else:
            # Penaliza warnings
            quality_score -= len(warnings) * 10
            quality_score = max(quality_score, 60)  # Mínimo de 60 se não houver erros
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            quality_score=quality_score
        )
    
    def process(
        self,
        name: str,
        func_inicio: int,
        func_fim: int,
        admissoes: int,
        demissoes: int,
        periodo_meses: int,
        setor: str,
        custos: Dict[str, float]
    ) -> AnalysisResult:
        """
        Processa os dados de turnover e calcula todas as métricas.
        
        Args:
            name: Nome da análise
            func_inicio: Funcionários no início do período
            func_fim: Funcionários no fim do período
            admissoes: Total de admissões
            demissoes: Total de demissões
            periodo_meses: Duração do período em meses
            setor: Setor da empresa (para benchmark)
            custos: Dicionário com custos unitários {
                'demissao': float,
                'contratacao': float,
                'produtividade': float
            }
        
        Returns:
            AnalysisResult com os resultados da análise
        """
        # Valida os dados
        validation = self.validate(func_inicio, func_fim, admissoes, demissoes, periodo_meses)
        if not validation.is_valid:
            raise ValueError(f"Dados inválidos: {'; '.join(validation.errors)}")
        
        # Calcula média de funcionários no período
        media_funcionarios = (func_inicio + func_fim) / 2
        
        # Calcula taxa de turnover no período
        # Fórmula: ((Admissões + Demissões) / 2) / Média de funcionários * 100
        if media_funcionarios > 0:
            taxa_periodo = ((admissoes + demissoes) / 2) / media_funcionarios * 100
        else:
            taxa_periodo = 0
        
        # Anualiza a taxa (projeta para 12 meses)
        taxa_anualizada = taxa_periodo * (12 / periodo_meses)
        
        # Calcula custos detalhados
        custo_demissoes = demissoes * custos.get('demissao', 0)
        custo_contratacoes = admissoes * custos.get('contratacao', 0)
        
        # Custo de produtividade (apenas para posições que foram substituídas)
        substituicoes = min(admissoes, demissoes)
        custo_produtividade = substituicoes * custos.get('produtividade', 0)
        
        # Impacto financeiro total
        impacto_total = custo_demissoes + custo_contratacoes + custo_produtividade
        
        # Custo por funcionário médio
        custo_por_funcionario = impacto_total / media_funcionarios if media_funcionarios > 0 else 0
        
        # Determina nível de risco
        benchmark = BENCHMARK_TURNOVER.get(setor, 4.0)
        risk_level = self._calculate_risk_level(taxa_anualizada, benchmark)
        
        # Gera insights automáticos
        insights = self._generate_insights(
            taxa_anualizada,
            benchmark,
            admissoes,
            demissoes,
            impacto_total,
            media_funcionarios
        )
        
        # Cria detalhamento de custos para exibição
        custos_detalhados = {
            'Demissões': custo_demissoes,
            'Contratações': custo_contratacoes,
            'Perda de Produtividade': custo_produtividade
        }
        
        return AnalysisResult(
            id=hashlib.md5(f"turnover_{datetime.now()}".encode()).hexdigest()[:8],
            type=AnalysisType.TURNOVER,
            name=name,
            timestamp=datetime.now(),
            data={
                'taxa_turnover_periodo': round(taxa_periodo, 2),
                'taxa_turnover_anual': round(taxa_anualizada, 2),
                'impacto_financeiro': round(impacto_total, 2),
                'custo_por_funcionario': round(custo_por_funcionario, 2),
                'custos_detalhados': custos_detalhados,
                'substituicoes': substituicoes
            },
            metadata={
                'func_inicio': func_inicio,
                'func_fim': func_fim,
                'media_funcionarios': round(media_funcionarios, 1),
                'admissoes': admissoes,
                'demissoes': demissoes,
                'periodo_meses': periodo_meses,
                'setor': setor,
                'benchmark_setor': benchmark
            },
            quality=validation.quality,
            risk_level=risk_level,
            insights=insights
        )
    
    def _calculate_risk_level(self, taxa: float, benchmark: float) -> RiskLevel:
        """Determina o nível de risco baseado na comparação com o benchmark."""
        if taxa > benchmark * 1.5:
            return RiskLevel.HIGH
        elif taxa > benchmark * 1.3:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _generate_insights(
        self,
        taxa: float,
        benchmark: float,
        admissoes: int,
        demissoes: int,
        impacto_total: float,
        media_funcionarios: float
    ) -> List[str]:
        """Gera insights automáticos baseados nos dados."""
        insights = []
        
        # Insight sobre a taxa
        diff = taxa - benchmark
        if diff > benchmark * 0.5:  # 50% acima
            insights.append(
                f" Taxa de turnover crítica: {diff:.1f}% acima do benchmark do setor ({benchmark:.1f}%)"
            )
        elif diff > 0:
            insights.append(
                f"️ Taxa de turnover {diff:.1f}% acima do benchmark do setor ({benchmark:.1f}%)"
            )
        else:
            insights.append(
                f" Taxa de turnover dentro dos parâmetros do setor"
            )
        
        # Insight sobre balanço de movimentação
        saldo = admissoes - demissoes
        if saldo > 0:
            percentual_crescimento = (saldo / media_funcionarios) * 100
            insights.append(
                f" Crescimento do quadro: {saldo} colaboradores ({percentual_crescimento:.1f}%)"
            )
        elif saldo < 0:
            percentual_reducao = abs(saldo / media_funcionarios) * 100
            insights.append(
                f" Redução do quadro: {abs(saldo)} colaboradores ({percentual_reducao:.1f}%)"
            )
        else:
            insights.append(
                f"️ Quadro estável: admissões e demissões equilibradas"
            )
        
        # Insight sobre custo
        custo_percentual = (impacto_total / (media_funcionarios * 12000)) * 100  # Assume salário médio 12k/ano
        if custo_percentual > 20:
            insights.append(
                f" Impacto financeiro elevado: R$ {impacto_total:,.2f} "
                f"(~{custo_percentual:.1f}% da folha anual estimada)"
            )
        elif impacto_total > 100000:
            insights.append(
                f" Impacto financeiro significativo: R$ {impacto_total:,.2f}"
            )
        
        # Insight sobre padrão de rotatividade
        if admissoes > 0 and demissoes > 0:
            ratio = admissoes / demissoes
            if ratio > 1.5:
                insights.append(
                    f" Alta taxa de contratação: {admissoes} admissões vs {demissoes} demissões - "
                    f"possível expansão ou dificuldade de retenção"
                )
            elif ratio < 0.7:
                insights.append(
                    f" Alta taxa de desligamento: {demissoes} demissões vs {admissoes} admissões - "
                    f"possível reestruturação ou redução de custos"
                )
        
        return insights


