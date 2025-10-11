# pages/2_🔥_Esgotamento_CBI.py
# Responsabilidade: Apresentar a interface para a ferramenta de análise de Esgotamento.

import streamlit as st
import numpy as np
import hashlib
import sys
import os
from datetime import datetime

# --- Adiciona o diretório raiz ao Python Path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # CORREÇÃO: abspath
if project_root not in sys.path:
    sys.path.append(project_root)
# ------------------------------------------------

# Importa os nossos módulos personalizados
from components.ui_components import UIComponents
from components.ai_assistant import AutoInsightsComponent, IntegratedAIAssistant
from logic.burnout_processor import BurnoutProcessor
from models.enums import AnalysisType, RiskLevel
from services.storage import get_persistent_storage
from services.api_client import APIClient

# --- Constantes do CBI (movidas para evitar importação circular) ---
cbi_questions = {
    "Burnout Pessoal": [
        {"question": "Com que frequência você se sente esgotado(a) física e emocionalmente?", "inverted": False},
        {"question": "Com que frequência você se sente exausto(a) ao final de um dia de trabalho?", "inverted": False},
        {"question": "Com que frequência você se sente cansado(a) pela manhã, só de pensar em mais um dia de trabalho?", "inverted": False},
        {"question": "Você tem energia para sua família e amigos durante seu tempo livre?", "inverted": True},
        {"question": "Com que frequência você se sente desgastado(a)?", "inverted": False},
        {"question": "Com que frequência você se sente fraco(a) e suscetível a doenças?", "inverted": False}
    ],
    "Burnout Relacionado ao Trabalho": [
        {"question": "Você se sente esgotado(a) pelo seu trabalho?", "inverted": False},
        {"question": "Você se sente frustrado(a) com seu trabalho?", "inverted": False},
        {"question": "O seu trabalho te cansa emocionalmente?", "inverted": False},
        {"question": "O seu trabalho te cansa fisicamente?", "inverted": False},
        {"question": "Você acha que está a trabalhar demais?", "inverted": False},
        {"question": "Você tem pique para trabalhar?", "inverted": True},
        {"question": "Você duvida que seu trabalho tenha algum significado?", "inverted": False}
    ],
    "Burnout Relacionado ao Cliente": [
        {"question": "Você acha desgastante trabalhar com clientes?", "inverted": False},
        {"question": "Você se sente farto(a) de trabalhar com clientes?", "inverted": False},
        {"question": "Você se pergunta por quanto tempo ainda conseguirá trabalhar com clientes?", "inverted": False},
        {"question": "Você acha que dá mais do que recebe ao trabalhar com clientes?", "inverted": False},
        {"question": "Você se sente esgotado(a) por ter que se relacionar com clientes no seu trabalho?", "inverted": False},
        {"question": "Você tem energia para trabalhar com clientes?", "inverted": True}
    ]
}

cbi_response_options = {
    "Sempre / Quase Sempre": 100, 
    "Frequentemente": 75, 
    "Às vezes": 50, 
    "Raramente": 25, 
    "Nunca / Quase Nunca": 0
}

cbi_inverted_options = {
    "Sempre / Quase Sempre": 0, 
    "Frequentemente": 25, 
    "Às vezes": 50, 
    "Raramente": 75, 
    "Nunca / Quase Nunca": 100
}

# --- Inicialização da Página ---
ui = UIComponents()
processor = BurnoutProcessor()
storage = get_persistent_storage()
api_client = APIClient()
ai_assistant = IntegratedAIAssistant(api_client)
auto_insights = AutoInsightsComponent(ai_assistant)
ANALYSIS_TYPE_FOR_THIS_PAGE = AnalysisType.BURNOUT_CBI

def get_risk_info(overall_score: float):
    """Determina o nível de risco com base na pontuação geral."""
    if overall_score >= 75:
        return RiskLevel.HIGH, "#EF4444", "🚨 ALTO"
    elif overall_score >= 50:
        return RiskLevel.MODERATE, "#F59E0B", "⚠️ MODERADO"
    else:
        return RiskLevel.LOW, "#10B981", "✅ BAIXO"

