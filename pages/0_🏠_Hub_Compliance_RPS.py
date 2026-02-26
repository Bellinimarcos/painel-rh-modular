"""
Hub Central de Compliance RPS
Página principal para gerenciamento de projetos de avaliação de riscos psicossociais
"""

import streamlit as st
from datetime import datetime
from services.compliance_manager import get_compliance_manager, FERRAMENTAS_DISPONIVEIS
from logic.consolidador_resultados import ConsolidadorResultados
import pandas as pd

# ✅ Fallback: não quebrar se a pasta reports não existir
try:
    from reports.gerador_pgr_gro import GeradorPGR  # type: ignore
except ModuleNotFoundError:
    GeradorPGR = None  # type: ignore

st.set_page_config(
    page_title="Hub Compliance RPS",
    page_icon="🏠",
    layout="wide"
)

# Inicializar gerenciador
manager = get_compliance_manager()

# Título principal
st.title("🏠 Hub Central de Compliance RPS")
st.markdown("**Central de Gestão de Riscos Psicossociais e SST**")
st.caption("Gerenciamento integrado de projetos conforme NR-1 (GRO/PGR) e NR-17 (Ergonomia)")

# Estatísticas gerais no topo
st.divider()
col1, col2, col3, col4, col5 = st.columns(5)

stats = manager.get_estatisticas_gerais()

with col1:
    st.metric("📊 Total de Projetos", stats['total_projetos'])
with col2:
    st.metric("🚀 Projetos Ativos", stats['projetos_ativos'])
with col3:
    st.metric("✅ Concluídos", stats['projetos_concluidos'])
with col4:
    st.metric("🏢 Empresas Avaliadas", stats['total_empresas_avaliadas'])
with col5:
    st.metric("👥 Total Respondentes", stats['total_respondentes'])

st.divider()

# Aviso sutil se reports não está disponível (sem travar o app)
if GeradorPGR is None:
    st.warning("📌 Módulo de relatórios (PGR/GRO) não está disponível neste projeto. Geração de documentos ficará desativada temporariamente.")

# Tabs principais
tab1, tab2, tab3 = st.tabs([
    "📋 Projetos Ativos",
    "➕ Novo Projeto",
    "📚 Ferramentas Disponíveis"
])

