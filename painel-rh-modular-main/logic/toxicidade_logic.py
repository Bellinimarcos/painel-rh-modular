"""
Lógica de Negócio para Avaliação de Toxicidade em Lideranças
Projeto SER | Marcos Simões Bellini, CRP 04/37811
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from models.toxicidade_model import (
    QuestionarioToxicidade,
    ResultadoAvaliacao,
    RespostaAvaliacao
)


class GerenciadorAvaliacaoToxicidade:
    """Gerencia o processo de avaliação de toxicidade"""
    
    def __init__(self, questionario: QuestionarioToxicidade, data_dir: str = "data/toxicidade"):
        """
        Inicializa o gerenciador
        
        Args:
            questionario: Instância do questionário
            data_dir: Diretório para salvar dados
        """
        self.questionario = questionario
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivos de dados
        self.arquivo_avaliacoes = self.data_dir / "avaliacoes.json"
        self.arquivo_historico = self.data_dir / "historico.json"
    
    def iniciar_avaliacao(self) -> Dict[str, any]:
        """
        Inicia uma nova avaliação
        
        Returns:
            Dict com informações da avaliação iniciada
        """
        avaliacao_id = f"avaliacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "id": avaliacao_id,
            "timestamp_inicio": datetime.now().isoformat(),
            "status": "em_andamento",
            "questionario_versao": self.questionario.versao,
            "total_questoes": len(self.questionario)
        }
    
    def validar_respostas(self, respostas: Dict[int, int]) -> tuple[bool, List[str]]:
        """
        Valida as respostas fornecidas
        
        Args:
            respostas: Dicionário {questao_id: resposta}
            
        Returns:
            tuple: (é_valido, lista_de_erros)
        """
        return self.questionario.validar_respostas(respostas)
    
    def processar_avaliacao(
        self, 
        respostas: Dict[int, int],
        dados_participante: Optional[Dict[str, str]] = None
    ) -> ResultadoAvaliacao:
        """
        Processa uma avaliação completa
        
        Args:
            respostas: Respostas do participante
            dados_participante: Dados opcionais do participante
            
        Returns:
            ResultadoAvaliacao: Resultado completo da avaliação
        """
        # Valida respostas
        valido, erros = self.validar_respostas(respostas)
        if not valido:
            raise ValueError(f"Respostas inválidas: {', '.join(erros)}")
        
        # Calcula resultado
        resultado = self.questionario.calcular_resultado(respostas)
        
        # Adiciona dados do participante se fornecidos
        if dados_participante:
            resultado.resposta.dados_participante = dados_participante
        
        return resultado
    
    def salvar_resultado(self, resultado: ResultadoAvaliacao) -> str:
        """
        Salva o resultado da avaliação
        
        Args:
            resultado: Resultado da avaliação
            
        Returns:
            str: ID do resultado salvo
        """
        # Carrega resultados existentes
        resultados_existentes = self._carregar_avaliacoes()
        
        # Converte resultado para dicionário
        resultado_dict = {
            "id": resultado.resposta.id,
            "timestamp": resultado.data_avaliacao.isoformat(),
            "dados_participante": resultado.resposta.dados_participante,
            "respostas": resultado.resposta.respostas,
            "pontuacao_total": resultado.pontuacao_total,
            "nivel_risco_geral": resultado.nivel_risco_geral,
            "pontuacoes_dimensoes": resultado.pontuacoes_dimensoes,
            "niveis_risco_dimensoes": resultado.niveis_risco_dimensoes,
            "recomendacoes": resultado.recomendacoes
        }
        
        # Adiciona à lista
        resultados_existentes.append(resultado_dict)
        
        # Salva
        self._salvar_avaliacoes(resultados_existentes)
        
        # Atualiza histórico
        self._atualizar_historico(resultado_dict)
        
        return resultado.resposta.id
    
    def carregar_resultado(self, avaliacao_id: str) -> Optional[Dict]:
        """
        Carrega um resultado específico
        
        Args:
            avaliacao_id: ID da avaliação
            
        Returns:
            Dict ou None se não encontrado
        """
        avaliacoes = self._carregar_avaliacoes()
        
        for avaliacao in avaliacoes:
            if avaliacao["id"] == avaliacao_id:
                return avaliacao
        
        return None
    
    def listar_avaliacoes(
        self, 
        limite: Optional[int] = None,
        ordem_reversa: bool = True
    ) -> List[Dict]:
        """
        Lista todas as avaliações
        
        Args:
            limite: Número máximo de avaliações a retornar
            ordem_reversa: Se True, mais recentes primeiro
            
        Returns:
            Lista de avaliações
        """
        avaliacoes = self._carregar_avaliacoes()
        
        # Ordena por timestamp
        avaliacoes_ordenadas = sorted(
            avaliacoes,
            key=lambda x: x["timestamp"],
            reverse=ordem_reversa
        )
        
        if limite:
            return avaliacoes_ordenadas[:limite]
        
        return avaliacoes_ordenadas
    
    def obter_estatisticas(self) -> Dict:
        """
        Calcula estatísticas gerais das avaliações
        
        Returns:
            Dict com estatísticas
        """
        avaliacoes = self._carregar_avaliacoes()
        
        if not avaliacoes:
            return {
                "total_avaliacoes": 0,
                "media_pontuacao_geral": 0.0,
                "distribuicao_niveis_risco": {},
                "dimensoes_mais_criticas": []
            }
        
        # Calcula médias
        pontuacoes_totais = [a["pontuacao_total"] for a in avaliacoes]
        media_geral = sum(pontuacoes_totais) / len(pontuacoes_totais)
        
        # Distribui níveis de risco
        distribuicao_risco = {}
        for avaliacao in avaliacoes:
            nivel = avaliacao["nivel_risco_geral"]
            distribuicao_risco[nivel] = distribuicao_risco.get(nivel, 0) + 1
        
        # Identifica dimensões mais problemáticas
        pontuacoes_por_dimensao = {}
        for avaliacao in avaliacoes:
            for dimensao, pontuacao in avaliacao["pontuacoes_dimensoes"].items():
                if dimensao not in pontuacoes_por_dimensao:
                    pontuacoes_por_dimensao[dimensao] = []
                pontuacoes_por_dimensao[dimensao].append(pontuacao)
        
        medias_dimensoes = {
            dim: sum(ponts) / len(ponts)
            for dim, ponts in pontuacoes_por_dimensao.items()
        }
        
        dimensoes_ordenadas = sorted(
            medias_dimensoes.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "total_avaliacoes": len(avaliacoes),
            "media_pontuacao_geral": media_geral,
            "distribuicao_niveis_risco": distribuicao_risco,
            "medias_por_dimensao": medias_dimensoes,
            "dimensoes_mais_criticas": dimensoes_ordenadas[:3]
        }
    
    def exportar_resultados(
        self, 
        formato: str = "json",
        caminho: Optional[str] = None
    ) -> str:
        """
        Exporta todos os resultados
        
        Args:
            formato: Formato de exportação (json, csv)
            caminho: Caminho do arquivo (None = gera automaticamente)
            
        Returns:
            str: Caminho do arquivo gerado
        """
        avaliacoes = self._carregar_avaliacoes()
        
        if not caminho:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho = str(self.data_dir / f"export_{timestamp}.{formato}")
        
        if formato == "json":
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(avaliacoes, f, indent=2, ensure_ascii=False)
        
        elif formato == "csv":
            import csv
            
            with open(caminho, 'w', newline='', encoding='utf-8') as f:
                if not avaliacoes:
                    return caminho
                
                # Define campos
                campos = [
                    'id', 'timestamp', 'pontuacao_total', 'nivel_risco_geral'
                ]
                
                # Adiciona dimensões
                primeira_avaliacao = avaliacoes[0]
                campos.extend(primeira_avaliacao['pontuacoes_dimensoes'].keys())
                
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                
                for avaliacao in avaliacoes:
                    linha = {
                        'id': avaliacao['id'],
                        'timestamp': avaliacao['timestamp'],
                        'pontuacao_total': avaliacao['pontuacao_total'],
                        'nivel_risco_geral': avaliacao['nivel_risco_geral']
                    }
                    linha.update(avaliacao['pontuacoes_dimensoes'])
                    writer.writerow(linha)
        
        return caminho
    
    def _carregar_avaliacoes(self) -> List[Dict]:
        """Carrega avaliações do arquivo JSON"""
        if not self.arquivo_avaliacoes.exists():
            return []
        
        try:
            with open(self.arquivo_avaliacoes, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _salvar_avaliacoes(self, avaliacoes: List[Dict]):
        """Salva avaliações no arquivo JSON"""
        with open(self.arquivo_avaliacoes, 'w', encoding='utf-8') as f:
            json.dump(avaliacoes, f, indent=2, ensure_ascii=False)
    
    def _atualizar_historico(self, resultado: Dict):
        """Atualiza arquivo de histórico"""
        historico = []
        
        if self.arquivo_historico.exists():
            try:
                with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                    historico = json.load(f)
            except (json.JSONDecodeError, IOError):
                historico = []
        
        # Adiciona resumo ao histórico
        resumo = {
            "id": resultado["id"],
            "timestamp": resultado["timestamp"],
            "pontuacao_total": resultado["pontuacao_total"],
            "nivel_risco": resultado["nivel_risco_geral"]
        }
        
        historico.append(resumo)
        
        with open(self.arquivo_historico, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=2, ensure_ascii=False)
    
    def limpar_dados(self, confirmar: bool = False):
        """
        Limpa todos os dados salvos
        
        Args:
            confirmar: Deve ser True para executar (segurança)
        """
        if not confirmar:
            raise ValueError("É necessário confirmar a exclusão de dados")
        
        if self.arquivo_avaliacoes.exists():
            self.arquivo_avaliacoes.unlink()
        
        if self.arquivo_historico.exists():
            self.arquivo_historico.unlink()


def criar_gerenciador(questionario: QuestionarioToxicidade) -> GerenciadorAvaliacaoToxicidade:
    """
    Factory function para criar gerenciador
    
    Args:
        questionario: Instância do questionário
        
    Returns:
        GerenciadorAvaliacaoToxicidade: Gerenciador configurado
    """
    return GerenciadorAvaliacaoToxicidade(questionario)