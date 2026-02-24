# -*- coding: utf-8 -*-
# pages/4_📊_Absenteísmo.py
# Responsabilidade: Interface para análise de absentismo com Fator de Bradford.

import streamlit as st
import sys
import os
from datetime import date, datetime
import calendar

# Adiciona diretório raiz ao path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from components.ui_components import UIComponents
from components.ai_assistant import IntegratedAIAssistant, AutoInsightsComponent
from logic.absenteeism_processor import AbsenteeismProcessor
from models.enums import AnalysisType
from services.storage import get_persistent_storage
from services.api_client import APIClient

try:
    from utils.file_validators import FileValidator, ColumnMapper
    from utils.validators import DataValidator
except ImportError:
    st.error("⚠️ Módulo utils.file_validators não encontrado.")
    st.stop()

# Inicialização
ui = UIComponents()
processor = AbsenteeismProcessor()
storage = get_persistent_storage()

api_client = APIClient()
ai_assistant = IntegratedAIAssistant(api_client)
ai_insights = AutoInsightsComponent(ai_assistant)

ANALYSIS_TYPE_FOR_THIS_PAGE = AnalysisType.ABSENTEEISM

# BENCHMARK DE ABSENTISMO
BENCHMARK_ABSENTISMO = {
    'Indústria': 4.5,
    'Comércio': 3.8,
    'Serviços': 3.2,
    'Saúde': 5.5,
    'Educação': 4.0,
    'TI': 2.5,
    'Outros': 3.5
}


def render_results(analysis):
    """Renderiza os resultados da análise."""
    st.success(f"✅ Análise '{analysis.name}' concluída!")
    
    # Métricas principais
    taxa = analysis.data['taxa_absentismo']
    benchmark = analysis.metadata['benchmark_setor']
    total_dias = analysis.data['total_dias_ausencia']
    bradford_medio = analysis.data['fator_bradford_medio']
    
    st.subheader("📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ui.render_metric_card(
            "Taxa de Absentismo",
            f"{taxa:.2f}%",
            icon="📉",
            color=analysis.risk_level.color
        )
    
    with col2:
        delta = taxa - benchmark
        st.metric(
            "Benchmark do Setor",
            f"{benchmark:.2f}%",
            delta=f"{delta:+.2f} p.p.",
            delta_color="inverse"
        )
    
    with col3:
        ui.render_metric_card(
            "Total Dias Ausência",
            f"{total_dias:.0f}",
            icon="🗓️"
        )
    
    with col4:
        ui.render_metric_card(
            "Bradford Médio",
            f"{bradford_medio:.1f}",
            icon="⚡"
        )
    
    # Insights
    if analysis.insights:
        st.subheader("💡 Insights Automáticos")
        for insight in analysis.insights:
            if "crítico" in insight.lower():
                st.error(insight)
            elif "atenção" in insight.lower():
                st.warning(insight)
            else:
                st.info(insight)
    
    st.divider()
    ai_insights.render(analysis)
    
    # Botão de Exportação
    st.divider()
    st.subheader("📥 Exportar Análise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Exportar para Excel", use_container_width=True):
            try:
                import pandas as pd
                from datetime import datetime
                
                # Cria DataFrame com resultados
                df_export = pd.DataFrame({
                    'Métrica': ['Taxa de Absentismo (%)', 'Benchmark Setor (%)', 'Total Dias Ausência', 'Bradford Médio'],
                    'Valor': [taxa, benchmark, total_dias, bradford_medio]
                })
                
                # Nome do arquivo
                filename = f"reports/Absentismo_{analysis.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                # Salva
                df_export.to_excel(filename, index=False)
                st.success(f"✅ Relatório exportado: {filename}")
                
            except Exception as e:
                st.error(f"❌ Erro ao exportar: {e}")
    
    with col2:
        if st.button("💾 Baixar Dados Completos (CSV)", use_container_width=True):
            try:
                import pandas as pd
                from datetime import datetime
                
                # DataFrame Bradford
                df_bradford = analysis.data['df_bradford']
                
                # Nome do arquivo
                filename = f"reports/Absentismo_Detalhado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                # Salva
                df_bradford.to_csv(filename, index=False, encoding='utf-8-sig')
                st.success(f"✅ Dados exportados: {filename}")
                
            except Exception as e:
                st.error(f"❌ Erro ao exportar: {e}")


# Interface Principal
ui.render_header("📊 Análise de Absentismo", "Cálculo da taxa de absentismo e Fator de Bradford")

uploaded_file = st.file_uploader(
    "📂 Selecione o arquivo de ausências",
    type=['csv', 'xlsx', 'xls', 'txt'],
    key="absenteeism_uploader",
    help="Arquivo deve conter: ID do colaborador, data início, data fim"
)

