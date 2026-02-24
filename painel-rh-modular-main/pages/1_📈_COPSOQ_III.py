# pages/1__COPSOQ_III.py
"""
Responsabilidade: Interface para análise COPSOQ III - Questionário psicossocial.
Suporta arquivos com respostas individuais (Resp_Q) ou scores já calculados.
"""
import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import time
import numpy as np
import hashlib
from datetime import datetime

# --- Path setup ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from components.ui_components import UIComponents
from components.ai_assistant import IntegratedAIAssistant, AutoInsightsComponent
from logic.copsoq_processor import COPSOQProcessor
from models.enums import AnalysisType
from services.storage import get_persistent_storage
from services.api_client import APIClient

# Importa validadores
try:
    from utils.file_validators import FileValidator
    from utils.validators import DataValidator
except ImportError:
    st.error("️ Módulo utils não encontrado.")
    st.stop()

# --- Inicialização ---
ui = UIComponents()
processor = COPSOQProcessor(version="III")
storage = get_persistent_storage()

api_client = APIClient()
ai_assistant = IntegratedAIAssistant(api_client)
ai_insights = AutoInsightsComponent(ai_assistant)

ANALYSIS_TYPE_FOR_THIS_PAGE = AnalysisType.COPSOQ_III

# =========================
# Regras COPSOQ (importante)
# =========================
# Dimensões "negativas": maior score = pior (mais risco).
NEGATIVE_DIMS = {
    "Burnout",
    "Stress",
    "Problemas de Sono",
    "Sintomas Depressivos",
    "Exigências Quantitativas",
    "Exigências Emocionais",
    "Conflitos de Papéis Laborais",
    "Conflito Trabalho-Família",
    "Assédio",
    "Violência",
}

def _normalize_dim_name(s: str) -> str:
    """Normaliza nome para comparação (reduz problemas com espaços)."""
    return str(s).strip()

def is_negative_dimension(dim_name: str) -> bool:
    return _normalize_dim_name(dim_name) in NEGATIVE_DIMS

def health_score(dim_name: str, score: float) -> float:
    """Converte score para uma métrica 'saudável' onde maior = melhor para qualquer dimensão."""
    if is_negative_dimension(dim_name):
        return 100.0 - float(score)
    return float(score)


def detect_file_format(df):
    """Detecta se arquivo tem respostas individuais (Resp_Q/P) ou scores calculados"""
    resp_cols = [
        col for col in df.columns
        if 'Resp_Q' in str(col) or (str(col).startswith('P') and str(col)[1:].isdigit())
    ]

    # Procura TODAS as colunas numéricas que não sejam respostas ou identificadores
    exclude_keywords = ['resp_q', 'timestamp', 'unnamed', 'index', 'id']
    numeric_cols = []

    for col in df.columns:
        col_lower = str(col).lower()
        # Se for numérica E não for coluna de resposta/identificador
        if (df[col].dtype in ['float64', 'int64', 'float32', 'int32'] and
            not any(keyword in col_lower for keyword in exclude_keywords)):
            numeric_cols.append(col)

    # Se tem muitas colunas numéricas (dimensões), usa elas
    if len(numeric_cols) >= 5:
        return "calculated_scores", numeric_cols
    # Se tem muitas colunas Resp_Q/P, são respostas brutas
    elif len(resp_cols) >= 20:
        return "raw_responses", resp_cols
    else:
        return "unknown", []


def extract_scores_from_df(df, dimension_columns):
    """Extrai scores médios das colunas de dimensões já calculadas"""
    scores = {}

    for col in dimension_columns:
        # Pega valores numéricos e calcula média
        values = pd.to_numeric(df[col], errors='coerce').dropna()
        if not values.empty:
            # Se valores estão em 0-100, usa direto
            # Se estão em 0-5, multiplica por 25
            max_val = values.max()
            if max_val <= 5:
                mean_score = values.mean() * 25
            elif max_val <= 100:
                mean_score = values.mean()
            else:
                mean_score = values.mean()

            scores[col] = float(mean_score)

    return scores


