"""
Hub Central de Compliance RPS
Página principal para gerenciamento de projetos de avaliação de riscos psicossociais
"""
import os
import sys
from datetime import datetime

# --- Path setup ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd

from services.compliance_manager import get_compliance_manager, FERRAMENTAS_DISPONIVEIS
from logic.consolidador_resultados import ConsolidadorResultados
from services.storage import get_persistent_storage

#  Import do GeradorPGR opcional (não derruba a página no Cloud se não existir)
try:
    from reports.gerador_pgr_gro import GeradorPGR
    GERADOR_PGR_OK = True
except Exception:
    GeradorPGR = None
    GERADOR_PGR_OK = False


st.set_page_config(
    page_title="Hub Compliance RPS",
    page_icon="",
    layout="wide"
)

# Inicializar gerenciador e storage
manager = get_compliance_manager()
storage = get_persistent_storage()

# Carrega análises (para não parecer que sumiu)
try:
    analises = storage.get_analyses()
    total_analises = len(analises)
except Exception:
    total_analises = 0

# Título principal
st.title(" Hub Central de Compliance RPS")
st.markdown("**Central de Gestão de Riscos Psicossociais e SST**")
st.caption("Gerenciamento integrado de projetos conforme NR-1 (GRO/PGR) e NR-17 (Ergonomia)")

# Atalho para o Hub Analítico (main.py)
col_top_a, col_top_b = st.columns([1, 3])
with col_top_a:
    if st.button(" Abrir Hub Analítico", key="btn_open_analytics", width="stretch"):
        st.switch_page("main.py")
with col_top_b:
    if not GERADOR_PGR_OK:
        st.warning("️ Módulo de relatório (PGR/GRO) não está carregado neste ambiente. A página continua funcionando.")

# Estatísticas gerais no topo
st.divider()
col1, col2, col3, col4, col5, col6 = st.columns(6)

stats = manager.get_estatisticas_gerais()

with col1:
    st.metric(" Total de Projetos", stats.get('total_projetos', 0))
with col2:
    st.metric(" Projetos Ativos", stats.get('projetos_ativos', 0))
with col3:
    st.metric(" Concluídos", stats.get('projetos_concluidos', 0))
with col4:
    st.metric(" Empresas Avaliadas", stats.get('total_empresas_avaliadas', 0))
with col5:
    st.metric(" Total Respondentes", stats.get('total_respondentes', 0))
with col6:
    st.metric(" Total de Análises", total_analises)

st.divider()

# Tabs principais
tab1, tab2, tab3 = st.tabs([
    " Projetos Ativos",
    " Novo Projeto",
    " Ferramentas Disponíveis"
])

