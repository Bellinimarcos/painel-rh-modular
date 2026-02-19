import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def render_analysis_timeline(analyses):
    """Mostra uma linha do tempo simples das análises por dia."""
    st.subheader("🗓️ Linha do tempo")

    if not analyses:
        st.info("Sem dados para timeline.")
        return

    rows = []
    for a in analyses:
        rows.append({
            "data": a.timestamp.date(),
            "tipo": a.type.value if a.type else "N/A",
            "nome": a.name
        })

    df = pd.DataFrame(rows)
    df["contagem"] = 1
    df_group = df.groupby("data", as_index=False)["contagem"].sum()

    fig = px.bar(df_group, x="data", y="contagem", title="Análises por dia")
    st.plotly_chart(fig, use_container_width=True)


def render_analysis_distribution(analyses):
    """Mostra a distribuição por tipo de análise."""
    st.subheader("📦 Distribuição por ferramenta")

    if not analyses:
        st.info("Sem dados para distribuição.")
        return

    rows = []
    for a in analyses:
        rows.append({
            "tipo": a.type.value if a.type else "N/A"
        })

    df = pd.DataFrame(rows)
    df_group = df.groupby("tipo", as_index=False).size()
    df_group.columns = ["tipo", "contagem"]

    fig = px.pie(df_group, names="tipo", values="contagem", title="Distribuição por tipo")
    st.plotly_chart(fig, use_container_width=True)