def render_results(analysis):
    """Renderiza os resultados da análise e os componentes de IA."""
    st.success(f"✅ Análise '{analysis.name}' concluída!")
    
    # Botões de ação
    col_save, col_export = st.columns(2)
    with col_save:
        if st.button("💾 Salvar Análise", use_container_width=True):
            try:
                storage.save_analysis(analysis)
                st.success("Análise salva com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar análise: {e}")
    
    with col_export:
        if st.button("📤 Exportar Resultados", use_container_width=True):
            st.info("Funcionalidade de exportação em desenvolvimento")
    
    overall = analysis.metadata.get('overall_score', 0)
    
    # CORREÇÃO: Exibir métrica principal corretamente
    st.subheader("📊 Score Geral de Esgotamento")
    st.metric(
        label="Pontuação Total", 
        value=f"{overall:.1f}/100",
        delta=None
    )
    
    # CORREÇÃO: Exibir nível de risco corretamente
    risk_level, risk_color, risk_text = get_risk_info(overall)
    st.markdown(f"**Nível de Risco:** <span style='color: {risk_color}; font-weight: bold;'>{risk_text}</span>", unsafe_allow_html=True)
    
    # Dimensões do burnout
    st.subheader("📈 Dimensões do Esgotamento")
    cols = st.columns(len(analysis.data))
    for i, (dim, score) in enumerate(analysis.data.items()):
        with cols[i]:
            # CORREÇÃO: Formatar nome da dimensão
            dim_name = dim.replace("Burnout ", "").replace("Relacionado ao ", "")
            st.metric(label=dim_name, value=f"{score:.1f}")
            
            # Barra de progresso colorida baseada no risco
            risk_color_dim = "#EF4444" if score >= 75 else "#F59E0B" if score >= 50 else "#10B981"
            st.markdown(
                f"<div style='background: #e0e0e0; border-radius: 10px; height: 10px; margin: 5px 0;'>"
                f"<div style='background: {risk_color_dim}; width: {score}%; height: 100%; border-radius: 10px;'></div>"
                f"</div>", 
                unsafe_allow_html=True
            )
            
    st.divider()
    # Componente de IA
    auto_insights.render(analysis)

# --- Estrutura Principal da Página ---
ui.render_header("Esgotamento (CBI)", "Análise com o Copenhagen Burnout Inventory.")

# O formulário garante que todas as respostas são submetidas de uma só vez.
with st.form(key="cbi_form"):
    responses = {}
    
    # Gera dinamicamente as perguntas do questionário
    for dimension, questions_data in cbi_questions.items():
        st.subheader(dimension)
        for item in questions_data:
            # Cria uma chave única para cada pergunta para o estado do Streamlit
            q_hash = hashlib.md5(item['question'].encode()).hexdigest()[:8]
            key = f"cbi_{dimension.replace(' ', '')}_{q_hash}"
            responses[key] = st.radio(
                label=item['question'], 
                options=list(cbi_response_options.keys()), 
                horizontal=True, 
                key=key
            )
            
    nome_analise = st.text_input("Nome da análise:", f"Esgotamento-{datetime.now().strftime('%Y%m%d-%H%M')}")

    submitted = st.form_submit_button("Calcular Resultados", type="primary")

if submitted:
    with st.spinner("Processando análise..."):
        analysis_result = processor.process(nome_analise, responses)
        st.session_state.latest_analysis = analysis_result
        # Salva automaticamente
        try:
            storage.save_analysis(analysis_result)
            st.success("✅ Análise salva automaticamente!")
        except Exception as e:
            st.warning(f"Análise calculada, mas não foi possível salvar: {e}")

# --- Lógica de Exibição de Resultados ---
if 'latest_analysis' in st.session_state and st.session_state.latest_analysis is not None:
    if st.session_state.latest_analysis.type == ANALYSIS_TYPE_FOR_THIS_PAGE:
        render_results(st.session_state.latest_analysis)