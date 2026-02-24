# components/ui_components.py
# Responsabilidade: Agrupar funções que criam elementos visuais reutilizáveis.

import streamlit as st
from typing import Any, Optional

class UIComponents:
    """
    Classe estática para agrupar funções que renderizam componentes de UI.
    Isto ajuda a manter a consistência visual em toda a aplicação.
    """

    @staticmethod
    def render_header(title: str, subtitle: Optional[str] = None):
        """Renderiza o cabeçalho padrão da página."""
        header_html = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem;">
            <h1 style="color: white; margin: 0;">{title}</h1>
            {f'<p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ''}
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)

    @staticmethod
    def render_metric_card(label: str, value: Any, delta: Optional[str] = None, color: str = "#1E3A8A", icon: str = "", help_text: str = ""):
        """Renderiza um cartão de métrica com ícone e formatação."""
        # CORREO: Usar st.metric em vez de HTML personalizado
        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color="normal" if not delta or not delta.startswith('-') else "inverse"
        )