def render_results(analysis):
    """Renderiza os resultados da análise COPSOQ"""
    st.success(f" Análise '{analysis.name}' concluída!")

    # Métricas gerais
    st.subheader(" Resumo Geral")

    scores = analysis.data  # dict {Dimensão: Score}
    avg_score = sum(scores.values()) / len(scores) if scores else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        ui.render_metric_card(
            "Score Médio",
            f"{avg_score:.1f}/100",
            icon="",
            color=analysis.risk_level.color if hasattr(analysis.risk_level, 'color') else "#3B82F6"
        )

    #  Contagens corrigidas considerando dimensões negativas/positivas
    high_risk = 0
    low_risk = 0
    for dim, s in scores.items():
        s = float(s)
        if is_negative_dimension(dim):
            # negativo: alto = pior
            if s > 70:
                high_risk += 1
            elif s < 40:
                low_risk += 1
        else:
            # positivo: baixo = pior
            if s < 40:
                high_risk += 1
            elif s > 70:
                low_risk += 1

    with col2:
        st.metric("Dimensões de Alto Risco", high_risk)

    with col3:
        st.metric("Dimensões Saudáveis", low_risk)

    # Insights automáticos
    if analysis.insights:
        st.subheader(" Insights Automáticos")
        for insight in analysis.insights:
            if "crítico" in insight.lower():
                st.error(insight)
            elif "atenção" in insight.lower():
                st.warning(insight)
            else:
                st.info(insight)

    # Gráfico principal
    st.subheader(" Scores por Dimensão")

    df_scores = pd.DataFrame({
        'Dimensão': list(scores.keys()),
        'Score': list(scores.values())
    }).sort_values('Score', ascending=True)

    fig = px.bar(
        df_scores,
        y='Dimensão',
        x='Score',
        orientation='h',
        title='Scores COPSOQ III (0-100)',
        color='Score',
        color_continuous_scale='RdYlGn',
        text='Score'
    )
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(
        height=max(500, len(df_scores) * 25),
        showlegend=False,
        xaxis_title="Score (0-100)",
        yaxis_title=""
    )
    st.plotly_chart(fig, width='stretch')

    # Detalhes por categoria
    with st.expander(" Detalhes Completos"):
        st.dataframe(
            df_scores.sort_values('Score', ascending=False),
            width='stretch',
            hide_index=True
        )

    #  Top 5 corrigido (usa HealthScore)
    st.divider()
    colA, colB = st.columns(2)

    df_rank = df_scores.copy()
    df_rank["HealthScore"] = df_rank.apply(lambda r: health_score(r["Dimensão"], r["Score"]), axis=1)

    top5 = df_rank.sort_values("HealthScore", ascending=False).head(5)
    bottom5 = df_rank.sort_values("HealthScore", ascending=True).head(5)

    with colA:
        st.markdown("** Top 5 Dimensões Mais Saudáveis**")
        for _, row in top5.iterrows():
            st.metric(row["Dimensão"], f"{row['Score']:.1f}")

    with colB:
        st.markdown("** Top 5 Dimensões Mais Críticas**")
        for _, row in bottom5.iterrows():
            st.metric(row["Dimensão"], f"{row['Score']:.1f}")

    st.divider()

    # Componente de IA
    ai_insights.render(analysis)


# --- Interface Principal ---
ui.render_header(
    " COPSOQ III",
    "Copenhagen Psychosocial Questionnaire - Versão III"
)

st.info("""
**Sobre o COPSOQ III:**

O COPSOQ é um questionário internacional para avaliação de riscos psicossociais no trabalho.

**Formatos aceitos:**
1. **Arquivo com scores calculados** (recomendado): Colunas com nomes das dimensões e valores já processados
2. **Arquivo com respostas brutas**: Colunas Resp_Q1, Resp_Q2... ou P1, P2, P3...
""")

st.divider()

# Upload do arquivo
uploaded_file = st.file_uploader(
    " Selecione o arquivo de respostas COPSOQ III",
    type=['csv', 'xlsx', 'xls'],
    key="copsoq_uploader",
    help="Arquivo com respostas ao questionário COPSOQ III"
)

# Inicializa variáveis para evitar "referenced before assignment"
df = None
warnings = []
errors = []
file_format = "unknown"
relevant_cols = []
nome_analise = None

