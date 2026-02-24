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
from utils.visualizations import render_analysis_timeline, render_analysis_distribution

# =========================
# CONFIGURAÇÃO DE LIMIARES
# =========================
# Faixas (COPSOQ, 0-100): Verde >= 60 | Amarelo 40-59.9 | Vermelho < 40
COPSOQ_RED = 40.0
COPSOQ_YELLOW = 60.0

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title=f"Hub Compliance RPS - v{AppConfig.APP_VERSION}",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# HELPERS
# =========================
def setup_session():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.latest_analysis = None

def verify_api_key():
    if not AppConfig.GEMINI_API_KEY:
        st.sidebar.warning("⚠️ Co-piloto Offline: Configure a API Key")
        return False
    return True

def _safe_label(risk_level):
    """Compatível com RiskLevel enum (label/emoji) ou string."""
    try:
        if risk_level is None:
            return ""
        if hasattr(risk_level, "label"):
            return str(risk_level.label)
        return str(risk_level)
    except Exception:
        return ""

def is_copsoq_analysis(a):
    """Detecta se é COPSOQ pelo type.value (ex.: 'COPSOQ_III') ou pelo nome."""
    try:
        t = getattr(a, "type", None)
        tv = getattr(t, "value", "")
        name = getattr(a, "name", "") or ""
        tv = str(tv).lower()
        name = str(name).lower()
        return ("copsoq" in tv) or ("copsoq" in name)
    except Exception:
        return False

def copsoq_risk_summary(a):
    """
    Retorna:
      - overall: "RED" | "YELLOW" | "GREEN"
      - counts: dict com qtd por faixa
      - worst: (dim, score)
      - critical_list: lista de (dim, score, faixa) ordenada do pior ao melhor (limitado)
    """
    if not isinstance(getattr(a, "data", None), dict) or not a.data:
        return "GREEN", {"RED": 0, "YELLOW": 0, "GREEN": 0}, (None, None), []

    numeric_items = [(k, v) for k, v in a.data.items() if isinstance(v, (int, float))]
    if not numeric_items:
        return "GREEN", {"RED": 0, "YELLOW": 0, "GREEN": 0}, (None, None), []

    def faixa(score: float) -> str:
        if score < COPSOQ_RED:
            return "RED"
        if score < COPSOQ_YELLOW:
            return "YELLOW"
        return "GREEN"

    counts = {"RED": 0, "YELLOW": 0, "GREEN": 0}
    tagged = []
    for k, v in numeric_items:
        s = float(v)
        f = faixa(s)
        counts[f] += 1
        tagged.append((k, s, f))

    tagged_sorted = sorted(tagged, key=lambda x: x[1])  # menor = pior
    worst_dim, worst_val, worst_band = tagged_sorted[0]

    if counts["RED"] > 0:
        overall = "RED"
    elif counts["YELLOW"] > 0:
        overall = "YELLOW"
    else:
        overall = "GREEN"

    critical_list = tagged_sorted[:8]  # top 8 para explicar/IA
    return overall, counts, (worst_dim, worst_val), critical_list

def analysis_risk_flag(a):
    """
    Retorna:
      (flag_alerta: bool, status: "RED|YELLOW|GREEN", reason: str, critical_list: list)
    """
    label = _safe_label(getattr(a, "risk_level", None)).lower()

    # Se seu risk_level já vier alto/crítico, mantém como RED por segurança
    if label in ["alto", "crítico", "critico"]:
        return True, "RED", "Risco geral alto/crítico", []

    if is_copsoq_analysis(a):
        overall, counts, worst, critical_list = copsoq_risk_summary(a)
        worst_dim, worst_val = worst

        if overall == "RED":
            return True, "RED", f"COPSOQ: {worst_dim}={worst_val:.1f} (vermelho)", critical_list
        if overall == "YELLOW":
            return True, "YELLOW", f"COPSOQ: {worst_dim}={worst_val:.1f} (amarelo)", critical_list

        return False, "GREEN", "Sem alertas (verde)", critical_list

    return False, "GREEN", "Sem alertas", []

# =========================
# BARRA LATERAL (BRANDING)
# =========================
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

        try:
            total = len(storage.get_analyses())
        except Exception:
            total = 0
        st.metric("Base de Dados", f"{total} Análises")

        st.markdown("### ⚙️ Administração")
        render_backup_interface()

        st.divider()
        st.toggle("🐞 Debug Mode", key="debug_mode")

        if st.button("🗑️ Resetar Base de Dados", key="btn_reset_db", use_container_width=True):
            if st.checkbox("Confirmar exclusão permanente", key="chk_confirm_reset"):
                storage.clear_all()
                st.session_state.clear()
                st.rerun()

