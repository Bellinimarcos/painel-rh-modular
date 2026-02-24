# pages/5_🔄_Turnover.py
# Responsabilidade: Interface para análise de rotatividade (turnover) e impacto financeiro.

import streamlit as st
import pandas as pd
import sys
import os
import time
import plotly.graph_objects as go

# --- Adiciona o diretório raiz ao Python Path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
# ------------------------------------------------

from components.ui_components import UIComponents
from components.ai_assistant import IntegratedAIAssistant, AutoInsightsComponent
from logic.turnover_processor import TurnoverProcessor
from models.enums import AnalysisType
from services.storage import get_persistent_storage
from services.api_client import APIClient
from config.settings import AppConfig

# Importa validadores
try:
    from utils.validators import DataValidator
except ImportError:
    st.error("⚠️ Módulo utils.validators não encontrado.")
    st.stop()

# --- Inicialização ---
ui = UIComponents()
processor = TurnoverProcessor()
storage = get_persistent_storage()
config = AppConfig()

api_client = APIClient()
ai_assistant = IntegratedAIAssistant(api_client)
ai_insights = AutoInsightsComponent(ai_assistant)

ANALYSIS_TYPE_FOR_THIS_PAGE = AnalysisType.TURNOVER


def render_results(analysis):
    """Renderiza os resultados da análise de turnover."""
    st.success(f"✅ Análise '{analysis.name}' concluída!")
    
    # Métricas principais
    taxa_anual = analysis.data['taxa_turnover_anual']
    benchmark = analysis.metadata['benchmark_setor']
    impacto = analysis.data['impacto_financeiro']
    custo_por_func = analysis.data['custo_por_funcionario']
    
    st.subheader("📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ui.render_metric_card(
            "Turnover Anualizado",
            f"{taxa_anual:.2f}%",
            icon="🔄",
            color=analysis.risk_level.color
        )
    
    with col2:
        delta = taxa_anual - benchmark
        st.metric(
            "Benchmark do Setor",
            f"{benchmark:.2f}%",
            delta=f"{delta:+.2f} p.p.",
            delta_color="inverse"
        )
    
    with col3:
        ui.render_metric_card(
            "Impacto Financeiro Total",
            f"R$ {impacto:,.2f}",
            icon="💰"
        )
    
    with col4:
        ui.render_metric_card(
            "Custo por Funcionário",
            f"R$ {custo_por_func:,.2f}",
            icon="👤"
        )
    
    # Insights da análise
    if analysis.insights:
        st.subheader("💡 Insights Automáticos")
        for insight in analysis.insights:
            if "crítica" in insight.lower() or "🚨" in insight:
                st.error(insight)
            elif "acima" in insight.lower() or "⚠️" in insight:
                st.warning(insight)
            else:
                st.info(insight)
    
    # Análise detalhada de custos
    st.subheader("💸 Detalhamento de Custos")
    
    custos_detalhados = analysis.data['custos_detalhados']
    
    # Cria gráfico de pizza de custos
    if any(custos_detalhados.values()):
        fig = go.Figure(data=[go.Pie(
            labels=list(custos_detalhados.keys()),
            values=list(custos_detalhados.values()),
            hole=0.4,
            marker_colors=['#EF4444', '#F59E0B', '#10B981']
        )])
        fig.update_layout(
            title="Distribuição de Custos",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de custos
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Custos Detalhados:**")
            for categoria, valor in custos_detalhados.items():
                percentual = (valor / impacto * 100) if impacto > 0 else 0
                st.metric(categoria, f"R$ {valor:,.2f}", delta=f"{percentual:.1f}%")
        
        with col2:
            st.markdown("**Informações do Período:**")
            st.metric("Admissões", analysis.metadata['admissoes'])
            st.metric("Demissões", analysis.metadata['demissoes'])
            st.metric("Substituições", analysis.data['substituicoes'])
            st.metric("Média de Funcionários", f"{analysis.metadata['media_funcionarios']:.0f}")
    else:
        st.info("Nenhum custo registrado para este período")
    
    # Comparação com benchmark
    st.subheader("📈 Comparação com o Mercado")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Sua Empresa',
        x=['Turnover'],
        y=[taxa_anual],
        marker_color=analysis.risk_level.color
    ))
    fig.add_trace(go.Bar(
        name=f'Benchmark {analysis.metadata["setor"]}',
        x=['Turnover'],
        y=[benchmark],
        marker_color='#3B82F6'
    ))
    fig.update_layout(
        title="Taxa de Turnover: Empresa vs Setor",
        yaxis_title="Taxa Anual (%)",
        barmode='group',
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Projeção de tendência
    st.subheader("📈 Projeção de Tendência")
    st.caption("Projeções baseadas na taxa atual observada no período analisado")
    
    taxa_mensal = taxa_anual / 12
    
    col_proj1, col_proj2, col_proj3 = st.columns(3)
    with col_proj1:
        st.metric(
            "Taxa Mensal Média",
            f"{taxa_mensal:.2f}%",
            help="Taxa média mensal de turnover"
        )
    with col_proj2:
        st.metric(
            "Projeção Semestral",
            f"{taxa_mensal * 6:.2f}%",
            help="Projeção para os próximos 6 meses"
        )
    with col_proj3:
        benchmark_semestral = benchmark / 2
        delta_semestral = (taxa_mensal * 6) - benchmark_semestral
        st.metric(
            "Benchmark Semestral",
            f"{benchmark_semestral:.2f}%",
            delta=f"{delta_semestral:+.2f} p.p.",
            delta_color="inverse",
            help="Metade do benchmark anual para comparação"
        )
    
    st.divider()
    
    # Componente de IA
    ai_insights.render(analysis)


# --- Interface Principal ---
ui.render_header("🔄 Análise de Turnover", "Rotatividade de pessoal e impacto financeiro")

st.info("""
**O que é Turnover?**

Taxa de rotatividade de colaboradores, calculada pela média entre admissões e demissões 
dividida pelo número médio de funcionários. Quanto maior, maior a instabilidade da força de trabalho.
""")

# Seleção do modo de entrada
modo_entrada = st.radio(
    "Selecione o modo de entrada de dados:",
    ["📝 Entrada Manual", "📂 Importar Arquivo"],
    horizontal=True
)

st.divider()

# Modo de importação de arquivo
if modo_entrada == "📂 Importar Arquivo":
    st.subheader("📂 Importação de Dados de Movimentação")
    
    st.info("""
    **Formato esperado:**
    - Importe 2 arquivos separados: um com admissões e outro com demissões
    - Cada arquivo deve ter colunas: `NOME`, `MATRICULA` (ou similar)
    - O sistema conta automaticamente o número de registros em cada arquivo
    """)
    
    col_up1, col_up2 = st.columns(2)
    
    with col_up1:
        st.markdown("**📥 Arquivo de Admissões**")
        uploaded_admissoes = st.file_uploader(
            "Lista de colaboradores admitidos",
            type=['csv', 'xlsx', 'xls', 'txt'],
            key="turnover_admissoes"
        )
    
    with col_up2:
        st.markdown("**📤 Arquivo de Demissões**")
        uploaded_demissoes = st.file_uploader(
            "Lista de colaboradores demitidos",
            type=['csv', 'xlsx', 'xls', 'txt'],
            key="turnover_demissoes"
        )
    
    if uploaded_admissoes or uploaded_demissoes:
        try:
            from utils.file_validators import FileValidator
            
            admissoes_count = 0
            demissoes_count = 0
            
            # Processa arquivo de admissões
            if uploaded_admissoes:
                with st.spinner("A ler arquivo de admissões..."):
                    df_adm, warnings_adm, errors_adm = FileValidator.read_file_robust(uploaded_admissoes)
                
                if df_adm is not None and not df_adm.empty:
                    df_adm = df_adm.dropna(how='all')
                    admissoes_count = len(df_adm)
                    st.success(f"✅ {admissoes_count} admissões detectadas em '{uploaded_admissoes.name}'")
                    
                    with st.expander("👁️ Preview Admissões"):
                        st.dataframe(df_adm.head(10), use_container_width=True)
            
            # Processa arquivo de demissões
            if uploaded_demissoes:
                with st.spinner("A ler arquivo de demissões..."):
                    df_dem, warnings_dem, errors_dem = FileValidator.read_file_robust(uploaded_demissoes)
                
                if df_dem is not None and not df_dem.empty:
                    df_dem = df_dem.dropna(how='all')
                    demissoes_count = len(df_dem)
                    st.success(f"✅ {demissoes_count} demissões detectadas em '{uploaded_demissoes.name}'")
                    
                    with st.expander("👁️ Preview Demissões"):
                        st.dataframe(df_dem.head(10), use_container_width=True)
            
            # Se pelo menos um arquivo foi carregado
            if admissoes_count > 0 or demissoes_count > 0:
                st.divider()
                st.subheader("Confirme os dados detectados:")
                
                with st.form(key="turnover_form_import"):
                    col1, col2 = st.columns(2)
                    with col1:
                        admissoes = st.number_input(
                            "Admissões detectadas", 
                            value=admissoes_count, 
                            min_value=0,
                            help="Ajuste se necessário"
                        )
                    with col2:
                        demissoes = st.number_input(
                            "Demissões detectadas", 
                            value=demissoes_count, 
                            min_value=0,
                            help="Ajuste se necessário"
                        )
                    
                    func_inicio = st.number_input(
                        "Funcionários no Início do Período", 
                        min_value=1, 
                        value=100
                    )
                    periodo_meses = st.selectbox("Duração (meses)", [1, 3, 6, 12, 24], index=3)
                    
                    func_fim = st.number_input(
                        "Funcionários no Fim", 
                        value=func_inicio + admissoes - demissoes, 
                        min_value=0
                    )
                    
                    setor = st.selectbox("Setor", list(config.BENCHMARK_TURNOVER.keys()))
                    
                    st.markdown("**Custos Unitários (R$):**")
                    col8, col9, col10 = st.columns(3)
                    with col8:
                        custo_demissao = st.number_input("Custo Demissão (R$)", value=2500, min_value=0)
                    with col9:
                        custo_contratacao = st.number_input("Custo Contratação (R$)", value=1800, min_value=0)
                    with col10:
                        custo_produtividade = st.number_input("Perda Produtividade (R$)", value=3200, min_value=0)
                    
                    nome_analise = st.text_input(
                        "Nome da Análise", 
                        f"Turnover - Importação - {periodo_meses} meses"
                    )
                    
                    submitted = st.form_submit_button("🚀 Executar Análise", type="primary")
                    
                    if submitted:
                        # VALIDAÇÕES
                        validations = [
                            DataValidator.validate_employee_count(func_inicio, field_name="Funcionários no início"),
                            DataValidator.validate_employee_count(admissoes, min_val=0, field_name="Admissões"),
                            DataValidator.validate_employee_count(demissoes, min_val=0, field_name="Demissões"),
                            DataValidator.validate_currency(custo_demissao, field_name="Custo demissão"),
                            DataValidator.validate_currency(custo_contratacao, field_name="Custo contratação"),
                            DataValidator.validate_currency(custo_produtividade, field_name="Custo produtividade")
                        ]
                        
                        all_valid, validation_errors = DataValidator.validate_all(validations)
                        
                        if not all_valid:
                            st.error("❌ Erros de validação:")
                            for error in validation_errors:
                                st.error(f"  • {error}")
                        else:
                            with st.spinner("A processar..."):
                                try:
                                    custos = {
                                        'demissao': custo_demissao, 
                                        'contratacao': custo_contratacao, 
                                        'produtividade': custo_produtividade
                                    }
                                    analysis_result = processor.process(
                                        nome_analise, func_inicio, func_fim, 
                                        admissoes, demissoes, periodo_meses, setor, custos
                                    )
                                    st.session_state.latest_analysis = analysis_result
                                    st.session_state.analysis_ready = True
                                    
                                    try:
                                        storage.save_analysis(analysis_result)
                                        st.success("✅ Análise salva automaticamente!")
                                    except Exception as e:
                                        st.warning(f"Análise calculada, mas não foi possível salvar: {e}")
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                                    st.exception(e)
        
        except Exception as e:
            st.error(f"Erro ao processar arquivos: {e}")
    
    if not uploaded_admissoes and not uploaded_demissoes:
        st.warning("📤 Faça upload de pelo menos um arquivo para começar")
        st.stop()

# Modo manual (original)
else:
    with st.form(key="turnover_form"):
        st.subheader("1️⃣ Dados do Período")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            func_inicio = st.number_input(
                "Funcionários no Início",
                min_value=1,
                value=100,
                help="Total de colaboradores no primeiro dia do período"
            )
        
        with col2:
            admissoes = st.number_input(
                "Admissões no Período",
                min_value=0,
                value=5,
                help="Total de contratações realizadas"
            )
        
        with col3:
            demissoes = st.number_input(
                "Demissões no Período",
                min_value=0,
                value=3,
                help="Total de desligamentos ocorridos"
            )
        
        func_fim_calculado = func_inicio + admissoes - demissoes
        
        col4, col5 = st.columns(2)
        
        with col4:
            func_fim = st.number_input(
                "Funcionários no Fim",
                min_value=0,
                value=func_fim_calculado,
                help="Total de colaboradores no último dia do período"
            )
        
        with col5:
            periodo_meses = st.selectbox(
                "Duração do Período (meses)",
                [1, 3, 6, 12, 24],
                index=3,
                help="Período analisado em meses"
            )
        
        if func_fim != func_fim_calculado:
            diff = abs(func_fim - func_fim_calculado)
            st.warning(
                f"⚠️ Atenção: O número de funcionários no fim ({func_fim}) difere do esperado "
                f"({func_fim_calculado}) por {diff} colaboradores. "
                f"Verifique se há transferências ou outros movimentos não contabilizados."
            )
        
        st.divider()
        
        st.subheader("2️⃣ Configurações e Custos")
        
        col6, col7 = st.columns(2)
        
        with col6:
            setor = st.selectbox(
                "Setor da Empresa",
                list(config.BENCHMARK_TURNOVER.keys()),
                help="Usado para comparação com benchmarks do mercado"
            )
        
        with col7:
            periodo_descricao = st.text_input(
                "Descrição do Período",
                value=f"Últimos {periodo_meses} mês(es)",
                help="Ex: 'Q1 2025', '1º Semestre 2025'"
            )
        
        st.markdown("**Custos Unitários (R$):**")
        st.caption("Valores médios estimados por colaborador. Ajuste conforme sua realidade.")
        
        col8, col9, col10 = st.columns(3)
        
        with col8:
            custo_demissao = st.number_input(
                "Custo de Demissão",
                min_value=0,
                value=2500,
                step=500,
                help="Aviso prévio, rescisão, férias proporcionais, etc."
            )
        
        with col9:
            custo_contratacao = st.number_input(
                "Custo de Contratação",
                min_value=0,
                value=1800,
                step=500,
                help="Recrutamento, seleção, exames, treinamento inicial"
            )
        
        with col10:
            custo_produtividade = st.number_input(
                "Perda de Produtividade",
                min_value=0,
                value=3200,
                step=500,
                help="Curva de aprendizado, período de adaptação"
            )
        
        nome_analise = st.text_input(
            "Nome da Análise",
            f"Turnover - {setor} - {periodo_descricao}"
        )
        
        submitted = st.form_submit_button("🚀 Executar Análise", type="primary", use_container_width=True)
        
        if submitted:
            # VALIDAÇÕES ROBUSTAS
            validations = [
                DataValidator.validate_employee_count(func_inicio, field_name="Funcionários no início"),
                DataValidator.validate_employee_count(admissoes, min_val=0, field_name="Admissões"),
                DataValidator.validate_employee_count(demissoes, min_val=0, field_name="Demissões"),
                DataValidator.validate_currency(custo_demissao, field_name="Custo demissão"),
                DataValidator.validate_currency(custo_contratacao, field_name="Custo contratação"),
                DataValidator.validate_currency(custo_produtividade, field_name="Custo produtividade")
            ]
            
            if func_fim < 0:
                validations.append((False, f"Funcionários no fim não pode ser negativo: {func_fim}"))
            else:
                validations.append((True, ""))
            
            all_valid, validation_errors = DataValidator.validate_all(validations)
            
            if not all_valid:
                st.error("❌ Erros de validação encontrados:")
                for error in validation_errors:
                    st.error(f"  • {error}")
            else:
                with st.spinner("A processar análise de turnover..."):
                    try:
                        custos = {
                            'demissao': custo_demissao,
                            'contratacao': custo_contratacao,
                            'produtividade': custo_produtividade
                        }
                        
                        analysis_result = processor.process(
                            name=nome_analise,
                            func_inicio=func_inicio,
                            func_fim=func_fim,
                            admissoes=admissoes,
                            demissoes=demissoes,
                            periodo_meses=periodo_meses,
                            setor=setor,
                            custos=custos
                        )
                        
                        st.session_state.latest_analysis = analysis_result
                        st.session_state.analysis_ready = True
                        
                        try:
                            storage.save_analysis(analysis_result)
                            st.success("✅ Análise salva automaticamente!")
                        except Exception as e:
                            st.warning(f"Análise calculada, mas não foi possível salvar: {e}")
                    
                    except ValueError as e:
                        st.error(f"❌ Erro de validação: {e}")
                    except Exception as e:
                        st.error(f"❌ Erro inesperado: {e}")
                        st.exception(e)

# --- Renderização de Resultados ---
if 'latest_analysis' in st.session_state and st.session_state.latest_analysis is not None:
    if st.session_state.latest_analysis.type == ANALYSIS_TYPE_FOR_THIS_PAGE:
        if st.session_state.get('analysis_ready', False):
            st.divider()
            render_results(st.session_state.latest_analysis)