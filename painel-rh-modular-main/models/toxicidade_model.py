"""
Models para Avaliação de Toxicidade em Lideranças
Projeto SER | Marcos Simões Bellini, CRP 04/37811
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class TipoQuestao(Enum):
    """Tipo de questão: direta (maior pontuação = mais tóxico) ou inversa"""
    DIRETA = "direta"
    INVERSA = "inversa"


@dataclass
class Questao:
    """Representa uma questão do questionário"""
    id: int
    texto: str
    tipo: TipoQuestao
    dimensao_id: str
    
    def calcular_pontuacao(self, resposta: int) -> float:
        """
        Calcula a pontuação da questão baseada no tipo
        
        Args:
            resposta: Valor de 1 a 5 da escala Likert
            
        Returns:
            float: Pontuação normalizada (0-100)
        """
        if self.tipo == TipoQuestao.INVERSA:
            # Questão inversa: resposta alta (concordo) = comportamento bom = pontuação baixa
            resposta = 6 - resposta  # Inverte: 5→1, 4→2, 3→3, 2→4, 1→5
        
        # Normaliza para escala 0-100
        # 1 = 0 pontos, 5 = 100 pontos
        return ((resposta - 1) / 4) * 100


@dataclass
class Dimensao:
    """Representa uma dimensão da toxicidade"""
    id: str
    nome: str
    descricao: str
    questoes: List[Questao] = field(default_factory=list)
    
    def calcular_pontuacao_media(self, respostas: Dict[int, int]) -> float:
        """
        Calcula a pontuação média da dimensão
        
        Args:
            respostas: Dicionário {questao_id: resposta}
            
        Returns:
            float: Pontuação média (0-100)
        """
        if not self.questoes:
            return 0.0
        
        pontuacoes = []
        for questao in self.questoes:
            if questao.id in respostas:
                pontuacao = questao.calcular_pontuacao(respostas[questao.id])
                pontuacoes.append(pontuacao)
        
        if not pontuacoes:
            return 0.0
        
        return sum(pontuacoes) / len(pontuacoes)
    
    def obter_nivel_risco(self, pontuacao: float) -> str:
        """
        Determina o nível de risco baseado na pontuação
        
        Args:
            pontuacao: Pontuação da dimensão (0-100)
            
        Returns:
            str: Nível de risco
        """
        if pontuacao < 25:
            return "Excelente"
        elif pontuacao < 50:
            return "Baixo"
        elif pontuacao < 75:
            return "Moderado"
        else:
            return "Alto"


@dataclass
class RespostaAvaliacao:
    """Representa as respostas de uma avaliação"""
    id: str
    timestamp: datetime
    respostas: Dict[int, int]  # {questao_id: resposta}
    dados_participante: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validação após inicialização"""
        if not self.respostas:
            raise ValueError("Respostas não podem estar vazias")
        
        # Valida que todas as respostas estão entre 1 e 5
        for questao_id, resposta in self.respostas.items():
            if not 1 <= resposta <= 5:
                raise ValueError(f"Resposta inválida para questão {questao_id}: {resposta}")


@dataclass
class ResultadoAvaliacao:
    """Representa o resultado completo de uma avaliação"""
    resposta: RespostaAvaliacao
    pontuacao_total: float
    pontuacoes_dimensoes: Dict[str, float]
    nivel_risco_geral: str
    niveis_risco_dimensoes: Dict[str, str]
    recomendacoes: List[str] = field(default_factory=list)
    
    @property
    def data_avaliacao(self) -> datetime:
        """Retorna a data da avaliação"""
        return self.resposta.timestamp
    
    def obter_dimensoes_criticas(self, limite: float = 75.0) -> List[tuple[str, float]]:
        """
        Retorna dimensões com pontuação acima do limite
        
        Args:
            limite: Pontuação limite para considerar crítico
            
        Returns:
            List[tuple]: Lista de (dimensao, pontuacao) ordenada por pontuação
        """
        criticas = [
            (dim, pont) 
            for dim, pont in self.pontuacoes_dimensoes.items() 
            if pont >= limite
        ]
        return sorted(criticas, key=lambda x: x[1], reverse=True)
    
    def obter_dimensoes_positivas(self, limite: float = 25.0) -> List[tuple[str, float]]:
        """
        Retorna dimensões com pontuação abaixo do limite (aspectos positivos)
        
        Args:
            limite: Pontuação limite para considerar positivo
            
        Returns:
            List[tuple]: Lista de (dimensao, pontuacao) ordenada por pontuação
        """
        positivas = [
            (dim, pont) 
            for dim, pont in self.pontuacoes_dimensoes.items() 
            if pont < limite
        ]
        return sorted(positivas, key=lambda x: x[1])


