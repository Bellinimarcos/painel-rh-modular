# C:\painel_rh_modular\models\__init__.py

"""
Módulo de modelos de dados do Painel RH Modular
"""

from .toxicidade_model import (
    QuestionarioToxicidade,
    Dimensao,
    Questao,
    TipoQuestao,
    RespostaAvaliacao,
    ResultadoAvaliacao
)

# --- INÍCIO DA ADIÇÃO ---
from .copsoq_ii_model import CopsoqII
# --- FIM DA ADIÇÃO ---


__all__ = [
    'QuestionarioToxicidade',
    'Dimensao',
    'Questao',
    'TipoQuestao',
    'RespostaAvaliacao',
    'ResultadoAvaliacao',
    
    # --- INÍCIO DA ADIÇÃO ---
    'CopsoqII'
    # --- FIM DA ADIÇÃO ---
]