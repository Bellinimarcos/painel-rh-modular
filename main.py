# main.py - Hub de Conformidade e Saúde Ocupacional (Projeto Itajubá 2026)
# Responsabilidade: Dashboard mestre com visão estratégica e pericial.

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from collections import Counter

from services.storage import get_persistent_storage
from config.settings import AppConfig
from utils.backup_manager import render_backup_interface

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title=f"Hub Compliance RPS - v{AppConfig.APP_VERSION}",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def setup_session():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.latest_analysis = None

def verify_api_key():
    if not AppConfig.GEMINI_API_KEY:
        st.sidebar.warning("⚠️ Co-piloto Offline: Configure a API Key")
        return False
    return True

# --- BARRA LATERAL (BRANDING PROFISSIONAL) ---
def render_sidebar():
    storage = get_persistent_storage()
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align: center; padding: 10px; background-color: #f8fafc; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='color: #1e3a8a; margin-bottom: 0;'>RPS Compliance</h2>
                <p style='color: #64748b; font-size: 0.85rem; font-weight: bold;'>Inteligência Pericial Itajubá</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.divider()
        if verify_api_key():
            st.success("🤖 Co-piloto IA: Ativo")

        st.metric("Base de Dados", f"{len(storage.get_analyses())} Análises")
        
        st.markdown("### ⚙️ Administração")
        render_backup_interface()
        
        st.divider()
        st.toggle("🐞 Debug Mode", key="debug_mode")
        
        if st.button("🗑️ Resetar Base de Dados", use_container_width=True):
            if st.sidebar.checkbox("Confirmar exclusão permanente"):
                storage.clear_all()
                st.session_state.clear()
                st.rerun()

# --- COMPONENTES DE VISUALIZAÇÃO ---
def render_metrics_overview(analyses):
    st.subheader("📊 Indicadores Estratégicos")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Volume de Dados", len(analyses), help="Total de diagnósticos processados")
    
    with col2:
        recent = [a for a in analyses if (datetime.now() - a.timestamp).days <= 7]
        st.metric("Atividade Semanal", len(recent), delta=f"{len(recent)} novos")
    
    with col3:
        high_risk = [a for a in analyses if a.risk_level and a.risk_level.label in ["Alto", "Crítico"]]
        status_msg = "🚨 Atenção Requerida" if high_risk else "✅ Ambiente Estável"
        st.metric("Status de Risco", f"{len(high_risk)} Alertas", delta=status_msg, delta_color="inverse" if high_risk else "normal")
    
    with col4:
        unique_tools = len(set(a.type.value for a in analyses))
        st.metric("Ferramentas", unique_tools, help="Diversidade de inventários aplicados")

def render_analysis_details(analysis):
    st.write(f"**📅 Data da Coleta:** {analysis.timestamp.strftime('%d/%m/%Y %H:%M')}")
    st.write(f"**🔬 Metodologia:** {analysis.type.value}")
    
    if analysis.risk_level:
        st.markdown(f"**Nível de Risco:** {analysis.risk_level.emoji} `{analysis.risk_level.label.upper()}`")
    
    st.divider()
    
    # Exibição de Scores
    st.markdown("**📈 Dimensões Processadas:**")
    items = list(analysis.data.items())
    cols = st.columns(3)
    for idx, (key, value) in enumerate(items):
        if isinstance(value, (int, float)):
            with cols[idx % 3]:
                st.metric(key, f"{value:.1f}")

    if analysis.metadata and 'ai_detailed_analysis' in analysis.metadata:
        st.divider()
        st.markdown("### 🤖 Parecer do Co-piloto IA")
        st.info(analysis.metadata['ai_detailed_analysis'])

# --- HEADER E EXECUÇÃO ---
setup_session()
render_sidebar()

# Header com Gradient Blue Itajubá
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
            padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);">
    <h1 style="color: white; margin: 0; font-family: 'Segoe UI', sans-serif; letter-spacing: -0.5px;">
        Hub Compliance RPS
    </h1>
    <p style="color: rgba(255,255,255,0.9); margin-top: 0.75rem; font-size: 1.2rem; font-weight: 300;">
        Gestão Estratégica de Riscos Psicossociais • <b>Projeto Itajubá 2026</b>
    </p>
</div>
""", unsafe_allow_html=True)

storage = get_persistent_storage()
analyses = storage.get_analyses()

if not analyses:
    st.info("👋 Bem-vindo, Marcos! Comece importando uma planilha do COPSOQ III no menu lateral para gerar os primeiros insights.")
else:
    render_metrics_overview(analyses)
    st.divider()
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        # Importamos aqui as funções de timeline/distribuição que você já tinha
        from main import render_analysis_timeline
        render_analysis_timeline(analyses)
    with col_t2:
        from main import render_analysis_distribution
        render_analysis_distribution(analyses)

    st.divider()
    # Lista de Análises Recentes
    st.subheader("🕒 Histórico de Diagnósticos")
    for a in sorted(analyses, key=lambda x: x.timestamp, reverse=True)[:10]:
        with st.expander(f"{a.risk_level.emoji if a.risk_level else '📊'} {a.name} - {a.timestamp.strftime('%d/%m/%Y')}"):
            render_analysis_details(a)