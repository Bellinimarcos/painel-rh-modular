# components/ai_assistant.py
# Responsabilidade: Gerir toda a interface e lógica relacionada com a IA.

import streamlit as st
import time
import logging
import pandas as pd

# Importa os nossos módulos personalizados
from models.analysis import AnalysisResult
from models.enums import AnalysisType
from services.api_client import APIClient
from services.storage import get_persistent_storage
from config.settings import AppConfig

# Configura o logger e inicializa os serviços
logger = logging.getLogger(__name__)
storage = get_persistent_storage()

class IntegratedAIAssistant:
    """
    Classe de Lógica para a IA. Gera insights e perguntas contextuais.
    """
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
    
    def generate_auto_insights(self, analysis: AnalysisResult) -> list[str]:
        """Gera insights rápidos e automáticos com base nos dados da análise."""
        insights = []
        analysis_type_value = analysis.type.value

        if analysis_type_value == AnalysisType.BURNOUT_CBI.value:
            # Lógica para Burnout (será usada no futuro)
            scores = analysis.data
            if scores:
                max_dimension = max(scores.items(), key=lambda x: x[1])
                if max_dimension[1] > 75:
                    insights.append(f"🔥 Dimensão '{max_dimension[0]}' em nível crítico ({max_dimension[1]:.1f}/100)")
                
                overall = sum(scores.values()) / len(scores)
                if overall > 60:
                    insights.append(f"🚨 Score geral de burnout preocupante ({overall:.1f}/100)")

        elif analysis_type_value in [AnalysisType.COPSOQ_II.value, AnalysisType.COPSOQ_III.value]:
            # Lógica específica para COPSOQ
            problem_dimensions = sorted([(k, v) for k, v in analysis.data.items() if v < 50], key=lambda item: item[1])
            if problem_dimensions:
                worst = problem_dimensions[0]
                insights.append(f"📊 Dimensão mais crítica: '{worst[0]}' com score {worst[1]:.1f}.")
        
        if not insights:
            insights.append("✅ Análise concluída. Dados dentro dos parâmetros esperados.")
            
        return insights
    
    def get_contextual_questions(self, analysis: AnalysisResult) -> list[str]:
        """Gera uma lista de perguntas sugeridas para a página de chat da IA."""
        return [
            "Quais são os principais riscos identificados nestes dados?",
            "Sugira 3 ações concretas para melhorar a dimensão mais crítica.",
            "Como estes resultados se comparam com benchmarks do setor?"
        ]

class AutoInsightsComponent:
    """
    Componente de UI que renderiza os insights automáticos e os botões de interação com a IA.
    """
    def __init__(self, ai_assistant: IntegratedAIAssistant):
        self.ai_assistant = ai_assistant

    def render(self, analysis: AnalysisResult):
        """Renderiza a secção completa de insights da IA."""
        st.subheader("🤖 Insights Automáticos do Co-piloto")
        
        try:
            insights = self.ai_assistant.generate_auto_insights(analysis)
            for insight in insights:
                if "🚨" in insight or "crítico" in insight.lower():
                    st.error(insight)
                elif "📊" in insight or "⚠️" in insight:
                    st.warning(insight)
                else:
                    st.info(insight)
        except Exception as e:
            st.error("Ocorreu um erro ao gerar os insights automáticos.")
            logger.error(f"Erro em generate_auto_insights: {e}")

                # Botões de Ação da IA
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Análise IA Detalhada", key=f"ai_detail_{analysis.id}", use_container_width=True):
                self._show_detailed_ai_analysis(analysis)
        
        with col2:
            if st.button("💬 Conversar sobre Resultados", key=f"ai_chat_{analysis.id}", use_container_width=True):
                storage.save_analysis(analysis)
                st.session_state.selected_analysis_id = analysis.id
                # Redireciona para página do Assistente IA
                st.switch_page("pages/6_🤖_Assistente_IA.py")

    def _prepare_data_summary(self, analysis: 'AnalysisResult') -> str:
        """Prepara resumo dos dados para o prompt"""
        
        summary_parts = []
        for key, value in analysis.data.items():
            # Ignora DataFrames
            if isinstance(value, pd.DataFrame):
                summary_parts.append(f"{key}: [DataFrame com {len(value)} linhas]")
            elif isinstance(value, (int, float)):
                summary_parts.append(f"{key}: {value:.2f}")
            elif isinstance(value, str):
                summary_parts.append(f"{key}: {value}")
        
        if analysis.metadata:
            for key, value in analysis.metadata.items():
                if isinstance(value, (int, float, str)) and key != 'timestamp':
                    summary_parts.append(f"{key}: {value}")
        
        return "; ".join(summary_parts)
    
    def _show_detailed_ai_analysis(self, analysis: AnalysisResult):
        """Mostra a análise detalhada da IA num expander."""
        
        # Chave única para controlar se já foi gerada
        ai_text_key = f"ai_text_{analysis.id}"
        
        # Verifica se já existe análise da IA salva
        if not st.session_state.get(ai_text_key):
            # Se não existe, verifica se tem nos metadata da análise
            if analysis.metadata and 'ai_detailed_analysis' in analysis.metadata:
                st.session_state[ai_text_key] = analysis.metadata['ai_detailed_analysis']
        
        with st.expander("🤖 Análise IA Detalhada", expanded=True):
            # Se já existe no session_state, mostra
            if st.session_state.get(ai_text_key):
                st.success("🤖 Análise IA sucesso")
                st.markdown(st.session_state[ai_text_key])
            else:
                # Se não existe, gera nova
                with st.spinner("A IA está a analisar os dados..."):
                    data_summary = self._prepare_data_summary(analysis)
                    prompt = f"""
                    Como consultor de RH, analise os seguintes dados da ferramenta de RH:
                    {data_summary}

                    Forneça:
                    1. **Diagnóstico Curto:** Qual é o principal problema revelado?
                    2. **Principais Riscos:** Quais os 3 maiores riscos?
                    3. **Ações Recomendadas:** Sugira 2 ações práticas e de baixo custo.
                    """
                    
                    response = self.ai_assistant.api_client.call_gemini(prompt)
                    
                    if response:
                        # Salva no session_state
                        st.session_state[ai_text_key] = response
                        
                        # Salva no metadata da análise
                        if not analysis.metadata:
                            analysis.metadata = {}
                        analysis.metadata['ai_detailed_analysis'] = response
                        
                        # Persiste no storage
                        try:
                            storage.save_analysis(analysis)
                            logger.info(f"Análise IA salva para {analysis.id}")
                        except Exception as e:
                            logger.error(f"Erro ao salvar análise IA: {e}")
                        
                        st.success("🤖 Análise IA sucesso")
                        st.markdown(response)
                    else:
                        st.error("Não foi possível obter uma resposta da IA. Verifique a chave da API.")