# TAB 1: PROJETOS ATIVOS
with tab1:
    st.header("Projetos de Compliance")

    projetos = manager.listar_projetos()

    if not projetos:
        st.info(" Nenhum projeto criado ainda. Crie seu primeiro projeto na aba 'Novo Projeto'!")
    else:
        # Filtros
        col_filtro1, col_filtro2 = st.columns([3, 1])
        with col_filtro1:
            filtro_empresa = st.text_input(" Buscar por empresa", "")
        with col_filtro2:
            filtro_status = st.selectbox("Status", ["Todos", "Criado", "Em Avaliação", "Em Análise", "Concluído"])

        # Filtrar projetos
        projetos_filtrados = projetos
        if filtro_empresa:
            projetos_filtrados = [p for p in projetos_filtrados if filtro_empresa.lower() in p['nome_empresa'].lower()]
        if filtro_status != "Todos":
            projetos_filtrados = [p for p in projetos_filtrados if p['status'] == filtro_status]

        st.caption(f"Exibindo {len(projetos_filtrados)} de {len(projetos)} projetos")

        # Exibir projetos como cards
        for projeto_info in projetos_filtrados:
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])

                with c1:
                    st.markdown(f"###  {projeto_info['nome_empresa']}")
                    st.caption(f"ID: {projeto_info['id']}")

                with c2:
                    status = projeto_info['status']
                    if status == "Concluído":
                        st.success(f" {status}")
                    elif status == "Em Avaliação":
                        st.info(f" {status}")
                    else:
                        st.warning(f"⏳ {status}")

                    progresso = projeto_info.get('progresso', 0)
                    st.progress(progresso / 100)
                    st.caption(f"{progresso:.0f}% completo")

                with c3:
                    st.metric("Respondentes", projeto_info.get('total_respondentes', 0))
                    data_atualizacao = datetime.fromisoformat(projeto_info['data_atualizacao'])
                    st.caption(f"Atualizado: {data_atualizacao.strftime('%d/%m/%Y')}")

                with c4:
                    if st.button(" Abrir", key=f"open_{projeto_info['id']}", width="stretch"):
                        st.session_state.projeto_selecionado = projeto_info['id']
                        st.rerun()

                st.divider()

        # Se há projeto selecionado, mostrar detalhes
        if 'projeto_selecionado' in st.session_state:
            st.markdown("---")
            st.header(" Detalhes do Projeto")

            projeto = manager.carregar_projeto(st.session_state.projeto_selecionado)

            if projeto:
                # Informações do projeto
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.subheader("Informações Básicas")
                    st.write(f"**Empresa:** {projeto.nome_empresa}")
                    st.write(f"**CNPJ:** {projeto.cnpj or 'N/A'}")
                    st.write(f"**Setor:** {projeto.setor_atividade or 'N/A'}")
                    st.write(f"**Funcionários:** {projeto.num_funcionarios}")

                with c2:
                    st.subheader("Status do Projeto")
                    st.write(f"**Status:** {projeto.status.value}")
                    st.write(f"**Criado em:** {projeto.data_criacao.strftime('%d/%m/%Y')}")
                    st.write(f"**Atualizado em:** {projeto.data_atualizacao.strftime('%d/%m/%Y')}")
                    st.write(f"**Responsável:** {projeto.responsavel_tecnico or 'N/A'}")

                with c3:
                    st.subheader("Métricas")
                    st.metric("Total Respondentes", projeto.total_respondentes)
                    st.metric("Riscos Identificados", projeto.riscos_identificados)
                    st.metric("Planos de Ação", projeto.planos_acao_criados)

                # Ferramentas aplicadas
                st.subheader("️ Ferramentas Aplicadas")

                if projeto.ferramentas:
                    for nome, ferramenta in projeto.ferramentas.items():
                        with st.expander(f"{FERRAMENTAS_DISPONIVEIS.get(nome, {}).get('icone', '')} {nome} - {ferramenta.status.value}"):
                            cc1, cc2 = st.columns(2)
                            with cc1:
                                st.write(f"**Status:** {ferramenta.status.value}")
                                st.write(f"**Respondentes:** {ferramenta.num_respondentes}")
                            with cc2:
                                if ferramenta.data_inicio:
                                    st.write(f"**Início:** {ferramenta.data_inicio.strftime('%d/%m/%Y')}")
                                if ferramenta.data_conclusao:
                                    st.write(f"**Conclusão:** {ferramenta.data_conclusao.strftime('%d/%m/%Y')}")

                            if nome == "COPSOQ III":
                                if st.button(f"Ir para {nome}", key=f"goto_{nome}"):
                                    st.switch_page("pages/1__COPSOQ_III.py")
                else:
                    st.info("Nenhuma ferramenta aplicada ainda. Configure as ferramentas para este projeto.")

                # Adicionar ferramenta ao projeto
                st.subheader(" Adicionar Ferramenta")
                c1, c2 = st.columns([3, 1])
                with c1:
                    nova_ferramenta = st.selectbox(
                        "Selecione uma ferramenta para adicionar",
                        [f for f in FERRAMENTAS_DISPONIVEIS.keys() if f not in projeto.ferramentas]
                    )
                with c2:
                    if st.button("Adicionar", key="btn_add_tool", width="stretch"):
                        projeto.adicionar_ferramenta(nova_ferramenta)
                        manager.salvar_projeto(projeto)
                        st.success(f" {nova_ferramenta} adicionada ao projeto!")
                        st.rerun()

                # Gerar documentação
                st.divider()
                st.subheader(" Documentação de Compliance")

                c1, c2, c3 = st.columns(3)

                with c1:
                    if st.button(" Gerar Inventário PGR (NR-1)", key="btn_pgr", width="stretch", disabled=not projeto.pode_gerar_pgr()):
                        if GERADOR_PGR_OK:
                            st.info("Gerador PGR disponível, mas integração total depende de dados consolidados.")
                        else:
                            st.warning("Gerador PGR não está disponível neste ambiente.")

                with c2:
                    if st.button(" Gerar AEP (NR-17)", key="btn_aep", width="stretch", disabled=not projeto.pode_gerar_pgr()):
                        st.info("Funcionalidade em desenvolvimento - requer dados consolidados")

                with c3:
                    if st.button(" Relatório Executivo", key="btn_exec", width="stretch", disabled=not projeto.pode_gerar_pgr()):
                        st.info("Funcionalidade em desenvolvimento - requer dados consolidados")

                # Botões de ação
                st.divider()
                c1, c2, c3 = st.columns([1, 1, 4])

                with c1:
                    if st.button(" Voltar", key="btn_back", width="stretch"):
                        del st.session_state.projeto_selecionado
                        st.rerun()

                with c2:
                    if st.button("️ Excluir Projeto", key="btn_delete", width="stretch", type="secondary"):
                        if st.checkbox("Confirmar exclusão", key="chk_delete"):
                            if manager.excluir_projeto(projeto.id):
                                st.success(" Projeto excluído!")
                                del st.session_state.projeto_selecionado
                                st.rerun()