# TAB 1: PROJETOS ATIVOS
with tab1:
    st.header("Projetos de Compliance")

    projetos = manager.listar_projetos()

    if not projetos:
        st.info("👋 Nenhum projeto criado ainda. Crie seu primeiro projeto na aba 'Novo Projeto'!")
    else:
        # Filtros
        col_filtro1, col_filtro2 = st.columns([3, 1])
        with col_filtro1:
            filtro_empresa = st.text_input("🔍 Buscar por empresa", "")
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
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.markdown(f"### 🏢 {projeto_info['nome_empresa']}")
                    st.caption(f"ID: {projeto_info['id']}")

                with col2:
                    status = projeto_info['status']
                    if status == "Concluído":
                        st.success(f"✅ {status}")
                    elif status == "Em Avaliação":
                        st.info(f"📝 {status}")
                    else:
                        st.warning(f"⏳ {status}")

                    progresso = projeto_info.get('progresso', 0)
                    st.progress(progresso / 100)
                    st.caption(f"{progresso:.0f}% completo")

                with col3:
                    st.metric("Respondentes", projeto_info.get('total_respondentes', 0))
                    data_atualizacao = datetime.fromisoformat(projeto_info['data_atualizacao'])
                    st.caption(f"Atualizado: {data_atualizacao.strftime('%d/%m/%Y')}")

                with col4:
                    if st.button("📂 Abrir", key=f"open_{projeto_info['id']}", use_container_width=True):
                        st.session_state.projeto_selecionado = projeto_info['id']
                        st.rerun()

                st.divider()

        # Se há projeto selecionado, mostrar detalhes
        if 'projeto_selecionado' in st.session_state:
            st.markdown("---")
            st.header("📊 Detalhes do Projeto")

            projeto = manager.carregar_projeto(st.session_state.projeto_selecionado)

            if projeto:
                # Informações do projeto
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader("Informações Básicas")
                    st.write(f"**Empresa:** {projeto.nome_empresa}")
                    st.write(f"**CNPJ:** {projeto.cnpj or 'N/A'}")
                    st.write(f"**Setor:** {projeto.setor_atividade or 'N/A'}")
                    st.write(f"**Funcionários:** {projeto.num_funcionarios}")

                with col2:
                    st.subheader("Status do Projeto")
                    st.write(f"**Status:** {projeto.status.value}")
                    st.write(f"**Criado em:** {projeto.data_criacao.strftime('%d/%m/%Y')}")
                    st.write(f"**Atualizado em:** {projeto.data_atualizacao.strftime('%d/%m/%Y')}")
                    st.write(f"**Responsável:** {projeto.responsavel_tecnico or 'N/A'}")

                with col3:
                    st.subheader("Métricas")
                    st.metric("Total Respondentes", projeto.total_respondentes)
                    st.metric("Riscos Identificados", projeto.riscos_identificados)
                    st.metric("Planos de Ação", projeto.planos_acao_criados)

                # Ferramentas aplicadas
                st.subheader("🛠️ Ferramentas Aplicadas")

                if projeto.ferramentas:
                    for nome, ferramenta in projeto.ferramentas.items():
                        with st.expander(f"{FERRAMENTAS_DISPONIVEIS.get(nome, {}).get('icone', '📋')} {nome} - {ferramenta.status.value}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Status:** {ferramenta.status.value}")
                                st.write(f"**Respondentes:** {ferramenta.num_respondentes}")
                            with col2:
                                if ferramenta.data_inicio:
                                    st.write(f"**Início:** {ferramenta.data_inicio.strftime('%d/%m/%Y')}")
                                if ferramenta.data_conclusao:
                                    st.write(f"**Conclusão:** {ferramenta.data_conclusao.strftime('%d/%m/%Y')}")

                            # Botão para ir à ferramenta
                            if nome == "COPSOQ III":
                                if st.button(f"Ir para {nome}", key=f"goto_{nome}"):
                                    st.switch_page("pages/7_🛡️_Riscos_Psicossociais.py")
                else:
                    st.info("Nenhuma ferramenta aplicada ainda. Configure as ferramentas para este projeto.")

                # Adicionar ferramenta ao projeto
                st.subheader("➕ Adicionar Ferramenta")
                col1, col2 = st.columns([3, 1])
                with col1:
                    nova_ferramenta = st.selectbox(
                        "Selecione uma ferramenta para adicionar",
                        [f for f in FERRAMENTAS_DISPONIVEIS.keys() if f not in projeto.ferramentas]
                    )
                with col2:
                    if st.button("Adicionar", use_container_width=True):
                        projeto.adicionar_ferramenta(nova_ferramenta)
                        manager.salvar_projeto(projeto)
                        st.success(f"✅ {nova_ferramenta} adicionada ao projeto!")
                        st.rerun()

                # Gerar documentação
                st.divider()
                st.subheader("📄 Documentação de Compliance")

                # ✅ Só habilita se tiver dados + módulo de relatórios disponível
                pode_documentar = projeto.pode_gerar_pgr()
                relatorios_disponiveis = (GeradorPGR is not None)

                if not relatorios_disponiveis:
                    st.info("🔒 Geração de documentos desativada porque o módulo `reports` não está presente neste projeto.")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(
                        "📋 Gerar Inventário PGR (NR-1)",
                        use_container_width=True,
                        disabled=(not pode_documentar) or (not relatorios_disponiveis)
                    ):
                        st.info("Funcionalidade em desenvolvimento - requer dados consolidados")

                with col2:
                    if st.button(
                        "📊 Gerar AEP (NR-17)",
                        use_container_width=True,
                        disabled=(not pode_documentar) or (not relatorios_disponiveis)
                    ):
                        st.info("Funcionalidade em desenvolvimento - requer dados consolidados")

                with col3:
                    if st.button(
                        "📈 Relatório Executivo",
                        use_container_width=True,
                        disabled=(not pode_documentar) or (not relatorios_disponiveis)
                    ):
                        st.info("Funcionalidade em desenvolvimento - requer dados consolidados")

                # Botões de ação
                st.divider()
                col1, col2, col3 = st.columns([1, 1, 4])

                with col1:
                    if st.button("🔙 Voltar", use_container_width=True):
                        del st.session_state.projeto_selecionado
                        st.rerun()

                with col2:
                    if st.button("🗑️ Excluir Projeto", use_container_width=True, type="secondary"):
                        if st.checkbox("Confirmar exclusão"):
                            if manager.excluir_projeto(projeto.id):
                                st.success("✅ Projeto excluído!")
                                del st.session_state.projeto_selecionado
                                st.rerun()

# TAB 2: NOVO PROJETO
with tab2:
    st.header("➕ Criar Novo Projeto de Compliance")

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

        submitted = st.form_submit_button("🚀 Criar Projeto", use_container_width=True)

        if submitted:
            if not nome_empresa:
                st.error("❌ Nome da empresa é obrigatório!")
            elif not ferramentas_selecionadas:
                st.warning("⚠️ Selecione pelo menos uma ferramenta!")
            else:
                # Criar projeto
                projeto = manager.criar_projeto(
                    nome_empresa=nome_empresa,
                    cnpj=cnpj,
                    setor=setor,
                    num_funcionarios=num_funcionarios,
                    responsavel=responsavel
                )

                # Adicionar ferramentas selecionadas
                for ferramenta in ferramentas_selecionadas:
                    projeto.adicionar_ferramenta(ferramenta)

                manager.salvar_projeto(projeto)

                st.success(f"✅ Projeto '{nome_empresa}' criado com sucesso!")
                st.balloons()
                st.info("📂 Vá para a aba 'Projetos Ativos' para gerenciar seu projeto.")

# TAB 3: FERRAMENTAS DISPONÍVEIS
with tab3:
    st.header("📚 Ferramentas Disponíveis no Sistema")

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
                        st.switch_page("pages/7_🛡️_Riscos_Psicossociais.py")
                else:
                    st.info("Em breve")

# Footer
st.divider()
st.caption("""
**Sistema de Gestão de Riscos Psicossociais**  
✓ Conforme NR-1 (Portaria MTE 1.419/2024) e NR-17  
✓ Metodologias cientificamente validadas  
✓ Gestão integrada de compliance SST
""")
