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

# --- INÍCIO DA ADIO ---
from .copsoq_ii_model import CopsoqII
# --- FIM DA ADIO ---


__all__ = [
    'QuestionarioToxicidade',
    'Dimensao',
    'Questao',
    'TipoQuestao',
    'RespostaAvaliacao',
    'ResultadoAvaliacao',
    
    # --- INÍCIO DA ADIO ---
    'CopsoqII'
    # --- FIM DA ADIO ---
]