if uploaded_file:
    with st.spinner("📖 Lendo arquivo..."):
        df, warnings, errors = FileValidator.read_file_robust(uploaded_file)
    
    for warning in warnings:
        st.warning(warning)
    for error in errors:
        st.error(error)
    
    if df is not None:
        st.success(f"✅ Arquivo lido com sucesso!")
        
        with st.expander("👁️ Pré-visualização"):
            st.dataframe(df.head(10), use_container_width=True)
        
        st.divider()
        st.subheader("1️⃣ Mapeamento de Colunas")
        
        suggestions = ColumnMapper.suggest_mappings(df)
        cols = df.columns.tolist()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            map_id = st.selectbox(
                "ID do Colaborador *",
                cols,
                index=cols.index(suggestions.get('id_colaborador', cols[0])) if suggestions.get('id_colaborador') in cols else 0
            )
        
        with col2:
            map_start = st.selectbox(
                "Data de Início *",
                cols,
                index=cols.index(suggestions.get('data_inicio', cols[1])) if len(cols) > 1 and suggestions.get('data_inicio') in cols else (1 if len(cols) > 1 else 0)
            )
        
        with col3:
            map_end = st.selectbox(
                "Data de Fim *",
                cols,
                index=cols.index(suggestions.get('data_fim', cols[2])) if len(cols) > 2 and suggestions.get('data_fim') in cols else (2 if len(cols) > 2 else 0)
            )
        
        column_mapping = {
            map_id: 'id_colaborador',
            map_start: 'data_inicio',
            map_end: 'data_fim'
        }
        
        st.divider()
        st.subheader("2️⃣ Parâmetros de Análise")
        
        period_option = st.selectbox("Selecione o Período", ["Mês Específico", "Período Personalizado"])
        
        if period_option == "Mês Específico":
            col1, col2 = st.columns(2)
            current_year = datetime.now().year
            years = list(range(current_year - 5, current_year + 2))
            
            with col1:
                selected_year = st.selectbox("Ano", years, index=len(years) - 2)
            
            with col2:
                month_names = {i: calendar.month_name[i] for i in range(1, 13)}
                selected_month_name = st.selectbox(
                    "Mês",
                    list(month_names.values()),
                    index=datetime.now().month - 1
                )
                selected_month_num = list(month_names.keys())[list(month_names.values()).index(selected_month_name)]
            
            start_date = date(selected_year, selected_month_num, 1)
            end_date = date(selected_year, selected_month_num, calendar.monthrange(selected_year, selected_month_num)[1])
        else:
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Início do Período", date.today().replace(day=1))
            with col2:
                end_date = st.date_input("Fim do Período", date.today())
        
        col3, col4 = st.columns(2)
        
        with col3:
            total_emp = st.number_input(
                "Total de Colaboradores",
                min_value=1,
                value=100
            )
        
        with col4:
            setor = st.selectbox(
                "Setor da Empresa",
                list(BENCHMARK_ABSENTISMO.keys())
            )
        
        nome_analise = st.text_input(
            "Nome da Análise",
            f"Absentismo - {start_date.strftime('%b %Y')}"
        )
        
        st.divider()
        
        if st.button("🚀 Executar Análise", type="primary", use_container_width=True):
            validations = [
                DataValidator.validate_date_range(start_date, end_date, max_days=730),
                DataValidator.validate_employee_count(total_emp, min_val=1, max_val=100000)
            ]
            
            all_valid, validation_errors = DataValidator.validate_all(validations)
            
            if not all_valid:
                st.error("❌ Erros de validação:")
                for error in validation_errors:
                    st.error(f"  • {error}")
            else:
                with st.spinner("⚙️ Processando..."):
                    try:
                        analysis_result = processor.process(
                            df=df,
                            name=nome_analise,
                            period_start=start_date,
                            period_end=end_date,
                            total_employees=total_emp,
                            setor=setor,
                            column_mapping=column_mapping
                        )
                        
                        st.session_state.latest_analysis = analysis_result
                        st.session_state.analysis_ready = True
                        
                        try:
                            storage.save_analysis(analysis_result)
                            st.success("✅ Análise salva!")
                        except Exception as e:
                            st.warning(f"Análise calculada, mas não salva: {e}")
                    
                    except ValueError as e:
                        st.error(f"❌ Erro: {e}")
                    except Exception as e:
                        st.error(f"❌ Erro inesperado: {e}")
                        st.exception(e)

# Renderização de Resultados
if 'latest_analysis' in st.session_state and st.session_state.latest_analysis is not None:
    if st.session_state.latest_analysis.type == ANALYSIS_TYPE_FOR_THIS_PAGE:
        if st.session_state.get('analysis_ready', False):
            st.divider()
            render_results(st.session_state.latest_analysis)