if uploaded_file:
    with st.spinner("A ler o arquivo..."):
        df, warnings, errors = FileValidator.read_file_robust(uploaded_file)

    # Mostra avisos e erros de leitura
    for warning in warnings:
        st.warning(warning)

    for error in errors:
        st.error(error)

    if df is not None:
        st.success(f" Arquivo '{uploaded_file.name}' lido com sucesso!")

        # Detecta formato do arquivo
        file_format, relevant_cols = detect_file_format(df)

        if file_format == "unknown":
            st.error("""
             **Formato de arquivo não reconhecido**

            O arquivo deve conter:
            - **Opção 1:** Colunas com nomes das dimensões COPSOQ (ex: 'Exigências Quantitativas', 'Burnout', 'Stress')
            - **Opção 2:** Colunas Resp_Q1, Resp_Q2... ou P1, P2, P3... com respostas individuais
            """)

            with st.expander(" Debug: Colunas encontradas"):
                st.write(list(df.columns))

            st.stop()

        # Mostra formato detectado
        if file_format == "calculated_scores":
            st.success(f" **Formato detectado:** Scores já calculados ({len(relevant_cols)} dimensões)")
        else:
            st.success(f" **Formato detectado:** Respostas brutas ({len(relevant_cols)} perguntas)")

        # VALIDAES
        validation_messages = []

        # Valida número de respostas
        if len(df) < 5:
            validation_messages.append(("error", f"Poucas respostas: {len(df)}. Mínimo: 5 para análise confiável."))
        elif len(df) < 10:
            validation_messages.append(("warning", f"Número baixo de respostas: {len(df)}. Recomendado: pelo menos 10."))

        # Valida dimensões/perguntas
        if file_format == "calculated_scores" and len(relevant_cols) < 5:
            validation_messages.append(("error", f"Poucas dimensões encontradas: {len(relevant_cols)}. Esperado: pelo menos 5."))

        # Valida dados ausentes
        null_pct = (df[relevant_cols].isnull().sum().sum() / df[relevant_cols].size) * 100 if relevant_cols else 0
        if null_pct > 40:
            validation_messages.append(("error", f"Alto percentual de dados ausentes: {null_pct:.1f}%."))
        elif null_pct > 20:
            validation_messages.append(("warning", f"Percentual moderado de dados ausentes: {null_pct:.1f}%."))

        # Mostra mensagens de validação
        for msg_type, msg_text in validation_messages:
            if msg_type == "error":
                st.error(f" {msg_text}")
            elif msg_type == "warning":
                st.warning(f"️ {msg_text}")

        # Bloqueia se houver erros críticos
        has_critical_errors = any(msg[0] == "error" for msg in validation_messages)

        if has_critical_errors:
            st.error("**Não é possível prosseguir devido aos erros acima.**")
            st.stop()

        # Preview dos dados
        with st.expander("️ Pré-visualização dos Dados"):
            st.write(f"**Dimensões:** {len(df)} linhas  {len(df.columns)} colunas")
            st.write(f"**Colunas relevantes:** {len(relevant_cols)}")
            st.dataframe(df[relevant_cols].head(10), width='stretch')

        st.divider()

        # Configuração da análise
        st.subheader("️ Configuração da Análise")

        nome_analise = st.text_input(
            "Nome da Análise",
            f"COPSOQ III - {uploaded_file.name.split('.')[0]}"
        )

# Botão de análise (com key e width="stretch")
if st.button(" Executar Análise COPSOQ III", type="primary", key="btn_run_copsoq3", width="stretch"):
    with st.spinner("A processar questionários COPSOQ III..."):
        try:
            if df is None or file_format == "unknown":
                st.error(" Carregue um arquivo válido antes de executar a análise.")
                st.stop()

            if file_format == "calculated_scores":
                # Extrai scores do arquivo
                scores = extract_scores_from_df(df, relevant_cols)

                # Cria AnalysisResult diretamente (sem usar processor)
                from models.enums import RiskLevel
                from models.analysis import AnalysisResult

                # Calcula risco baseado na média
                avg_score = sum(scores.values()) / len(scores) if scores else 50
                if avg_score < 40:
                    risk = RiskLevel.HIGH
                elif avg_score < 60:
                    risk = RiskLevel.MODERATE
                else:
                    risk = RiskLevel.LOW

                analysis_result = AnalysisResult(
                    id=hashlib.md5(f"copsoq_{datetime.now()}".encode()).hexdigest()[:8],
                    type=ANALYSIS_TYPE_FOR_THIS_PAGE,
                    name=nome_analise or f"COPSOQ III - {uploaded_file.name.split('.')[0]}",
                    timestamp=datetime.now(),
                    data=scores,
                    metadata={
                        'version': 'III',
                        'n_responses': len(df),
                        'format': 'calculated_scores',
                        'coverage': 100.0
                    },
                    quality=None,
                    risk_level=risk,
                    insights=[f" Dimensão mais crítica: '{min(scores.items(), key=lambda x: x[1])[0]}' com score {min(scores.values()):.1f}"]
                )
            else:
                # Processa respostas brutas (usa processador normal)
                analysis_result = processor.process(data=df, name=nome_analise)

            st.session_state.latest_analysis = analysis_result
            st.session_state.analysis_ready = True

            # Salva automaticamente
            try:
                storage.save_analysis(analysis_result)
                st.success(" Análise salva automaticamente!")
            except Exception as e:
                st.warning(f"Análise calculada, mas não foi possível salvar: {e}")

        except ValueError as e:
            st.error(f" Erro de validação: {e}")
        except Exception as e:
            st.error(f" Erro inesperado ao processar: {e}")
            st.exception(e)

# --- Renderização de Resultados ---
if 'latest_analysis' in st.session_state and st.session_state.latest_analysis is not None:
    if st.session_state.latest_analysis.type == ANALYSIS_TYPE_FOR_THIS_PAGE:
        if st.session_state.get('analysis_ready', False):
            st.divider()
            render_results(st.session_state.latest_analysis)



