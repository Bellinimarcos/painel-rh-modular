# main.py - Dashboard Consolidado
# Responsabilidade: Página inicial com visão geral de todas as análises

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import Counter

from services.storage import get_persistent_storage
from config.settings import AppConfig
from utils.backup_manager import render_backup_interface

# Validação de configuração ao iniciar
try:
    AppConfig.validate()
except ValueError as e:
    st.error(str(e))
    st.stop()

# Configuração da página
st.set_page_config(
    page_title=f"Painel Inteligente de RH - v{AppConfig.APP_VERSION}",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

def setup_session():
    """Inicializa o estado da sessão."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.latest_analysis = None
        st.session_state.debug_mode = False

def verify_api_key():
    """Verifica se a chave da API está configurada."""
    if not AppConfig.GEMINI_API_KEY:
        st.sidebar.error("🔑 API não configurada")
        st.sidebar.info("Configure `GEMINI_API_KEY` no arquivo .env")
        return False
    return True

def render_sidebar():
    """Renderiza a barra lateral."""
    storage = get_persistent_storage()

    with st.sidebar:
        st.markdown(
            f"<h1 style='color: white; text-align: center;'>🧠 Painel RH v{AppConfig.APP_VERSION}</h1>", 
            unsafe_allow_html=True
        )
        
        st.divider()
        
        if verify_api_key():
            st.sidebar.success("✅ API Configurada")

        st.metric("Análises Salvas", len(storage.get_analyses()))
        
        # Sistema de Backup
        render_backup_interface()
        
        st.divider()
        st.toggle("🐞 Modo de Depuração", key="debug_mode")
        
        if st.button("🔄 Limpar Dados", use_container_width=True):
            if st.sidebar.checkbox("Confirmar limpeza"):
                storage.clear_all()
                st.session_state.clear()
                st.rerun()

def render_analysis_details(analysis):
    """Renderiza detalhes completos de uma análise em um expander."""
    
    # Informações básicas
    st.write(f"**📅 Data:** {analysis.timestamp.strftime('%d/%m/%Y %H:%M')}")
    st.write(f"**📊 Tipo:** {analysis.type.value}")
    
    if analysis.risk_level:
        st.write(f"**⚠️ Nível de Risco:** {analysis.risk_level.emoji} {analysis.risk_level.label}")
    
    if analysis.quality:
        st.write(f"**✅ Qualidade:** {analysis.quality.label}")
    
    st.divider()
    
    # Dados/Métricas principais
    st.markdown("**📈 Métricas:**")
    
    # Filtra apenas dados numéricos ou strings simples (ignora DataFrames)
    displayable_data = {}
    for key, value in analysis.data.items():
        if isinstance(value, (int, float)):
            displayable_data[key] = f"{value:.2f}"
        elif isinstance(value, str):
            displayable_data[key] = value
        elif isinstance(value, pd.DataFrame):
            displayable_data[key] = f"[DataFrame com {len(value)} linhas]"
    
    if displayable_data:
        # Mostra em colunas se tiver muitos dados
        items = list(displayable_data.items())
        if len(items) <= 6:
            cols = st.columns(min(3, len(items)))
            for idx, (key, value) in enumerate(items):
                with cols[idx % 3]:
                    st.metric(key.replace('_', ' ').title(), value)
        else:
            # Se tiver muitos, mostra em formato de lista
            for key, value in items[:10]:  # Limita a 10
                st.write(f"- **{key.replace('_', ' ').title()}:** {value}")
    
    st.divider()
    
    # Insights automáticos
    if analysis.insights:
        st.markdown("**💡 Insights Automáticos:**")
        for insight in analysis.insights:
            if "🚨" in insight or "crítico" in insight.lower():
                st.error(insight)
            elif "⚠️" in insight or "atenção" in insight.lower():
                st.warning(insight)
            else:
                st.info(insight)
        st.divider()
    
    # Insights da IA (se existirem)
    if analysis.metadata and 'ai_detailed_analysis' in analysis.metadata:
        st.markdown("**🤖 Análise Detalhada da IA:**")
        st.success("Análise da IA disponível")
        with st.expander("Ver análise completa da IA", expanded=False):
            st.markdown(analysis.metadata['ai_detailed_analysis'])
    else:
        st.info("💡 Insights detalhados da IA não foram gerados para esta análise")

def render_metrics_overview(analyses):
    """Renderiza métricas gerais do dashboard."""
    st.subheader("📊 Visão Geral")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total de análises
    with col1:
        st.metric(
            "Total de Análises",
            len(analyses),
            help="Número total de análises realizadas"
        )
    
    # Análises nos últimos 7 dias
    recent = [a for a in analyses if (datetime.now() - a.timestamp).days <= 7]
    with col2:
        st.metric(
            "Últimos 7 Dias",
            len(recent),
            help="Análises realizadas na última semana"
        )
    
    # Análises de alto risco
    high_risk = [a for a in analyses if a.risk_level and a.risk_level.label in ["Alto", "Crítico"]]
    with col3:
        delta_color = "inverse" if high_risk else "normal"
        st.metric(
            "Alertas Críticos",
            len(high_risk),
            delta=f"{len(high_risk)} análises",
            delta_color=delta_color,
            help="Análises com risco Alto ou Crítico"
        )
    
    # Tipos de análise únicos
    unique_types = len(set(a.type.value for a in analyses))
    with col4:
        st.metric(
            "Ferramentas Utilizadas",
            unique_types,
            help="Diferentes tipos de análise realizadas"
        )

def render_risk_alerts(analyses):
    """Renderiza alertas de risco crítico."""
    high_risk = [
        a for a in analyses 
        if a.risk_level and a.risk_level.label in ["Alto", "Crítico"]
    ]
    
    if high_risk:
        st.subheader("🚨 Alertas Críticos")
        
        for analysis in sorted(high_risk, key=lambda x: x.timestamp, reverse=True)[:5]:
            with st.expander(
                f"{analysis.risk_level.emoji} {analysis.name} - {analysis.type.value}",
                expanded=False
            ):
                render_analysis_details(analysis)
    else:
        st.success("✅ Nenhum alerta crítico no momento")

def render_analysis_timeline(analyses):
    """Renderiza linha do tempo das análises."""
    st.subheader("📅 Linha do Tempo")
    
    if not analyses:
        st.info("Nenhuma análise realizada ainda")
        return
    
    # Prepara dados para o gráfico
    df_timeline = pd.DataFrame([
        {
            'Data': a.timestamp.date(),
            'Tipo': a.type.value,
            'Nome': a.name,
            'Risco': a.risk_level.label if a.risk_level else 'N/A'
        }
        for a in analyses
    ])
    
    # Agrupa por data e tipo
    df_grouped = df_timeline.groupby(['Data', 'Tipo']).size().reset_index(name='Quantidade')
    
    fig = px.line(
        df_grouped,
        x='Data',
        y='Quantidade',
        color='Tipo',
        title='Análises Realizadas ao Longo do Tempo',
        markers=True
    )
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Número de Análises",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_analysis_distribution(analyses):
    """Renderiza distribuição de análises por tipo."""
    st.subheader("📈 Distribuição por Tipo de Análise")
    
    if not analyses:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza - tipos de análise
        type_counts = Counter(a.type.value for a in analyses)
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(type_counts.keys()),
            values=list(type_counts.values()),
            hole=0.4
        )])
        fig_pie.update_layout(
            title="Análises por Tipo",
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Gráfico de barras - níveis de risco
        risk_data = [a.risk_level.label for a in analyses if a.risk_level]
        
        if risk_data:
            risk_counts = Counter(risk_data)
            
            colors = {
                'Baixo': '#10B981',
                'Moderado': '#F59E0B',
                'Alto': '#EF4444',
                'Crítico': '#7C3AED'
            }
            
            fig_bar = go.Figure(data=[go.Bar(
                x=list(risk_counts.keys()),
                y=list(risk_counts.values()),
                marker_color=[colors.get(k, '#3B82F6') for k in risk_counts.keys()]
            )])
            fig_bar.update_layout(
                title="Análises por Nível de Risco",
                xaxis_title="Nível de Risco",
                yaxis_title="Quantidade",
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)

def render_recent_analyses(analyses):
    """Renderiza lista de análises recentes com opção de ver detalhes."""
    st.subheader("🕒 Análises Recentes")
    
    if not analyses:
        st.info("Nenhuma análise realizada ainda. Use as ferramentas no menu lateral para começar.")
        return
    
    # Ordena por data (mais recente primeiro)
    recent = sorted(analyses, key=lambda x: x.timestamp, reverse=True)[:15]
    
    for idx, analysis in enumerate(recent):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.write(f"**{analysis.name}**")
        
        with col2:
            st.write(f"📅 {analysis.timestamp.strftime('%d/%m/%Y %H:%M')}")
        
        with col3:
            if analysis.risk_level:
                st.write(f"{analysis.risk_level.emoji} {analysis.risk_level.label}")
            else:
                st.write("N/A")
        
        with col4:
            # Botão para ver detalhes
            if st.button("👁️ Ver", key=f"view_{analysis.id}_{idx}", use_container_width=True):
                st.session_state[f'show_details_{analysis.id}'] = True
        
        # Mostra detalhes se o botão foi clicado
        if st.session_state.get(f'show_details_{analysis.id}', False):
            with st.container():
                with st.expander(f"📋 Detalhes: {analysis.name}", expanded=True):
                    render_analysis_details(analysis)
                    
                    # Botão para fechar
                    if st.button("✖️ Fechar", key=f"close_{analysis.id}_{idx}"):
                        st.session_state[f'show_details_{analysis.id}'] = False
                        st.rerun()
        
        st.divider()

def render_quick_insights(analyses):
    """Renderiza insights rápidos baseados nas análises."""
    st.subheader("💡 Insights Rápidos")
    
    if not analyses:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Principais Observações:**")
        
        # Ferramenta mais usada
        type_counts = Counter(a.type.value for a in analyses)
        most_used = type_counts.most_common(1)[0]
        st.write(f"🔹 Ferramenta mais utilizada: **{most_used[0]}** ({most_used[1]}x)")
        
        # Análises no último mês
        last_month = [a for a in analyses if (datetime.now() - a.timestamp).days <= 30]
        st.write(f"🔹 Análises no último mês: **{len(last_month)}**")
        
        # Taxa de risco alto
        high_risk = [a for a in analyses if a.risk_level and a.risk_level.label in ["Alto", "Crítico"]]
        risk_rate = (len(high_risk) / len(analyses) * 100) if analyses else 0
        st.write(f"🔹 Taxa de alertas críticos: **{risk_rate:.1f}%**")
    
    with col2:
        st.markdown("**Recomendações:**")
        
        if risk_rate > 30:
            st.warning("⚠️ Alta taxa de riscos críticos - revisar estratégias de intervenção")
        elif risk_rate < 10:
            st.success("✅ Baixa taxa de riscos - situação sob controle")
        else:
            st.info("ℹ️ Taxa moderada de riscos - manter monitoramento")
        
        if len(last_month) < 2:
            st.info("💡 Considere realizar análises mais frequentes para melhor acompanhamento")

# --- Execução Principal ---
setup_session()
render_sidebar()

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">Dashboard de RH</h1>
    <p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;">
        Visão consolidada de todas as análises organizacionais
    </p>
</div>
""", unsafe_allow_html=True)

# Carrega análises
storage = get_persistent_storage()
analyses = storage.get_analyses()

# Renderiza componentes
render_metrics_overview(analyses)

st.divider()

render_risk_alerts(analyses)

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    render_analysis_timeline(analyses)

with col2:
    render_analysis_distribution(analyses)

st.divider()

render_quick_insights(analyses)

st.divider()

render_recent_analyses(analyses)