# TAB 2: NOVO PROJETO
with tab2:
    st.header(" Criar Novo Projeto de Compliance")

    with st.form("form_novo_projeto"):
        st.subheader("Dados da Empresa")

        col1, col2 = st.columns(2)

        with col1:
            nome_empresa = st.text_input("Nome da Empresa *", placeholder="Ex: Empresa XYZ Ltda")
            cnpj = st.text_input("CNPJ", placeholder="00.000.000/0000-00")
            setor = st.text_input("Setor de Atividade", placeholder="Ex: Tecnologia, Saúde, Indústria")

        with col2:
            num_funcionarios = st.number_input("Número de Funcionários *", min_value=1, value=50)
            responsavel = st.text_input("Responsável Técnico", placeholder="Nome do responsável pela avaliação")

        st.subheader("Ferramentas a Aplicar")
        st.caption("Selecione as ferramentas que serão utilizadas neste projeto:")

        ferramentas_selecionadas = []
        cols = st.columns(3)

        for idx, (ferramenta, info) in enumerate(FERRAMENTAS_DISPONIVEIS.items()):
            with cols[idx % 3]:
                if st.checkbox(f"{info['icone']} {ferramenta}", key=f"ferr_{ferramenta}"):
                    ferramentas_selecionadas.append(ferramenta)
                    st.caption(info['descricao'])

        submitted = st.form_submit_button(" Criar Projeto", width="stretch")

        if submitted:
            if not nome_empresa:
                st.error(" Nome da empresa é obrigatório!")
            elif not ferramentas_selecionadas:
                st.warning("️ Selecione pelo menos uma ferramenta!")
            else:
                projeto = manager.criar_projeto(
                    nome_empresa=nome_empresa,
                    cnpj=cnpj,
                    setor=setor,
                    num_funcionarios=num_funcionarios,
                    responsavel=responsavel
                )

                for ferramenta in ferramentas_selecionadas:
                    projeto.adicionar_ferramenta(ferramenta)

                manager.salvar_projeto(projeto)

                st.success(f" Projeto '{nome_empresa}' criado com sucesso!")
                st.balloons()
                st.info(" Vá para a aba 'Projetos Ativos' para gerenciar seu projeto.")

# TAB 3: FERRAMENTAS DISPONÍVEIS
with tab3:
    st.header(" Ferramentas Disponíveis no Sistema")

    st.markdown("""
    O sistema integra as principais ferramentas validadas para avaliação de riscos 
    psicossociais e indicadores organizacionais:
    """)

    for ferramenta, info in FERRAMENTAS_DISPONIVEIS.items():
        with st.expander(f"{info['icone']} {ferramenta} - {info['nome_completo']}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Descrição:** {info['descricao']}")
                st.markdown(f"**Validação:** {info['validacao']}")
                st.markdown(f"**Normas Relacionadas:** {info['nr_relacionada']}")

            with col2:
                if ferramenta == "COPSOQ III":
                    if st.button(f"Acessar {ferramenta}", key=f"access_{ferramenta}"):
                        st.switch_page("pages/1__COPSOQ_III.py")
                else:
                    st.info("Em breve")

# Footer
st.divider()
st.caption("""
**Sistema de Gestão de Riscos Psicossociais**  
 Conforme NR-1 (Portaria MTE 1.419/2024) e NR-17  
 Metodologias cientificamente validadas  
 Gestão integrada de compliance SST
""")



