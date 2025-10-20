"""
Consolidador de Resultados de Múltiplas Ferramentas
Integra resultados do COPSOQ III, CBI, DUWAS e outras ferramentas
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

class ConsolidadorResultados:
    """Consolida resultados de diferentes ferramentas de avaliação"""
    
    def __init__(self):
        """Inicializa o consolidador"""
        self.resultados = {}
        self.riscos_consolidados = []
    
    def adicionar_resultados_copsoq(self, respondentes: List[Dict]) -> None:
        """
        Adiciona resultados do COPSOQ III
        
        Args:
            respondentes: Lista de respondentes com scores
        """
        if not respondentes:
            return
        
        # Calcular médias por dimensão
        df = pd.DataFrame([r['scores'] for r in respondentes])
        medias = df.mean()
        
        # Identificar dimensões de risco (score < 40)
        dimensoes_risco = medias[medias < 40]
        
        self.resultados['copsoq'] = {
            'ferramenta': 'COPSOQ III',
            'num_respondentes': len(respondentes),
            'dimensoes_avaliadas': len(medias),
            'scores_medios': medias.to_dict(),
            'dimensoes_risco': list(dimensoes_risco.index),
            'num_riscos': len(dimensoes_risco)
        }
        
        # Adicionar aos riscos consolidados
        for dimensao, score in dimensoes_risco.items():
            self.riscos_consolidados.append({
                'fonte': 'COPSOQ III',
                'tipo': 'Risco Psicossocial',
                'dimensao': dimensao,
                'score': round(score, 1),
                'severidade': self._calcular_severidade_copsoq(score),
                'descricao': f'Score baixo em {dimensao}: {score:.1f}/100',
                'nr_relacionada': 'NR-1, NR-17'
            })
    
    def adicionar_resultados_cbi(self, resultados_cbi: Dict) -> None:
        """
        Adiciona resultados do Copenhagen Burnout Inventory
        
        Args:
            resultados_cbi: Dicionário com resultados CBI
        """
        if not resultados_cbi:
            return
        
        self.resultados['cbi'] = {
            'ferramenta': 'CBI - Burnout',
            'num_respondentes': resultados_cbi.get('num_respondentes', 0),
            'score_medio': resultados_cbi.get('score_medio', 0),
            'nivel_risco': resultados_cbi.get('nivel_risco', 'Baixo')
        }
        
        # Se detectou burnout, adicionar aos riscos
        if resultados_cbi.get('nivel_risco') in ['Alto', 'Muito Alto']:
            self.riscos_consolidados.append({
                'fonte': 'CBI',
                'tipo': 'Esgotamento Profissional',
                'dimensao': 'Burnout',
                'score': resultados_cbi.get('score_medio', 0),
                'severidade': 4 if resultados_cbi.get('nivel_risco') == 'Muito Alto' else 3,
                'descricao': f"Nível de burnout {resultados_cbi.get('nivel_risco')}",
                'nr_relacionada': 'NR-1'
            })
    
    def adicionar_resultados_duwas(self, resultados_duwas: Dict) -> None:
        """
        Adiciona resultados do DUWAS (Workaholism)
        
        Args:
            resultados_duwas: Dicionário com resultados DUWAS
        """
        if not resultados_duwas:
            return
        
        self.resultados['duwas'] = {
            'ferramenta': 'DUWAS - Workaholism',
            'num_respondentes': resultados_duwas.get('num_respondentes', 0),
            'score_medio': resultados_duwas.get('score_medio', 0),
            'nivel_risco': resultados_duwas.get('nivel_risco', 'Baixo')
        }
        
        # Se detectou workaholism, adicionar aos riscos
        if resultados_duwas.get('nivel_risco') in ['Alto', 'Muito Alto']:
            self.riscos_consolidados.append({
                'fonte': 'DUWAS',
                'tipo': 'Vício em Trabalho',
                'dimensao': 'Workaholism',
                'score': resultados_duwas.get('score_medio', 0),
                'severidade': 3,
                'descricao': f"Nível de workaholism {resultados_duwas.get('nivel_risco')}",
                'nr_relacionada': 'NR-1'
            })
    
    def adicionar_indicadores_rh(self, absenteismo: float = 0, turnover: float = 0) -> None:
        """
        Adiciona indicadores de RH
        
        Args:
            absenteismo: Taxa de absenteísmo (%)
            turnover: Taxa de turnover (%)
        """
        self.resultados['indicadores_rh'] = {
            'absenteismo': absenteismo,
            'turnover': turnover
        }
        
        # Absenteísmo alto é risco
        if absenteismo > 5.0:  # Threshold: 5%
            self.riscos_consolidados.append({
                'fonte': 'Indicadores RH',
                'tipo': 'Indicador Organizacional',
                'dimensao': 'Absenteísmo',
                'score': absenteismo,
                'severidade': 3 if absenteismo > 10 else 2,
                'descricao': f'Taxa de absenteísmo elevada: {absenteismo:.1f}%',
                'nr_relacionada': 'NR-1'
            })
        
        # Turnover alto é risco
        if turnover > 15.0:  # Threshold: 15%
            self.riscos_consolidados.append({
                'fonte': 'Indicadores RH',
                'tipo': 'Indicador Organizacional',
                'dimensao': 'Turnover',
                'score': turnover,
                'severidade': 3 if turnover > 25 else 2,
                'descricao': f'Taxa de rotatividade elevada: {turnover:.1f}%',
                'nr_relacionada': 'NR-1'
            })
    
    def _calcular_severidade_copsoq(self, score: float) -> int:
        """
        Calcula severidade baseada no score COPSOQ
        
        Args:
            score: Score da dimensão (0-100)
            
        Returns:
            Severidade (1-5)
        """
        if score < 20:
            return 5  # Crítico
        elif score < 30:
            return 4  # Alto
        elif score < 40:
            return 3  # Médio
        else:
            return 2  # Baixo
    
    def gerar_inventario_riscos(self) -> pd.DataFrame:
        """
        Gera inventário consolidado de riscos
        
        Returns:
            DataFrame com todos os riscos identificados
        """
        if not self.riscos_consolidados:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.riscos_consolidados)
        
        # Ordenar por severidade (maior primeiro)
        df = df.sort_values('severidade', ascending=False)
        
        return df
    
    def gerar_matriz_risco(self) -> Dict:
        """
        Gera matriz de probabilidade × severidade
        
        Returns:
            Dict com contagem de riscos por célula da matriz
        """
        matriz = {}
        
        for risco in self.riscos_consolidados:
            # Assumir probabilidade baseada na fonte
            if risco['fonte'] in ['COPSOQ III', 'CBI', 'DUWAS']:
                probabilidade = 4  # Alta (dados de avaliação direta)
            else:
                probabilidade = 3  # Média (indicadores indiretos)
            
            severidade = risco['severidade']
            
            key = f"P{probabilidade}_S{severidade}"
            matriz[key] = matriz.get(key, 0) + 1
        
        return matriz
    
    def calcular_nivel_risco_geral(self) -> str:
        """
        Calcula nível de risco geral da organização
        
        Returns:
            String com nível de risco
        """
        if not self.riscos_consolidados:
            return "BAIXO"
        
        # Contar riscos por severidade
        criticos = sum(1 for r in self.riscos_consolidados if r['severidade'] >= 4)
        altos = sum(1 for r in self.riscos_consolidados if r['severidade'] == 3)
        
        if criticos >= 3:
            return "CRÍTICO"
        elif criticos >= 1 or altos >= 5:
            return "ALTO"
        elif altos >= 2:
            return "MÉDIO"
        else:
            return "BAIXO"
    
    def gerar_resumo_executivo(self) -> Dict:
        """
        Gera resumo executivo consolidado
        
        Returns:
            Dict com resumo executivo
        """
        total_respondentes = sum(
            r.get('num_respondentes', 0) 
            for r in self.resultados.values() 
            if 'num_respondentes' in r
        )
        
        return {
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'ferramentas_aplicadas': len(self.resultados),
            'total_respondentes': total_respondentes,
            'total_riscos_identificados': len(self.riscos_consolidados),
            'nivel_risco_geral': self.calcular_nivel_risco_geral(),
            'principais_riscos': self._get_top_riscos(5),
            'recomendacoes_prioritarias': self._gerar_recomendacoes()
        }
    
    def _get_top_riscos(self, n: int = 5) -> List[Dict]:
        """Retorna os N riscos mais severos"""
        riscos_ordenados = sorted(
            self.riscos_consolidados, 
            key=lambda x: x['severidade'], 
            reverse=True
        )
        return riscos_ordenados[:n]
    
    def _gerar_recomendacoes(self) -> List[str]:
        """Gera recomendações baseadas nos riscos identificados"""
        recomendacoes = []
        
        # Análise por fonte
        tem_copsoq = 'copsoq' in self.resultados
        tem_burnout = 'cbi' in self.resultados and self.resultados['cbi'].get('nivel_risco') in ['Alto', 'Muito Alto']
        tem_indicadores_ruins = 'indicadores_rh' in self.resultados
        
        if tem_copsoq and self.resultados['copsoq']['num_riscos'] > 5:
            recomendacoes.append("Implementar programa abrangente de gestão de riscos psicossociais")
        
        if tem_burnout:
            recomendacoes.append("Ações urgentes de prevenção e tratamento de burnout")
        
        if tem_indicadores_ruins:
            ind = self.resultados['indicadores_rh']
            if ind.get('absenteismo', 0) > 5:
                recomendacoes.append("Investigar causas do absenteísmo elevado")
            if ind.get('turnover', 0) > 15:
                recomendacoes.append("Revisar políticas de retenção de talentos")
        
        if not recomendacoes:
            recomendacoes.append("Manter monitoramento periódico dos riscos psicossociais")
        
        return recomendacoes
    
    def exportar_para_dict(self) -> Dict:
        """
        Exporta todos os dados consolidados
        
        Returns:
            Dict completo com todos os resultados
        """
        return {
            'resultados': self.resultados,
            'riscos': self.riscos_consolidados,
            'resumo_executivo': self.gerar_resumo_executivo(),
            'matriz_risco': self.gerar_matriz_risco()
        }