# =========================
# COMPONENTES DE VISUALIZAÇÃO
# =========================
def render_metrics_overview(analyses):
    st.subheader("📊 Indicadores Estratégicos")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Volume de Dados", len(analyses), help="Total de diagnósticos processados")

    with col2:
        recent = [a for a in analyses if (datetime.now() - a.timestamp).days <= 7]
        st.metric("Atividade Semanal", len(recent), delta=f"{len(recent)} novos")

    with col3:
        red = 0
        yellow = 0
        explanations = []

        for a in analyses:
            flag, status, reason, _critical_list = analysis_risk_flag(a)
            if status == "RED":
                red += 1
            elif status == "YELLOW":
                yellow += 1

            if flag:
                explanations.append(f"- {a.name}: {reason}")

        total_alerts = red + yellow
        if red > 0:
            status_msg = "🚨 Vermelho: ação imediata"
        elif yellow > 0:
            status_msg = "⚠️ Amarelo: atenção e monitorar"
        else:
            status_msg = "✅ Verde: ambiente estável"

        st.metric(
            "Status de Risco",
            f"{total_alerts} Alertas",
            delta=status_msg,
            delta_color="inverse" if total_alerts else "normal"
        )

        if st.session_state.get("debug_mode") and explanations:
            with st.expander("🐞 Debug Alertas (por quê?)"):
                st.markdown("\n".join(explanations))

    with col4:
        unique_tools = len(set(getattr(a.type, "value", str(a.type)) for a in analyses))
        st.metric("Ferramentas", unique_tools, help="Diversidade de inventários aplicados")

def render_analysis_details(analysis):
    st.write(f"**📅 Data da Coleta:** {analysis.timestamp.strftime('%d/%m/%Y %H:%M')}")
    st.write(f"**🔬 Metodologia:** {analysis.type.value}")

    if analysis.risk_level:
        st.markdown(f"**Nível de Risco (geral):** {analysis.risk_level.emoji} `{analysis.risk_level.label.upper()}`")

    st.divider()

    # Resumo COPSOQ com cores e "por quê"
    if is_copsoq_analysis(analysis):
        overall, counts, worst, critical_list = copsoq_risk_summary(analysis)
        badge = {"RED": "🔴 Vermelho", "YELLOW": "🟡 Amarelo", "GREEN": "🟢 Verde"}[overall]
        st.markdown(f"### {badge} — Resumo COPSOQ")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dimensões Vermelhas", counts["RED"])
        c2.metric("Dimensões Amarelas", counts["YELLOW"])
        c3.metric("Dimensões Verdes", counts["GREEN"])

        st.markdown("**🎯 Principais riscos (pior → melhor):**")
        for dim, score, band in critical_list:
            icon = "🔴" if band == "RED" else "🟡" if band == "YELLOW" else "🟢"
            st.write(f"{icon} **{dim}**: {score:.1f}")

        st.divider()

    # Exibição de Scores (cards)
    st.markdown("**📈 Dimensões Processadas:**")
    items = list(analysis.data.items()) if isinstance(analysis.data, dict) else []
    numeric_items = [(k, v) for k, v in items if isinstance(v, (int, float))]
    cols = st.columns(3)
    for idx, (key, value) in enumerate(numeric_items):
        with cols[idx % 3]:
            st.metric(key, f"{float(value):.1f}")

    if analysis.metadata and 'ai_detailed_analysis' in analysis.metadata:
        st.divider()
        st.markdown("### 🤖 Parecer do Co-piloto IA")
        st.info(analysis.metadata['ai_detailed_analysis'])

# =========================
# HEADER E EXECUÇÃO
# =========================
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
        render_analysis_timeline(analyses)
    with col_t2:
        render_analysis_distribution(analyses)

    st.divider()
    st.subheader("🕒 Histórico de Diagnósticos")
    for a in sorted(analyses, key=lambda x: x.timestamp, reverse=True)[:10]:
        icon = "📊"
        try:
            # Ícone baseado no risco COPSOQ (mais explicável)
            if is_copsoq_analysis(a):
                overall, _, _, _ = copsoq_risk_summary(a)
                icon = "🔴" if overall == "RED" else "🟡" if overall == "YELLOW" else "🟢"
            elif a.risk_level:
                icon = a.risk_level.emoji
        except Exception:
            pass

        with st.expander(f"{icon} {a.name} - {a.timestamp.strftime('%d/%m/%Y')}"):
            render_analysis_details(a)
