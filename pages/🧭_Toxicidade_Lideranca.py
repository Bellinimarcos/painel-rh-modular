"""
Página: Avaliação de Toxicidade em Lideranças
Módulo integrado ao Painel RH Modular
Projeto SER | Marcos Simões Bellini, CRP 04/37811
Versão Completa: 788 linhas
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

from config.questionario_toxicidade import (
    criar_questionario_toxicidade, ESCALA_LIKERT, obter_interpretacao
)
from logic.toxicidade_logic import GerenciadorAvaliacaoToxicidade


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Avaliação de Toxicidade em Lideranças",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CSS CUSTOMIZADO E ESTILOS
# ============================================================================

st.markdown("""
<style>
    /* Header principal */
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Dimensões */
    .dimensao-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-top: 25px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .dimensao-header h3 {
        margin: 0;
        font-size: 1.3rem;
    }
    
    /* Questões */
    .questao-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 4px solid #667eea;
    }
    
    /* Caixas de resultado */
    .result-box {
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .result-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Níveis de risco */
    .risk-high {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 6px solid #f44336;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 6px solid #ff9800;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 6px solid #4caf50;
    }
    
    .risk-excellent {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 6px solid #2196f3;
    }
    
    /* Métricas */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 5px;
    }
    
    .badge-excellent { background-color: #2196f3; color: white; }
    .badge-low { background-color: #4caf50; color: white; }
    .badge-medium { background-color: #ff9800; color: white; }
    .badge-high { background-color: #f44336; color: white; }
    
    /* Progress bar customizada */
    .custom-progress {
        background-color: #e0e0e0;
        border-radius: 10px;
        height: 25px;
        overflow: hidden;
    }
    
    .custom-progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        transition: width 0.3s ease;
    }
    
    /* Tabelas */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Botões */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Cards de recomendação */
    .recommendation-card {
        background: #fff9c4;
        border-left: 5px solid #fbc02d;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* Alertas personalizados */
    .custom-alert {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
    }
    
    .alert-danger {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    
    .alert-info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        color: #0c5460;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #888;
        margin-top: 3rem;
        padding: 2rem;
        font-size: 0.9rem;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Tooltip customizado */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INICIALIZAÇÃO DO SESSION STATE
# ============================================================================

def inicializar_session_state():
    """Inicializa todas as variáveis de sessão necessárias"""
    
    # Respostas do questionário
    if 'respostas_toxicidade' not in st.session_state:
        st.session_state.respostas_toxicidade = {}
    
    # Status da avaliação
    if 'avaliacao_completa' not in st.session_state:
        st.session_state.avaliacao_completa = False
    
    # Resultado atual
    if 'resultado_atual' not in st.session_state:
        st.session_state.resultado_atual = None
    
    # Página atual
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = "Nova Avaliação"
    
    # Dados do participante
    if 'dados_participante' not in st.session_state:
        st.session_state.dados_participante = {}
    
    # Configurações de visualização
    if 'mostrar_descricoes' not in st.session_state:
        st.session_state.mostrar_descricoes = True
    
    # Histórico de navegação
    if 'historico_navegacao' not in st.session_state:
        st.session_state.historico_navegacao = []
    
    # Filtros e ordenação
    if 'filtro_nivel_risco' not in st.session_state:
        st.session_state.filtro_nivel_risco = "Todos"
    
    if 'ordenacao_historico' not in st.session_state:
        st.session_state.ordenacao_historico = "Data (Mais Recente)"


# ============================================================================
# FUNÇÕES DE RENDERIZAÇÃO DE QUESTIONÁRIO
# ============================================================================

def renderizar_escala_likert(questao_id: int, texto: str, chave: str, tipo: str = "direta"):
    """
    Renderiza uma questão com escala Likert customizada
    
    Args:
        questao_id: ID da questão
        texto: Texto da questão
        chave: Chave única para o widget
        tipo: Tipo da questão (direta ou inversa)
    """
    # Container da questão
    st.markdown(f"""
    <div class="questao-container fade-in">
        <strong style="color: #667eea;">Questão {questao_id}</strong>
        <p style="margin: 10px 0; font-size: 1.05rem;">{texto}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Escala Likert
    col1, col2, col3, col4, col5 = st.columns(5)
    
    opcoes = list(ESCALA_LIKERT.keys())
    labels = list(ESCALA_LIKERT.values())
    
    resposta = None
    
    with col1:
        if st.button(f"1️⃣\n{labels[0]}", key=f"{chave}_1", use_container_width=True):
            resposta = opcoes[0]
    
    with col2:
        if st.button(f"2️⃣\n{labels[1]}", key=f"{chave}_2", use_container_width=True):
            resposta = opcoes[1]
    
    with col3:
        if st.button(f"3️⃣\n{labels[2]}", key=f"{chave}_3", use_container_width=True):
            resposta = opcoes[2]
    
    with col4:
        if st.button(f"4️⃣\n{labels[3]}", key=f"{chave}_4", use_container_width=True):
            resposta = opcoes[3]
    
    with col5:
        if st.button(f"5️⃣\n{labels[4]}", key=f"{chave}_5", use_container_width=True):
            resposta = opcoes[4]
    
    # Mostra resposta atual se já houver uma
    if questao_id in st.session_state.respostas_toxicidade:
        resp_atual = st.session_state.respostas_toxicidade[questao_id]
        st.success(f"✓ Resposta registrada: {resp_atual} - {ESCALA_LIKERT[resp_atual]}")
    
    # Registra resposta
    if resposta:
        st.session_state.respostas_toxicidade[questao_id] = resposta
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)


def renderizar_questionario(questionario):
    """
    Renderiza o questionário completo com todas as dimensões
    
    Args:
        questionario: Instância de QuestionarioToxicidade
    """
    # Header
    st.markdown(f"""
    <div class="fade-in">
        <h1 class="main-header">🧭 {questionario.titulo}</h1>
        <p class="sub-header">{questionario.descricao}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Instruções
    with st.expander("📋 **Instruções de Preenchimento**", expanded=True):
        st.markdown("""
        ### 👋 Bem-vindo(a) à Avaliação de Toxicidade em Lideranças
        
        Esta ferramenta foi desenvolvida para auxiliar na identificação de comportamentos tóxicos 
        em ambientes de liderança organizacional.
        
        #### 📝 Como responder:
        
        1. **Leia cada afirmação com atenção** - Não há respostas certas ou erradas
        2. **Pense na sua experiência real** com a liderança avaliada
        3. **Selecione a opção** que melhor representa a frequência do comportamento
        4. **Seja honesto(a)** - Suas respostas são confidenciais
        5. **Responda todas as questões** para obter um resultado completo
        
        #### 🎯 Escala de Resposta:
        
        - **1 - Discordo Totalmente**: Nunca acontece / Não se aplica
        - **2 - Discordo**: Acontece raramente (menos de 25% das vezes)
        - **3 - Neutro**: Acontece às vezes (cerca de 50% das vezes)
        - **4 - Concordo**: Acontece frequentemente (mais de 75% das vezes)
        - **5 - Concordo Totalmente**: Acontece sempre ou quase sempre
        
        #### 🔒 Confidencialidade:
        
        Todas as suas respostas serão tratadas com confidencialidade e utilizadas apenas 
        para fins de diagnóstico organizacional e desenvolvimento de liderança.
        
        ---
        
        **⏱️ Tempo estimado:** 10-15 minutos  
        **📊 Total de questões:** {len(questionario)} questões em {len(questionario.dimensoes)} dimensões
        """)
    
    st.markdown("---")
    
    # Opção de coletar dados do participante
    with st.expander("👤 Dados do Participante (Opcional)", expanded=False):
        st.markdown("*Preencha apenas se desejar identificar esta avaliação*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome (opcional)", key="participante_nome")
            cargo = st.text_input("Cargo (opcional)", key="participante_cargo")
        
        with col2:
            departamento = st.text_input("Departamento (opcional)", key="participante_dept")
            tempo_empresa = st.text_input("Tempo na empresa (opcional)", key="participante_tempo")
        
        if any([nome, cargo, departamento, tempo_empresa]):
            st.session_state.dados_participante = {
                "nome": nome,
                "cargo": cargo,
                "departamento": departamento,
                "tempo_empresa": tempo_empresa,
                "data_preenchimento": datetime.now().isoformat()
            }
    
    st.markdown("---")
    
    # Renderiza cada dimensão
    for idx, dimensao in enumerate(questionario.dimensoes, 1):
        st.markdown(f"""
        <div class="dimensao-header fade-in">
            <h3>📌 Dimensão {idx}: {dimensao.nome}</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">{dimensao.descricao}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Renderiza questões da dimensão
        for questao in dimensao.questoes:
            renderizar_escala_likert(
                questao_id=questao.id,
                texto=questao.texto,
                chave=f"questao_{questao.id}",
                tipo=questao.tipo.value
            )
        
        st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO DE RESULTADOS
# ============================================================================

def criar_grafico_radar(resultado):
    """Cria gráfico radar com pontuações por dimensão"""
    dimensoes = list(resultado.pontuacoes_dimensoes.keys())
    valores = list(resultado.pontuacoes_dimensoes.values())
    
    # Adiciona o primeiro valor no final para fechar o polígono
    dimensoes_circ = dimensoes + [dimensoes[0]]
    valores_circ = valores + [valores[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=valores_circ,
        theta=dimensoes_circ,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='rgba(102, 126, 234, 1)', width=2),
        name='Pontuação'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11)
            )
        ),
        showlegend=False,
        title={
            'text': "Perfil de Toxicidade por Dimensão",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333'}
        },
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def criar_grafico_barras_horizontal(resultado):
    """Cria gráfico de barras horizontais com pontuações"""
    df = pd.DataFrame({
        'Dimensão': list(resultado.pontuacoes_dimensoes.keys()),
        'Pontuação': list(resultado.pontuacoes_dimensoes.values()),
        'Nível': [resultado.niveis_risco_dimensoes[dim] 
                  for dim in resultado.pontuacoes_dimensoes.keys()]
    })
    
    # Ordena por pontuação
    df = df.sort_values('Pontuação', ascending=True)
    
    # Define cores
    color_map = {
        'Excelente': '#2196f3',
        'Baixo': '#4caf50',
        'Moderado': '#ff9800',
        'Alto': '#f44336'
    }
    
    df['Cor'] = df['Nível'].map(color_map)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['Dimensão'],
        x=df['Pontuação'],
        orientation='h',
        marker=dict(
            color=df['Cor'],
            line=dict(color='rgba(0,0,0,0.2)', width=1)
        ),
        text=df['Pontuação'].round(1),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Pontuação: %{x:.1f}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title="Pontuação por Dimensão (ordenado)",
        xaxis_title="Pontuação (0-100)",
        yaxis_title="",
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)')
    )
    
    return fig


def criar_grafico_gauge(pontuacao_total, nivel_risco):
    """Cria gráfico tipo gauge para pontuação geral"""
    
    # Define cor baseada no nível
    cor_map = {
        'Excelente': '#2196f3',
        'Baixo': '#4caf50',
        'Moderado': '#ff9800',
        'Alto': '#f44336'
    }
    cor = cor_map.get(nivel_risco, '#999')
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pontuacao_total,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>Nível: {nivel_risco}</b>", 'font': {'size': 20}},
        number={'font': {'size': 50}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': cor},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#e3f2fd'},
                {'range': [25, 50], 'color': '#fff3e0'},
                {'range': [50, 75], 'color': '#ffebee'},
                {'range': [75, 100], 'color': '#ffcdd2'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def criar_tabela_dimensoes(resultado):
    """Cria tabela formatada com detalhes das dimensões"""
    df = pd.DataFrame({
        'Dimensão': list(resultado.pontuacoes_dimensoes.keys()),
        'Pontuação': [f"{v:.1f}" for v in resultado.pontuacoes_dimensoes.values()],
        'Nível de Risco': [resultado.niveis_risco_dimensoes[dim] 
                           for dim in resultado.pontuacoes_dimensoes.keys()]
    })
    
    # Ordena por pontuação (decrescente)
    df['Pont_Num'] = df['Pontuação'].astype(float)
    df = df.sort_values('Pont_Num', ascending=False)
    df = df.drop('Pont_Num', axis=1)
    
    return df


# ============================================================================
# FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO DE RESULTADOS
# ============================================================================

def renderizar_resultados(resultado, gerenciador):
    """
    Renderiza página completa de resultados com análises detalhadas
    
    Args:
        resultado: ResultadoAvaliacao
        gerenciador: GerenciadorAvaliacaoToxicidade
    """
    st.markdown("""
    <div class="fade-in">
        <h1 class="main-header">📊 Resultados da Avaliação</h1>
        <p class="sub-header">Análise Completa de Toxicidade em Liderança</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== SEÇÃO 1: PONTUAÇÃO GERAL ==========
    st.markdown("### 🎯 Pontuação Geral")
    
    col_gauge, col_metrics = st.columns([1, 1])
    
    with col_gauge:
        st.plotly_chart(
            criar_grafico_gauge(resultado.pontuacao_total, resultado.nivel_risco_geral),
            use_container_width=True
        )
    
    with col_metrics:
        classe_css = obter_classe_css_risco(resultado.nivel_risco_geral)
        st.markdown(f"""
        <div class='result-box {classe_css}' style='height: 250px; display: flex; flex-direction: column; justify-content: center;'>
            <h2 style='text-align: center; margin: 0;'>Pontuação Final</h2>
            <h1 style='text-align: center; font-size: 5rem; margin: 20px 0;'>{resultado.pontuacao_total:.1f}</h1>
            <h3 style='text-align: center; margin: 0;'>
                <span class='badge badge-{resultado.nivel_risco_geral.lower()}'>{resultado.nivel_risco_geral}</span>
            </h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== SEÇÃO 2: INTERPRETAÇÃO ==========
    st.markdown("### 📖 Interpretação dos Resultados")
    
    interpretacao = obter_interpretacao(resultado.nivel_risco_geral)
    
    if resultado.nivel_risco_geral == "Alto":
        st.markdown(f"""
        <div class="custom-alert alert-danger">
            <h4>⚠️ Situação Crítica Detectada</h4>
            <p>{interpretacao}</p>
        </div>
        """, unsafe_allow_html=True)
    elif resultado.nivel_risco_geral == "Moderado":
        st.markdown(f"""
        <div class="custom-alert alert-warning">
            <h4>⚠️ Atenção Necessária</h4>
            <p>{interpretacao}</p>
        </div>
        """, unsafe_allow_html=True)
    elif resultado.nivel_risco_geral == "Baixo":
        st.markdown(f"""
        <div class="custom-alert alert-success">
            <h4>✓ Situação Controlada</h4>
            <p>{interpretacao}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="custom-alert alert-info">
            <h4>✓ Excelente Ambiente</h4>
            <p>{interpretacao}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== SEÇÃO 3: ANÁLISE POR DIMENSÃO ==========
    st.markdown("### 📊 Análise Detalhada por Dimensão")
    
    tab_graficos, tab_tabela = st.tabs(["📈 Visualizações", "📋 Tabela Detalhada"])
    
    with tab_graficos:
        col_radar, col_barras = st.columns(2)
        
        with col_radar:
            st.plotly_chart(criar_grafico_radar(resultado), use_container_width=True)
        
        with col_barras:
            st.plotly_chart(criar_grafico_barras_horizontal(resultado), use_container_width=True)
    
    with tab_tabela:
        df_dimensoes = criar_tabela_dimensoes(resultado)
        st.dataframe(df_dimensoes, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ========== SEÇÃO 4: DIMENSÕES CRÍTICAS E POSITIVAS ==========
    col_criticas, col_positivas = st.columns(2)
    
    with col_criticas:
        st.markdown("### 🚨 Dimensões Mais Críticas")
        
        dimensoes_criticas = resultado.obter_dimensoes_criticas(limite=50)
        
        if dimensoes_criticas:
            for dimensao, pontuacao in dimensoes_criticas[:3]:
                nivel = resultado.niveis_risco_dimensoes[dimensao]
                classe = obter_classe_css_risco(nivel)
                st.markdown(f"""
                <div class='result-box {classe}'>
                    <h4>{dimensao}</h4>
                    <p><strong>Pontuação:</strong> {pontuacao:.1f} / 100</p>
                    <p><strong>Nível:</strong> <span class='badge badge-{nivel.lower()}'>{nivel}</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✓ Nenhuma dimensão crítica identificada!")
    
    with col_positivas:
        st.markdown("### ✨ Dimensões Mais Positivas")
        
        dimensoes_positivas = resultado.obter_dimensoes_positivas(limite=50)
        
        if dimensoes_positivas:
            for dimensao, pontuacao in dimensoes_positivas[:3]:
                nivel = resultado.niveis_risco_dimensoes[dimensao]
                classe = obter_classe_css_risco(nivel)
                st.markdown(f"""
                <div class='result-box {classe}'>
                    <h4>{dimensao}</h4>
                    <p><strong>Pontuação:</strong> {pontuacao:.1f} / 100</p>
                    <p><strong>Nível:</strong> <span class='badge badge-{nivel.lower()}'>{nivel}</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Todas as dimensões necessitam atenção.")
    
    st.markdown("---")
    
    # ========== SEÇÃO 5: RECOMENDAÇÕES ==========
    if resultado.recomendacoes:
        st.markdown("### 💡 Recomendações e Plano de Ação")
        
        for idx, recomendacao in enumerate(resultado.recomendacoes, 1):
            if recomendacao.strip():
                if "**" in recomendacao:
                    st.markdown(recomendacao)
                elif recomendacao.startswith("⚠️") or recomendacao.startswith("✓"):
                    st.markdown(f"""
                    <div class="recommendation-card">
                        {recomendacao}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"• {recomendacao}")
    
    st.markdown("---")
    
    # ========== SEÇÃO 6: AÇÕES E EXPORTAÇÃO ==========
    st.markdown("### 🎬 Próximas Ações")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Salvar Resultado", use_container_width=True, type="primary"):
            try:
                avaliacao_id = gerenciador.salvar_resultado(resultado)
                st.success(f"✅ Resultado salvo!\n\nID: `{avaliacao_id}`")
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {str(e)}")
    
    with col2:
        if st.button("📥 Exportar JSON", use_container_width=True):
            try:
                caminho = gerenciador.exportar_resultados(formato="json")
                st.success(f"✅ Exportado para:\n`{caminho}`")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    with col3:
        if st.button("📊 Exportar CSV", use_container_width=True):
            try:
                caminho = gerenciador.exportar_resultados(formato="csv")
                st.success(f"✅ Exportado para:\n`{caminho}`")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    with col4:
        if st.button("🔄 Nova Avaliação", use_container_width=True):
            st.session_state.respostas_toxicidade = {}
            st.session_state.avaliacao_completa = False
            st.session_state.resultado_atual = None
            st.session_state.dados_participante = {}
            st.rerun()


# ============================================================================
# FUNÇÃO DE RENDERIZAÇÃO DE HISTÓRICO
# ============================================================================

def renderizar_historico(gerenciador):
    """Renderiza página de histórico com estatísticas"""
    
    st.markdown("### 📚 Histórico de Avaliações")
    
    avaliacoes = gerenciador.listar_avaliacoes()
    
    if not avaliacoes:
        st.info("📭 Nenhuma avaliação registrada ainda.")
        st.markdown("""
        **Comece agora:**
        1. Vá para "Nova Avaliação"
        2. Responda o questionário
        3. Salve os resultados
        """)
        return
    
    # ========== ESTATÍSTICAS GERAIS ==========
    st.markdown("#### 📊 Visão Geral")
    
    stats = gerenciador.obter_estatisticas()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total</div>
            <div class="metric-value">{stats['total_avaliacoes']}</div>
            <small>avaliações realizadas</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Média Geral</div>
            <div class="metric-value">{stats['media_pontuacao_geral']:.1f}</div>
            <small>pontos</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        nivel_comum = max(stats['distribuicao_niveis_risco'].items(), key=lambda x: x[1])[0] if stats['distribuicao_niveis_risco'] else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Nível Mais Comum</div>
            <div class="metric-value" style="font-size: 1.5rem;">{nivel_comum}</div>
            <small>categoria predominante</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        dimensao_critica = stats['dimensoes_mais_criticas'][0][0] if stats['dimensoes_mais_criticas'] else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Dimensão Crítica</div>
            <div class="metric-value" style="font-size: 1.2rem;">{dimensao_critica[:15]}...</div>
            <small>maior pontuação média</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== LISTA DE AVALIAÇÕES ==========
    st.markdown("#### 📋 Lista de Avaliações")
    
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        filtro_nivel = st.selectbox(
            "Filtrar por Nível",
            ["Todos", "Excelente", "Baixo", "Moderado", "Alto"]
        )
    
    with col_filtro2:
        limite_exibir = st.slider("Número de resultados", 5, 50, 10)
    
    with col_filtro3:
        ordem = st.radio("Ordenar por", ["Mais Recente", "Mais Antigo", "Maior Pontuação", "Menor Pontuação"], horizontal=True)
    
    # Aplica filtros
    avaliacoes_filtradas = avaliacoes
    
    if filtro_nivel != "Todos":
        avaliacoes_filtradas = [a for a in avaliacoes if a['nivel_risco_geral'] == filtro_nivel]
    
    # Aplica ordenação
    if ordem == "Mais Recente":
        avaliacoes_filtradas = sorted(avaliacoes_filtradas, key=lambda x: x['timestamp'], reverse=True)
    elif ordem == "Mais Antigo":
        avaliacoes_filtradas = sorted(avaliacoes_filtradas, key=lambda x: x['timestamp'])
    elif ordem == "Maior Pontuação":
        avaliacoes_filtradas = sorted(avaliacoes_filtradas, key=lambda x: x['pontuacao_total'], reverse=True)
    else:
        avaliacoes_filtradas = sorted(avaliacoes_filtradas, key=lambda x: x['pontuacao_total'])
    
    # Limita quantidade
    avaliacoes_exibir = avaliacoes_filtradas[:limite_exibir]
    
    # Cria DataFrame
    if avaliacoes_exibir:
        df = pd.DataFrame([
            {
                'ID': a['id'][-8:],  # Últimos 8 caracteres
                'Data': pd.to_datetime(a['timestamp']).strftime('%d/%m/%Y %H:%M'),
                'Pontuação': f"{a['pontuacao_total']:.1f}",
                'Nível': a['nivel_risco_geral'],
                'Participante': a.get('dados_participante', {}).get('nome', 'Anônimo')[:20]
            }
            for a in avaliacoes_exibir
        ])
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.caption(f"Exibindo {len(avaliacoes_exibir)} de {len(avaliacoes_filtradas)} avaliações filtradas")
    else:
        st.info("Nenhuma avaliação corresponde aos filtros selecionados.")


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def obter_classe_css_risco(nivel_risco: str) -> str:
    """Retorna classe CSS baseada no nível de risco"""
    mapa = {
        'Excelente': 'risk-excellent',
        'Baixo': 'risk-low',
        'Moderado': 'risk-medium',
        'Alto': 'risk-high'
    }
    return mapa.get(nivel_risco, 'risk-low')


def renderizar_sobre():
    """Renderiza página Sobre"""
    st.markdown("""
    <div class="fade-in">
        <h1 class="main-header">📖 Sobre esta Ferramenta</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ## Sistema de Aferição de Toxidade em Lideranças
    
    **Desenvolvido por:** Projeto SER | Marcos Simões Bellini, CRP 04/37811
    
    ### 🎯 Objetivo
    
    Esta ferramenta foi desenvolvida para auxiliar organizações na identificação e mensuração 
    de comportamentos tóxicos em ambientes de liderança, contribuindo para:
    
    - 🏢 Ambientes de trabalho mais saudáveis
    - 📈 Maior produtividade e engajamento
    - 🤝 Melhor clima organizacional
    - 💪 Desenvolvimento de lideranças mais eficazes
    
    ### 📊 Dimensões Avaliadas
    
    O questionário avalia **8 dimensões fundamentais** de toxicidade:
    
    1. **🗣️ Comunicação e Feedback** - Qualidade e clareza da comunicação
    2. **🏆 Reconhecimento e Valorização** - Reconhecimento de esforços e resultados
    3. **⚖️ Equidade e Justiça** - Tratamento justo e imparcial
    4. **🤝 Confiança e Transparência** - Honestidade e confiabilidade
    5. **💪 Empoderamento e Autonomia** - Delegação e confiança na equipe
    6. **😰 Pressão e Estresse** - Gestão de prazos e pressões
    7. **👁️ Respeito e Dignidade** - Tratamento respeitoso
    8. **🎯 Expectativas e Clareza** - Clareza de objetivos e expectativas
    
    ### 📈 Interpretação dos Resultados
    
    Os resultados são classificados em **4 níveis de risco**:
    
    #### 🟦 Excelente (0-24 pontos)
    - Liderança exemplar e saudável
    - Ambiente positivo e motivador
    - Manter e fortalecer práticas atuais
    
    #### 🟩 Baixo (25-49 pontos)
    - Situação aceitável com pontos de atenção
    - Monitoramento regular recomendado
    - Algumas melhorias podem ser implementadas
    
    #### 🟨 Moderado (50-74 pontos)
    - Sinais significativos de toxicidade
    - Requer avaliação aprofundada
    - Plano de ação corretivo necessário
    
    #### 🟥 Alto (75-100 pontos)
    - Situação crítica
    - Intervenção imediata necessária
    - Suporte do RH e profissionais especializados
    
    ### 🔒 Confidencialidade
    
    - Todas as respostas são tratadas com **confidencialidade**
    - Dados utilizados apenas para **diagnóstico organizacional**
    - Resultados apresentados de forma **agregada e anônima**
    - Conformidade com **LGPD** (Lei Geral de Proteção de Dados)
    
    ### 📱 Recursos da Ferramenta
    
    - ✅ Questionário completo com 40+ questões
    - 📊 Visualizações interativas dos resultados
    - 💾 Salvamento e histórico de avaliações
    - 📥 Exportação de dados (JSON, CSV)
    - 📈 Estatísticas e análises comparativas
    - 💡 Recomendações personalizadas
    
    ### 🎓 Base Científica
    
    Esta ferramenta foi desenvolvida com base em:
    
    - Literatura científica sobre liderança tóxica
    - Melhores práticas de RH
    - Experiência clínica em psicologia organizacional
    - Feedback de profissionais de RH
    
    ### 📞 Contato e Suporte
    
    **Projeto SER**  
    Marcos Simões Bellini, CRP 04/37811  
    
    Para dúvidas, sugestões ou suporte técnico, entre em contato através dos canais oficiais.
    
    ---
    
    **Versão:** 1.0  
    **Última Atualização:** Novembro 2025  
    **Licença:** Proprietária - Todos os direitos reservados
    """)


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal da aplicação"""
    
    # Inicializa session state
    inicializar_session_state()
    
    # Cria questionário e gerenciador
    questionario = criar_questionario_toxicidade()
    gerenciador = GerenciadorAvaliacaoToxicidade(questionario)
    
    # ========== SIDEBAR ==========
    with st.sidebar:
        st.markdown("## 🧭 Toxicidade em Lideranças")
        st.markdown("---")
        
        # Navegação
        pagina = st.radio(
            "**Navegação**",
            ["Nova Avaliação", "Histórico", "Sobre"],
            key="navegacao_principal"
        )
        
        st.markdown("---")
        
        # Progresso (apenas na página de avaliação)
        if pagina == "Nova Avaliação" and not st.session_state.avaliacao_completa:
            st.markdown("### 📊 Progresso")
            
            total_questoes = len(questionario)
            respondidas = len(st.session_state.respostas_toxicidade)
            progresso = (respondidas / total_questoes) * 100
            
            st.markdown(f"""
            <div class="custom-progress">
                <div class="custom-progress-bar" style="width: {progresso}%">
                    {int(progresso)}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <p style="text-align: center; margin-top: 10px;">
                <strong>{respondidas}</strong> de <strong>{total_questoes}</strong> questões
            </p>
            """, unsafe_allow_html=True)
            
            if respondidas < total_questoes:
                st.warning(f"⚠️ Faltam {total_questoes - respondidas} questões")
            else:
                st.success("✅ Todas as questões respondidas!")
        
        # Informações adicionais
        with st.expander("ℹ️ Informações"):
            st.markdown("""
            **Versão:** 1.0  
            **Total de Dimensões:** 8  
            **Total de Questões:** 40+  
            **Tempo Médio:** 10-15 min  
            
            ---
            
            **Projeto SER**  
            Marcos Simões Bellini  
            CRP 04/37811
            """)
    
    # ========== CONTEÚDO PRINCIPAL ==========
    
    if pagina == "Nova Avaliação":
        if not st.session_state.avaliacao_completa:
            # Renderiza questionário
            renderizar_questionario(questionario)
            
            # Botão de envio
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                total_questoes = len(questionario)
                respondidas = len(st.session_state.respostas_toxicidade)
                
                if respondidas < total_questoes:
                    st.warning(f"⚠️ Complete todas as {total_questoes - respondidas} questões restantes")
                    enviar_disabled = True
                else:
                    enviar_disabled = False
                
                if st.button(
                    "✅ ENVIAR AVALIAÇÃO",
                    use_container_width=True,
                    disabled=enviar_disabled,
                    type="primary"
                ):
                    with st.spinner("🔄 Processando sua avaliação..."):
                        try:
                            # Valida
                            valido, erros = gerenciador.validar_respostas(
                                st.session_state.respostas_toxicidade
                            )
                            
                            if not valido:
                                st.error(f"❌ Erro na validação:\n{chr(10).join(erros)}")
                            else:
                                # Processa
                                resultado = gerenciador.processar_avaliacao(
                                    st.session_state.respostas_toxicidade,
                                    st.session_state.dados_participante
                                )
                                
                                st.session_state.resultado_atual = resultado
                                st.session_state.avaliacao_completa = True
                                
                                st.success("✅ Avaliação processada com sucesso!")
                                st.balloons()
                                
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao processar: {str(e)}")
        
        else:
            # Mostra resultados
            if st.session_state.resultado_atual:
                renderizar_resultados(st.session_state.resultado_atual, gerenciador)
    
    elif pagina == "Histórico":
        renderizar_historico(gerenciador)
    
    elif pagina == "Sobre":
        renderizar_sobre()


def render_footer():
    """Renderiza rodapé"""
    st.markdown("""
    <div class="footer">
        <p><strong>Sistema de Aferição de Toxidade em Lideranças</strong></p>
        <p>Projeto SER | Marcos Simões Bellini, CRP 04/37811</p>
        <p>© 2025 - Todos os direitos reservados</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    main()
    render_footer()