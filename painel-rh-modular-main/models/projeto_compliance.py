"""
Modelo de dados para Projetos de Compliance RPS
Gerencia projetos de avaliação de Riscos Psicossociais e SST
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class StatusProjeto(Enum):
    """Status do projeto de compliance"""
    CRIADO = "Criado"
    EM_AVALIACAO = "Em Avaliação"
    ANALISE = "Em Análise"
    PLANOS_ACAO = "Planos de Ação"
    CONCLUIDO = "Concluído"

class StatusFerramenta(Enum):
    """Status de aplicação de cada ferramenta"""
    NAO_APLICADA = "Não Aplicada"
    EM_COLETA = "Em Coleta"
    FINALIZADA = "Finalizada"

@dataclass
class FerramentaAplicada:
    """Representa uma ferramenta aplicada no projeto"""
    nome: str  # "COPSOQ III", "CBI", "DUWAS", etc.
    status: StatusFerramenta
    data_inicio: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None
    num_respondentes: int = 0
    resultados_path: Optional[str] = None  # Caminho para resultados salvos
    
    def progresso(self) -> str:
        """Retorna string de progresso visual"""
        if self.status == StatusFerramenta.FINALIZADA:
            return f" {self.num_respondentes} respondentes"
        elif self.status == StatusFerramenta.EM_COLETA:
            return f" {self.num_respondentes} respondentes"
        else:
            return "⏳ Pendente"

@dataclass
class ProjetoCompliance:
    """
    Projeto de Compliance RPS para uma empresa
    Centraliza todas as avaliações e documentações NR-1/NR-17
    """
    # Identificação
    id: str
    nome_empresa: str
    cnpj: Optional[str] = None
    
    # Dados organizacionais
    setor_atividade: str = ""
    num_funcionarios: int = 0
    responsavel_tecnico: str = ""
    
    # Controle do projeto
    data_criacao: datetime = field(default_factory=datetime.now)
    data_atualizacao: datetime = field(default_factory=datetime.now)
    status: StatusProjeto = StatusProjeto.CRIADO
    
    # Ferramentas aplicadas
    ferramentas: Dict[str, FerramentaAplicada] = field(default_factory=dict)
    
    # Resultados consolidados
    total_respondentes: int = 0
    riscos_identificados: int = 0
    planos_acao_criados: int = 0
    
    # Documentação gerada
    inventario_pgr_gerado: bool = False
    aep_nr17_gerada: bool = False
    relatorio_executivo_gerado: bool = False
    
    def adicionar_ferramenta(self, nome: str) -> None:
        """Adiciona uma ferramenta ao projeto"""
        if nome not in self.ferramentas:
            self.ferramentas[nome] = FerramentaAplicada(
                nome=nome,
                status=StatusFerramenta.NAO_APLICADA
            )
            self.data_atualizacao = datetime.now()
    
    def iniciar_ferramenta(self, nome: str) -> None:
        """Marca ferramenta como em coleta"""
        if nome in self.ferramentas:
            self.ferramentas[nome].status = StatusFerramenta.EM_COLETA
            self.ferramentas[nome].data_inicio = datetime.now()
            self.data_atualizacao = datetime.now()
            if self.status == StatusProjeto.CRIADO:
                self.status = StatusProjeto.EM_AVALIACAO
    
    def finalizar_ferramenta(self, nome: str, num_respondentes: int, resultados_path: str) -> None:
        """Marca ferramenta como finalizada"""
        if nome in self.ferramentas:
            self.ferramentas[nome].status = StatusFerramenta.FINALIZADA
            self.ferramentas[nome].data_conclusao = datetime.now()
            self.ferramentas[nome].num_respondentes = num_respondentes
            self.ferramentas[nome].resultados_path = resultados_path
            self.data_atualizacao = datetime.now()
            self._atualizar_totais()
    
    def _atualizar_totais(self) -> None:
        """Atualiza contadores totais do projeto"""
        respondentes = set()
        for ferr in self.ferramentas.values():
            if ferr.status == StatusFerramenta.FINALIZADA:
                respondentes.add(ferr.num_respondentes)
        
        if respondentes:
            self.total_respondentes = max(respondentes)
    
    def progresso_geral(self) -> float:
        """Retorna progresso geral do projeto (0-100)"""
        if not self.ferramentas:
            return 0.0
        
        finalizadas = sum(1 for f in self.ferramentas.values() 
                         if f.status == StatusFerramenta.FINALIZADA)
        return (finalizadas / len(self.ferramentas)) * 100
    
    def pode_gerar_pgr(self) -> bool:
        """Verifica se há dados suficientes para gerar PGR"""
        return any(f.status == StatusFerramenta.FINALIZADA 
                  for f in self.ferramentas.values())
    
    def resumo_status(self) -> str:
        """Retorna resumo textual do status"""
        if self.status == StatusProjeto.CONCLUIDO:
            return " Projeto Concluído - Documentação gerada"
        elif self.status == StatusProjeto.PLANOS_ACAO:
            return " Planos de Ação em desenvolvimento"
        elif self.status == StatusProjeto.ANALISE:
            return " Análise de resultados em andamento"
        elif self.status == StatusProjeto.EM_AVALIACAO:
            return f" Avaliações em andamento - {self.progresso_geral():.0f}% completo"
        else:
            return " Projeto iniciado - Configure as ferramentas"

# Ferramentas disponíveis no sistema
FERRAMENTAS_DISPONIVEIS = {
    "COPSOQ III": {
        "nome_completo": "Copenhagen Psychosocial Questionnaire III",
        "descricao": "Avaliação de riscos psicossociais (84 questões - Versão Média)",
        "icone": "️",
        "validacao": "Dra. Teresa Cotrim",
        "nr_relacionada": "NR-1, NR-17"
    },
    "COPSOQ II": {
        "nome_completo": "Copenhagen Psychosocial Questionnaire II",
        "descricao": "Versão anterior do COPSOQ (validada Brasil)",
        "icone": "",
        "validacao": "Validação Brasil",
        "nr_relacionada": "NR-1, NR-17"
    },
    "CBI": {
        "nome_completo": "Copenhagen Burnout Inventory",
        "descricao": "Avaliação de esgotamento profissional",
        "icone": "",
        "validacao": "Internacional",
        "nr_relacionada": "NR-1"
    },
    "DUWAS": {
        "nome_completo": "Dutch Work Addiction Scale",
        "descricao": "Avaliação de workaholism",
        "icone": "",
        "validacao": "Internacional",
        "nr_relacionada": "NR-1"
    },
    "Absenteísmo": {
        "nome_completo": "Análise de Absenteísmo",
        "descricao": "Índices de faltas e afastamentos",
        "icone": "",
        "validacao": "Indicador RH",
        "nr_relacionada": "NR-1"
    },
    "Turnover": {
        "nome_completo": "Análise de Rotatividade",
        "descricao": "Índices de turnover voluntário/involuntário",
        "icone": "",
        "validacao": "Indicador RH",
        "nr_relacionada": "NR-1"
    }
}