@dataclass
class QuestionarioToxicidade:
    """Representa o questionário completo de toxicidade"""
    titulo: str
    descricao: str
    dimensoes: List[Dimensao] = field(default_factory=list)
    versao: str = "1.0"
    
    def adicionar_dimensao(self, dimensao: Dimensao):
        """Adiciona uma dimensão ao questionário"""
        if any(d.id == dimensao.id for d in self.dimensoes):
            raise ValueError(f"Dimensão com ID {dimensao.id} já existe")
        self.dimensoes.append(dimensao)
    
    def obter_dimensao(self, dimensao_id: str) -> Optional[Dimensao]:
        """Retorna uma dimensão pelo ID"""
        return next((d for d in self.dimensoes if d.id == dimensao_id), None)
    
    def obter_todas_questoes(self) -> List[Questao]:
        """Retorna todas as questões de todas as dimensões"""
        questoes = []
        for dimensao in self.dimensoes:
            questoes.extend(dimensao.questoes)
        return questoes
    
    def calcular_resultado(self, respostas: Dict[int, int]) -> ResultadoAvaliacao:
        """
        Calcula o resultado completo da avaliação
        
        Args:
            respostas: Dicionário {questao_id: resposta}
            
        Returns:
            ResultadoAvaliacao: Resultado completo
        """
        # Calcula pontuações por dimensão
        pontuacoes_dimensoes = {}
        niveis_risco_dimensoes = {}
        
        for dimensao in self.dimensoes:
            pontuacao = dimensao.calcular_pontuacao_media(respostas)
            pontuacoes_dimensoes[dimensao.nome] = pontuacao
            niveis_risco_dimensoes[dimensao.nome] = dimensao.obter_nivel_risco(pontuacao)
        
        # Calcula pontuação total (média de todas as dimensões)
        pontuacao_total = sum(pontuacoes_dimensoes.values()) / len(pontuacoes_dimensoes)
        
        # Determina nível de risco geral
        if pontuacao_total < 25:
            nivel_risco_geral = "Excelente"
        elif pontuacao_total < 50:
            nivel_risco_geral = "Baixo"
        elif pontuacao_total < 75:
            nivel_risco_geral = "Moderado"
        else:
            nivel_risco_geral = "Alto"
        
        # Gera recomendações
        recomendacoes = self._gerar_recomendacoes(
            pontuacao_total, 
            pontuacoes_dimensoes
        )
        
        # Cria objeto de resposta
        resposta = RespostaAvaliacao(
            id=f"avaliacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            respostas=respostas
        )
        
        return ResultadoAvaliacao(
            resposta=resposta,
            pontuacao_total=pontuacao_total,
            pontuacoes_dimensoes=pontuacoes_dimensoes,
            nivel_risco_geral=nivel_risco_geral,
            niveis_risco_dimensoes=niveis_risco_dimensoes,
            recomendacoes=recomendacoes
        )
    
    def _gerar_recomendacoes(
        self, 
        pontuacao_total: float, 
        pontuacoes_dimensoes: Dict[str, float]
    ) -> List[str]:
        """
        Gera recomendações baseadas nos resultados
        
        Args:
            pontuacao_total: Pontuação geral
            pontuacoes_dimensoes: Pontuações por dimensão
            
        Returns:
            List[str]: Lista de recomendações
        """
        recomendacoes = []
        
        # Recomendações gerais
        if pontuacao_total >= 75:
            recomendacoes.append(
                "⚠️ URGENTE: Situação crítica detectada. "
                "Recomenda-se intervenção imediata do RH e suporte psicológico à equipe."
            )
        elif pontuacao_total >= 50:
            recomendacoes.append(
                "⚠️ ATENÇÃO: Sinais significativos de toxicidade. "
                "Recomenda-se avaliação aprofundada e plano de ação corretivo."
            )
        elif pontuacao_total >= 25:
            recomendacoes.append(
                "✓ Situação dentro de limites aceitáveis, mas há pontos de atenção. "
                "Monitoramento regular é recomendado."
            )
        else:
            recomendacoes.append(
                "✓ Excelente ambiente de liderança. "
                "Manter práticas atuais e fortalecer pontos positivos."
            )
        
        # Recomendações específicas por dimensão
        dimensoes_criticas = [
            (dim, pont) 
            for dim, pont in pontuacoes_dimensoes.items() 
            if pont >= 75
        ]
        
        if dimensoes_criticas:
            recomendacoes.append(
                f"\n**Dimensões Críticas Identificadas:**"
            )
            for dimensao, pontuacao in sorted(dimensoes_criticas, key=lambda x: x[1], reverse=True):
                recomendacoes.append(
                    f"- {dimensao}: {pontuacao:.1f} pontos - Requer ação imediata"
                )
        
        # Recomendações de ações
        if pontuacao_total >= 50:
            recomendacoes.extend([
                "\n**Ações Recomendadas:**",
                "1. Realizar entrevistas individuais confidenciais com membros da equipe",
                "2. Considerar programa de coaching ou mentoria para o líder",
                "3. Implementar canais seguros de feedback anônimo",
                "4. Avaliar possibilidade de realocação ou mudanças estruturais",
                "5. Estabelecer plano de acompanhamento com prazos definidos"
            ])
        
        return recomendacoes
    
    def validar_respostas(self, respostas: Dict[int, int]) -> tuple[bool, List[str]]:
        """
        Valida se as respostas estão completas e corretas
        
        Args:
            respostas: Dicionário {questao_id: resposta}
            
        Returns:
            tuple: (é_valido, lista_de_erros)
        """
        erros = []
        todas_questoes = self.obter_todas_questoes()
        ids_questoes = {q.id for q in todas_questoes}
        
        # Verifica se todas as questões foram respondidas
        questoes_faltantes = ids_questoes - set(respostas.keys())
        if questoes_faltantes:
            erros.append(
                f"Questões não respondidas: {sorted(questoes_faltantes)}"
            )
        
        # Verifica se há respostas para questões inexistentes
        questoes_extras = set(respostas.keys()) - ids_questoes
        if questoes_extras:
            erros.append(
                f"Respostas para questões inexistentes: {sorted(questoes_extras)}"
            )
        
        # Valida valores das respostas
        for questao_id, resposta in respostas.items():
            if not 1 <= resposta <= 5:
                erros.append(
                    f"Resposta inválida para questão {questao_id}: {resposta} "
                    "(deve estar entre 1 e 5)"
                )
        
        return len(erros) == 0, erros
    
    def exportar_estrutura(self) -> Dict:
        """
        Exporta a estrutura do questionário para um dicionário
        
        Returns:
            Dict: Estrutura completa do questionário
        """
        return {
            "titulo": self.titulo,
            "descricao": self.descricao,
            "versao": self.versao,
            "total_dimensoes": len(self.dimensoes),
            "total_questoes": len(self.obter_todas_questoes()),
            "dimensoes": [
                {
                    "id": dim.id,
                    "nome": dim.nome,
                    "descricao": dim.descricao,
                    "total_questoes": len(dim.questoes),
                    "questoes": [
                        {
                            "id": q.id,
                            "texto": q.texto,
                            "tipo": q.tipo.value
                        }
                        for q in dim.questoes
                    ]
                }
                for dim in self.dimensoes
            ]
        }
    
    def __len__(self) -> int:
        """Retorna o número total de questões"""
        return len(self.obter_todas_questoes())
    
    def __str__(self) -> str:
        """Representação em string do questionário"""
        return (
            f"{self.titulo} (v{self.versao})\n"
            f"Dimensões: {len(self.dimensoes)}\n"
            f"Questões: {len(self)}"
        )