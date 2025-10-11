# pages/3_💼_Workaholism_DUWAS.py
"""
Responsabilidade: Interface para análise de Workaholism usando DUWAS.
"""
import streamlit as st
import sys
import os
import time

# --- Path setup ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from components.ui_components import UIComponents
from components.ai_assistant import IntegratedAIAssistant, AutoInsightsComponent
from logic.workaholism_processor import WorkaholismProcessor
from models.enums import AnalysisType
from services.storage import get_persistent_storage
from services.api_client import APIClient

# --- Inicialização ---
ui = UIComponents()
processor = WorkaholismProcessor()
storage = get_persistent_storage()

api_client = APIClient()
ai_assistant = IntegratedAIAssistant(api_client)
ai_insights = AutoInsightsComponent(ai_assistant)

ANALYSIS_TYPE_FOR_THIS_PAGE = AnalysisType.WORKAHOLISM

# --- Perguntas DUWAS ---
duwas_questions = {
    "Trabalhar Excessivamente": [
        "Eu dou por mim a trabalhar mais tempo do que o planeado.",
        "Eu dedico mais tempo ao trabalho do que a atividades sociais ou de lazer.",
        "Eu trabalho mais do que os meus colegas.",
        "Eu sinto que as horas do dia não são suficientes para terminar o meu trabalho.",
        "Eu geralmente saio do escritório mais tarde que a maioria dos meus colegas."
    ],
    "Trabalhar Compulsivamente": [
        "Eu sinto-me culpado(a) quando tiro um tempo para relaxar.",
        "Eu penso no trabalho mesmo durante o meu tempo livre.",
        "Eu sinto-me ansioso(a) ou inquieto(a) em dias que não trabalho.",
        "Eu tenho dificuldade em me 'desligar' do trabalho.",
        "Outras pessoas dizem que eu trabalho demais."
    ]
}

# Opções de resposta
duwas_response_options = {
    "Quase Nunca / Nunca": 1,
    "Às vezes": 2,
    "Frequentemente": 3,
    "Quase Sempre / Sempre": 4
}


def render_results(analysis):
    """Renderiza resultados DUWAS"""
    st.success(f"✅ Análise '{analysis.name}' concluída!")
    
    scores = analysis.data
    excessive = scores.get("Trabalhar Excessivamente", 0)
    compulsive = scores.get("Trabalhar Compulsivamente", 0)
    
    # Scores principais
    st.subheader("📊 Resultados DUWAS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ui.render_metric_card(
            "Trabalhar Excessivamente",
            f"{excessive}/20",
            icon="🏃",
            color=analysis.risk_level.color,
            help_text="Mede quanto tempo você dedica ao trabalho"
        )
        
        # Interpretação
        if excessive >= 15:
            st.error("🚨 Nível muito alto")
        elif excessive >= 12:
            st.warning("⚠️ Nível alto")
        elif excessive >= 8:
            st.info("ℹ️ Nível moderado")
        else:
            st.success("✅ Nível normal")
    
    with col2:
        ui.render_metric_card(
            "Trabalhar Compulsivamente",
            f"{compulsive}/20",
            icon="🧠",
            color=analysis.risk_level.color,
            help_text="Mede obsessão e dificuldade em se desligar"
        )
        
        # Interpretação
        if compulsive >= 15:
            st.error("🚨 Nível muito alto")
        elif compulsive >= 12:
            st.warning("⚠️ Nível alto")
        elif compulsive >= 8:
            st.info("ℹ️ Nível moderado")
        else:
            st.success("✅ Nível normal")
    
    # Classificação geral
    st.subheader("🎯 Classificação")
    
    if excessive > 12 and compulsive > 12:
        st.error("""
        **Workaholic (Viciado em Trabalho)**
        
        Você trabalha excessivamente E de forma compulsiva. Isso pode levar a:
        - Burnout
        - Problemas de saúde
        - Conflitos trabalho-família
        - Deterioração de relacionamentos
        
        **Ação recomendada:** Procure apoio profissional e estabeleça limites claros.
        """)
    
    elif excessive > 12:
        st.warning("""
        **Trabalho Excessivo (sem compulsão)**
        
        Você trabalha muitas horas, mas não parece obcecado. Pontos de atenção:
        - Risco de fadiga acumulada
        - Possível pressão externa
        - Necessidade de melhor gestão do tempo
        
        **Ação recomendada:** Revise prioridades e delegue quando possível.
        """)
    
    elif compulsive > 12:
        st.warning("""
        **Trabalho Compulsivo (sem excesso de horas)**
        
        Você pensa constantemente no trabalho, mesmo sem trabalhar longas horas:
        - Dificuldade em relaxar
        - Ansiedade relacionada ao trabalho
        - Falta de desconexão mental
        
        **Ação recomendada:** Pratique mindfulness e estabeleça rotinas de desconexão.
        """)
    
    else:
        st.success("""
        **Equilíbrio Saudável**
        
        Seus scores indicam uma relação equilibrada com o trabalho.
        Continue mantendo:
        - Limites claros entre trabalho e vida pessoal
        - Tempo para hobbies e família
        - Capacidade de desconectar
        """)
    
    # Insights automáticos
    if analysis.insights:
        st.subheader("💡 Insights Automáticos")
        for insight in analysis.insights:
            if "alto" in insight.lower():
                st.warning(insight)
            else:
                st.info(insight)
    
    # Recomendações específicas
    st.subheader("🎯 Recomendações Personalizadas")
    
    recommendations = []
    
    if excessive > 10:
        recommendations.append("📅 **Gestão de tempo:** Use técnicas como Pomodoro e estabeleça horários fixos de saída")
    
    if compulsive > 10:
        recommendations.append("🧘 **Mindfulness:** Pratique meditação e exercícios de respiração para desligar mentalmente")
    
    if excessive > 10 or compulsive > 10:
        recommendations.append("🏃 **Atividade física:** Exercícios regulares ajudam a reduzir ansiedade relacionada ao trabalho")
        recommendations.append("👥 **Suporte social:** Compartilhe suas preocupações com amigos, família ou terapeuta")
    
    for rec in recommendations:
        st.info(rec)
    
    st.divider()
    
    # Componente de IA
    ai_insights.render(analysis)


