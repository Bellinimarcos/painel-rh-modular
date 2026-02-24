"""
Serviço de Gerenciamento de Projetos de Compliance RPS
Gerencia CRUD e persistência de projetos
"""

import json
import os
from typing import List, Optional, Dict
from datetime import datetime
from models.projeto_compliance import ProjetoCompliance, StatusProjeto, FERRAMENTAS_DISPONIVEIS
import streamlit as st

class ComplianceManager:
    """Gerenciador central de projetos de compliance"""
    
    def __init__(self, data_dir: str = "data/compliance"):
        """
        Inicializa o gerenciador
        
        Args:
            data_dir: Diretório para armazenar projetos
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.projetos_file = os.path.join(data_dir, "projetos.json")
        self._cache = {}
    
    def _get_projeto_path(self, projeto_id: str) -> str:
        """Retorna caminho do arquivo de um projeto"""
        return os.path.join(self.data_dir, f"projeto_{projeto_id}.json")
    
    def criar_projeto(self, nome_empresa: str, cnpj: Optional[str] = None,
                     setor: str = "", num_funcionarios: int = 0,
                     responsavel: str = "") -> ProjetoCompliance:
        """
        Cria novo projeto de compliance
        
        Args:
            nome_empresa: Nome da empresa
            cnpj: CNPJ da empresa
            setor: Setor de atividade
            num_funcionarios: Número de funcionários
            responsavel: Nome do responsável técnico
            
        Returns:
            ProjetoCompliance criado
        """
        # Limpar nome para criar ID válido (SEM ASPAS!)
        nome_limpo = nome_empresa.lower()
        nome_limpo = nome_limpo.replace(' ', '_')
        nome_limpo = nome_limpo.replace('"', '')
        nome_limpo = nome_limpo.replace("'", '')
        nome_limpo = ''.join(c for c in nome_limpo if c.isalnum() or c == '_')
        
        projeto_id = f"{nome_limpo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        projeto = ProjetoCompliance(
            id=projeto_id,
            nome_empresa=nome_empresa,
            cnpj=cnpj,
            setor_atividade=setor,
            num_funcionarios=num_funcionarios,
            responsavel_tecnico=responsavel
        )
        
        self.salvar_projeto(projeto)
        return projeto
    
    def salvar_projeto(self, projeto: ProjetoCompliance) -> bool:
        """
        Salva projeto em disco
        
        Args:
            projeto: Projeto a ser salvo
            
        Returns:
            True se salvou com sucesso
        """
        try:
            projeto.data_atualizacao = datetime.now()
            
            # Converter para dict
            projeto_dict = {
                'id': projeto.id,
                'nome_empresa': projeto.nome_empresa,
                'cnpj': projeto.cnpj,
                'setor_atividade': projeto.setor_atividade,
                'num_funcionarios': projeto.num_funcionarios,
                'responsavel_tecnico': projeto.responsavel_tecnico,
                'data_criacao': projeto.data_criacao.isoformat(),
                'data_atualizacao': projeto.data_atualizacao.isoformat(),
                'status': projeto.status.value,
                'ferramentas': {
                    nome: {
                        'nome': ferr.nome,
                        'status': ferr.status.value,
                        'data_inicio': ferr.data_inicio.isoformat() if ferr.data_inicio else None,
                        'data_conclusao': ferr.data_conclusao.isoformat() if ferr.data_conclusao else None,
                        'num_respondentes': ferr.num_respondentes,
                        'resultados_path': ferr.resultados_path
                    }
                    for nome, ferr in projeto.ferramentas.items()
                },
                'total_respondentes': projeto.total_respondentes,
                'riscos_identificados': projeto.riscos_identificados,
                'planos_acao_criados': projeto.planos_acao_criados,
                'inventario_pgr_gerado': projeto.inventario_pgr_gerado,
                'aep_nr17_gerada': projeto.aep_nr17_gerada,
                'relatorio_executivo_gerado': projeto.relatorio_executivo_gerado
            }
            
            # Salvar arquivo individual do projeto
            with open(self._get_projeto_path(projeto.id), 'w', encoding='utf-8') as f:
                json.dump(projeto_dict, f, indent=2, ensure_ascii=False)
            
            # Atualizar índice de projetos
            self._atualizar_indice(projeto)
            
            # Atualizar cache
            self._cache[projeto.id] = projeto
            
            return True
        except Exception as e:
            st.error(f"Erro ao salvar projeto: {e}")
            return False
    
    def _atualizar_indice(self, projeto: ProjetoCompliance) -> None:
        """Atualiza arquivo índice com lista de projetos"""
        indice = self._carregar_indice()
        
        # Atualizar ou adicionar projeto no índice
        indice[projeto.id] = {
            'nome_empresa': projeto.nome_empresa,
            'status': projeto.status.value,
            'data_criacao': projeto.data_criacao.isoformat(),
            'data_atualizacao': projeto.data_atualizacao.isoformat(),
            'total_respondentes': projeto.total_respondentes,
            'progresso': projeto.progresso_geral()
        }
        
        # GARANTIR que o diretório existe
        os.makedirs(os.path.dirname(self.projetos_file), exist_ok=True)
        
        with open(self.projetos_file, 'w', encoding='utf-8') as f:
            json.dump(indice, f, indent=2, ensure_ascii=False)
    
    def _carregar_indice(self) -> Dict:
        """Carrega índice de projetos"""
        if os.path.exists(self.projetos_file):
            try:
                with open(self.projetos_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def listar_projetos(self) -> List[Dict]:
        """
        Lista todos os projetos (resumo)
        
        Returns:
            Lista de dicionários com resumo dos projetos
        """
        indice = self._carregar_indice()
        projetos = []
        
        for projeto_id, info in indice.items():
            projetos.append({
                'id': projeto_id,
                **info
            })
        
        # Ordenar por data de atualização (mais recentes primeiro)
        projetos.sort(key=lambda x: x['data_atualizacao'], reverse=True)
        return projetos
    
    def carregar_projeto(self, projeto_id: str) -> Optional[ProjetoCompliance]:
        """
        Carrega projeto completo do disco
        
        Args:
            projeto_id: ID do projeto
            
        Returns:
            ProjetoCompliance ou None se não encontrado
        """
        # Verificar cache primeiro
        if projeto_id in self._cache:
            return self._cache[projeto_id]
        
        projeto_path = self._get_projeto_path(projeto_id)
        
        if not os.path.exists(projeto_path):
            return None
        
        try:
            with open(projeto_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruir objeto ProjetoCompliance
            from models.projeto_compliance import FerramentaAplicada, StatusFerramenta
            
            projeto = ProjetoCompliance(
                id=data['id'],
                nome_empresa=data['nome_empresa'],
                cnpj=data.get('cnpj'),
                setor_atividade=data.get('setor_atividade', ''),
                num_funcionarios=data.get('num_funcionarios', 0),
                responsavel_tecnico=data.get('responsavel_tecnico', ''),
                data_criacao=datetime.fromisoformat(data['data_criacao']),
                data_atualizacao=datetime.fromisoformat(data['data_atualizacao']),
                status=StatusProjeto(data['status']),
                total_respondentes=data.get('total_respondentes', 0),
                riscos_identificados=data.get('riscos_identificados', 0),
                planos_acao_criados=data.get('planos_acao_criados', 0),
                inventario_pgr_gerado=data.get('inventario_pgr_gerado', False),
                aep_nr17_gerada=data.get('aep_nr17_gerada', False),
                relatorio_executivo_gerado=data.get('relatorio_executivo_gerado', False)
            )
            
            # Reconstruir ferramentas
            for nome, ferr_data in data.get('ferramentas', {}).items():
                ferramenta = FerramentaAplicada(
                    nome=ferr_data['nome'],
                    status=StatusFerramenta(ferr_data['status']),
                    data_inicio=datetime.fromisoformat(ferr_data['data_inicio']) if ferr_data.get('data_inicio') else None,
                    data_conclusao=datetime.fromisoformat(ferr_data['data_conclusao']) if ferr_data.get('data_conclusao') else None,
                    num_respondentes=ferr_data.get('num_respondentes', 0),
                    resultados_path=ferr_data.get('resultados_path')
                )
                projeto.ferramentas[nome] = ferramenta
            
            # Adicionar ao cache
            self._cache[projeto_id] = projeto
            
            return projeto
            
        except Exception as e:
            st.error(f"Erro ao carregar projeto {projeto_id}: {e}")
            return None
    
    def excluir_projeto(self, projeto_id: str) -> bool:
        """
        Exclui projeto
        
        Args:
            projeto_id: ID do projeto
            
        Returns:
            True se excluiu com sucesso
        """
        try:
            # Remover arquivo do projeto
            projeto_path = self._get_projeto_path(projeto_id)
            if os.path.exists(projeto_path):
                os.remove(projeto_path)
            
            # Remover do índice
            indice = self._carregar_indice()
            if projeto_id in indice:
                del indice[projeto_id]
                with open(self.projetos_file, 'w', encoding='utf-8') as f:
                    json.dump(indice, f, indent=2, ensure_ascii=False)
            
            # Remover do cache
            if projeto_id in self._cache:
                del self._cache[projeto_id]
            
            return True
        except Exception as e:
            st.error(f"Erro ao excluir projeto: {e}")
            return False
    
    def get_estatisticas_gerais(self) -> Dict:
        """
        Retorna estatísticas gerais de todos os projetos
        
        Returns:
            Dict com estatísticas
        """
        projetos = self.listar_projetos()
        
        if not projetos:
            return {
                'total_projetos': 0,
                'projetos_ativos': 0,
                'projetos_concluidos': 0,
                'total_empresas_avaliadas': 0,
                'total_respondentes': 0
            }
        
        return {
            'total_projetos': len(projetos),
            'projetos_ativos': sum(1 for p in projetos if p['status'] != StatusProjeto.CONCLUIDO.value),
            'projetos_concluidos': sum(1 for p in projetos if p['status'] == StatusProjeto.CONCLUIDO.value),
            'total_empresas_avaliadas': len(set(p['nome_empresa'] for p in projetos)),
            'total_respondentes': sum(p.get('total_respondentes', 0) for p in projetos)
        }

# Instância global do gerenciador
_manager_instance = None

def get_compliance_manager() -> ComplianceManager:
    """Retorna instância singleton do gerenciador"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ComplianceManager()
    return _manager_instance


