# C:\painel_rh_modular\logic\copsoq_ii_logic.py

import sys
import os
import pandas as pd
from typing import Dict, Any, List, Tuple

# --- INÍCIO DA CORREO DE IMPORTAO ---
current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)
# --- FIM DA CORREO ---

from models.copsoq_ii_model import CopsoqII

# --- CONSTANTES DE PONTUAO ---

# Mapeamento das dimensões para as suas respectivas questões no modelo
# Formato: (nome_da_questao, reverter_pontuacao, min_escala, max_escala)
# Reverter=True significa que 5 é 'bom' e 1 é 'ruim' (ex: Influência)
# Reverter=False significa que 5 é 'ruim' e 1 é 'bom' (ex: Carga de Trabalho)

DIMENSOES_MAP = {
    # Exigências Laborais
    "Exigências Quantitativas": [
        ('q1', False, 1, 5), ('q2', False, 1, 5), ('q3', False, 1, 5)
    ],
    "Exigências Cognitivas": [
        ('q4', False, 1, 5), ('q5', False, 1, 5)
    ],
    "Exigências Emocionais": [
        ('q6', False, 1, 5)
    ],
    # Organização do Trabalho e Conteúdo
    "Influência e Desenvolvimento": [
        ('q7', True, 1, 5), ('q8', True, 1, 5), ('q9', True, 1, 5)
    ],
    "Significado e Propósito": [
        ('q24', True, 1, 5), ('q25', True, 1, 5) # (Escala 1-5 'Nada/quase nada' a 'Extremamente')
    ],
    "Clareza de Papel": [
        ('q10', True, 1, 5), ('q11', True, 1, 5), ('q12', True, 1, 5)
    ],
    # Relações Sociais e Liderança
    "Reconhecimento e Justiça": [
        ('q13', True, 1, 5), ('q14', True, 1, 5), ('q21', True, 1, 5), ('q22', True, 1, 5)
    ],
    "Qualidade da Liderança": [
        ('q15', True, 1, 5), ('q17', True, 1, 5), ('q18', True, 1, 5)
    ],
    "Apoio Social (Colegas)": [
        ('q16', True, 1, 5)
    ],
    "Confiança": [
        ('q19', True, 1, 5), ('q20', True, 1, 5)
    ],
    "Autoeficácia": [
        ('q23', True, 1, 5)
    ],
    # Interface Trabalho-Indivíduo
    "Satisfação com o Trabalho": [
        ('q27', True, 1, 5) # (Escala 'Nada/quase nada')
    ],
    "Comprometimento Afetivo": [
        ('q26', True, 1, 5) # (Escala 'Nada/quase nada')
    ],
    "Insegurança no Trabalho": [
        ('q28', False, 1, 5) # (Escala 'Nada/quase nada')
    ],
    "Conflito Trabalho-Família": [
        ('q30', False, 1, 5), ('q31', False, 1, 5) # (Escala 'Nada/quase nada')
    ],
    # Saúde e Bem-Estar (Sintomas)
    "Distúrbios do Sono": [
        ('q32', False, 1, 5)
    ],
    "Exaustão Física e Emocional (Burnout)": [
        ('q33', False, 1, 5), ('q34', False, 1, 5)
    ],
    "Sintomas de Estresse (Ansiedade/Irritação)": [
        ('q35', False, 1, 5), ('q36', False, 1, 5)
    ],
    "Sintomas Depressivos": [
        ('q37', False, 1, 5)
    ],
    # Comportamentos Ofensivos
    "Assédio Moral (Provocações/Insultos)": [
        ('q38', False, 1, 5)
    ],
    "Assédio Sexual": [
        ('q39', False, 1, 5)
    ],
    "Ameaças e Violência": [
        ('q40', False, 1, 5), ('q41', False, 1, 5)
    ]
}


def normalizar_pontuacao(valor: int, min_escala: int, max_escala: int, reverter: bool = False) -> float:
    """
    Normaliza uma pontuação da escala Likert (1-5) para uma escala de risco (0-100).
    0 = Risco Mínimo (Melhor)
    100 = Risco Máximo (Pior)
    """
    if valor is None:
        return None

    if reverter:
        # Se 5 é 'bom' e 1 é 'ruim' (ex: Influência)
        # (5 - valor) / (5 - 1) * 100
        pontuacao = ((max_escala - valor) / (max_escala - min_escala)) * 100
    else:
        # Se 5 é 'ruim' e 1 é 'bom' (ex: Carga de Trabalho)
        # (valor - 1) / (5 - 1) * 100
        pontuacao = ((valor - min_escala) / (max_escala - min_escala)) * 100
    
    return round(pontuacao)

def get_cor_risco(pontuacao: float) -> str:
    """
    Retorna a cor do semáforo com base na pontuação 0-100.
    """
    if pontuacao is None:
        return "N/A"
    if pontuacao <= 33:
        return "Verde"
    elif pontuacao <= 66:
        return "Amarelo"
    else:
        return "Vermelho"

def calcular_pontuacao_copsoq_ii(respostas: CopsoqII) -> pd.DataFrame:
    """
    Processa as respostas validadas do COPSOQ II e retorna um DataFrame
    com as pontuações 0-100 e as cores de risco.
    """
    
    resultados = []
    respostas_dict = respostas.model_dump()

    for dimensao, questoes in DIMENSOES_MAP.items():
        pontuacoes_norm = []
        for q_id, reverter, min_escala, max_escala in questoes:
            valor_bruto = respostas_dict.get(q_id)
            if valor_bruto is not None:
                pontuacoes_norm.append(
                    normalizar_pontuacao(valor_bruto, min_escala, max_escala, reverter)
                )
        
        # Calcula a pontuação final da dimensão (média das questões)
        if pontuacoes_norm:
            pontuacao_final = round(sum(pontuacoes_norm) / len(pontuacoes_norm))
        else:
            pontuacao_final = None
            
        resultados.append({
            "Dimensão": dimensao,
            "Pontuação (0-100)": pontuacao_final,
            "Nível de Risco": get_cor_risco(pontuacao_final)
        })

    # Adicionar a questão de saúde (Q29), que é nominal
    resultados.append({
        "Dimensão": "Saúde Geral Percebida",
        "Pontuação (0-100)": respostas.q29, # Armazena o texto
        "Nível de Risco": "N/A" # Não se aplica semáforo aqui
    })

    return pd.DataFrame(resultados)