# --- Interface Principal ---
ui.render_header(
    "💼 Dutch Work Addiction Scale (DUWAS)",
    "Avaliação de vício em trabalho (Workaholism)"
)

st.info("""
**Sobre o DUWAS:**

O DUWAS mede duas dimensões do workaholism:
- **Trabalhar Excessivamente:** Quantidade de tempo dedicado ao trabalho
- **Trabalhar Compulsivamente:** Obsessão e dificuldade de se desligar

**Instruções:** Responda com base em como você **geralmente** se comporta, não em situações excepcionais.
""")

st.divider()

# Formulário DUWAS
with st.form(key="duwas_form"):
    responses = {}
    
    for dimension, questions in duwas_questions.items():
        st.subheader(f"📋 {dimension}")
        st.caption(f"{len(questions)} perguntas")
        
        for i, question in enumerate(questions):
            key = f"duwas_{dimension.replace(' ', '')}_{i}"
            
            response = st.radio(
                question,
                options=list(duwas_response_options.keys()),
                horizontal=True,
                key=key,
                index=None  # Força seleção explícita
            )
            
            responses[key] = response
        
        st.divider()
    
    nome_analise = st.text_input(
        "Nome da Análise",
        f"Workaholism - {st.session_state.get('user_name', 'Avaliação')}"
    )
    
    submitted = st.form_submit_button(
        "🚀 Calcular Resultados",
        type="primary",
        use_container_width=True
    )
    
    if submitted:
        # VALIDAÇÃO: Verifica se todas as perguntas foram respondidas
        unanswered = [key for key, value in responses.items() if value is None]
        
        if unanswered:
            st.error(f"❌ Por favor, responda todas as {len(unanswered)} perguntas pendentes antes de submeter.")
            st.warning("Role para cima e verifique se há perguntas sem resposta.")
            
            # Mostra quais dimensões têm perguntas pendentes
            pending_dims = set()
            for key in unanswered:
                if "TrabalharExcessivamente" in key:
                    pending_dims.add("Trabalhar Excessivamente")
                elif "TrabalharCompulsivamente" in key:
                    pending_dims.add("Trabalhar Compulsivamente")
            
            if pending_dims:
                st.info(f"Dimensões com respostas pendentes: {', '.join(pending_dims)}")
        else:
            with st.spinner("A calcular scores de workaholism..."):
                try:
                    analysis_result = processor.process(
                        name=nome_analise,
                        responses=responses
                    )
                    
                    st.session_state.latest_analysis = analysis_result
                    st.session_state.analysis_ready = True
                    
                    # Salva automaticamente
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