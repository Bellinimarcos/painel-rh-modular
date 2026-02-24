# C:\painel_rh_modular\pages\3_AEP_COPSOQ_II.py

import streamlit as st
import sys
import os
import pandas as pd

# --- INÍCIO DA CORREO DE IMPORTAO ---
current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)
# --- FIM DA CORREO ---

from models import CopsoqII
from logic.copsoq_ii_logic import calcular_pontuacao_copsoq_ii, get_cor_risco

st.set_page_config(layout="wide", page_title="COPSOQ II - AEP")

# --- Definição das Escalas (CORRIGIDAS) ---
ESCALA_FREQUENCIA_1 = ["Nunca/ quase nunca", "Raramente", "s vezes", "Frequentemente", "Sempre"]
ESCALA_FREQUENCIA_2 = ["Nunca/ quase nunca", "Raramente", "s vezes", "Frequentemente", "Sempre"]
ESCALA_INTENSIDADE_1 = ["Nada/ quase nada", "Um pouco", "Moderadamente", "Muito", "Extremamente"]
ESCALA_SAUDE = ["Excelente", "Muito boa", "Boa", "Razoável", "Deficitária"] # Corrigido
ESCALA_INTENSIDADE_2 = ["Nada/ quase nada", "Um pouco", "Moderadamente", "Muito", "Extremamente"] # Corrigido
ESCALA_FREQUENCIA_3 = ["Nunca/ quase nunca", "Raramente", "s vezes", "Frequentemente", "Sempre"]
ESCALA_FREQUENCIA_4 = ["Nunca/quase nunca", "Raramente", "s vezes", "Frequentemente", "Sempre"]

# Mapeamento de texto para valor numérico (1-5)
map_freq_1 = {k: i+1 for i, k in enumerate(ESCALA_FREQUENCIA_1)}
map_freq_2 = {k: i+1 for i, k in enumerate(ESCALA_FREQUENCIA_2)}
map_int_1 = {k: i+1 for i, k in enumerate(ESCALA_INTENSIDADE_1)}
map_int_2 = {k: i+1 for i, k in enumerate(ESCALA_INTENSIDADE_2)}
map_freq_3 = {k: i+1 for i, k in enumerate(ESCALA_FREQUENCIA_3)}
map_freq_4 = {k: i+1 for i, k in enumerate(ESCALA_FREQUENCIA_4)}

# --- FUNO PARA COLORIR O SEMÁFORO ---
def colorir_risco(val):
    cor = 'black' # Cor padrão
    if val == "Verde":
        cor = 'green'
    elif val == "Amarelo":
        cor = 'orange'
    elif val == "Vermelho":
        cor = 'red'
    return f'color: {cor}; font-weight: bold;'

# --- PÁGINA PRINCIPAL ---
def render_form():
    st.title("COPSOQ II - Versão Curta")
    st.caption("Readaptação para o português brasileiro e uso em Avaliação Ergonômica Preliminar de Magalhães, A. et al., 2024")
    st.info("Por favor, avalie sua situação de trabalho respondendo às seguintes questões.")

    with st.form("form_copsoq_ii"):
        respostas = {}
        
        # --- Bloco 1 ---
        st.subheader("Critério: exigências laborais/organização do trabalho e conteúdo")
        st.caption("Escala: 1- Nunca/ quase nunca, 2- Raramente, 3- s vezes, 4- Frequentemente, 5- Sempre")
        
        q_text = [
            "1. A sua carga de trabalho acumula-se por ser mal distribuída?",
            "2. Com que frequência não tem tempo para completar todas as tarefas do seu trabalho?",
            "3. Precisa trabalhar muito rapidamente?",
            "4. O seu trabalho exige a sua atenção constante?",
            "5. O seu trabalho exige que tome decisões difíceis?",
            "6. O seu trabalho exige emocionalmente de si?",
            "7. Tem um elevado grau de influência no seu trabalho?",
            "8. O seu trabalho exige que tenha iniciativa?",
            "9. O seu trabalho permite-lhe aprender coisas novas?",
            "10. No seu local de trabalho, é informado com antecedência sobre decisões importantes, mudanças ou planos para o futuro?",
            "11. Recebe toda a informação de que necessita para fazer bem o seu trabalho?",
            "12. Sabe exatamente quais as suas responsabilidades?",
            "13. O seu trabalho é reconhecido e apreciado pela gerência?",
            "14.  tratado de forma justa no seu local de trabalho?",
            "15. Com que frequência tem ajuda e apoio do seu superior imediato?",
            "16. Existe um bom ambiente de trabalho entre si e os seus colegas?"
        ] 
        
        for i, q in enumerate(q_text, 1):
            respostas[f'q{i}'] = st.radio(q, options=ESCALA_FREQUENCIA_1, index=None, horizontal=True)

        # --- Bloco 2 ---
        st.subheader("Critério: relações sociais e liderança")
        st.caption("Em relação à sua chefia direta... Escala: 1- Nunca/ quase nunca, 2- Raramente, 3- s vezes, 4- Frequentemente, 5- Sempre")

        q_text_2 = [
            "17. Oferece aos indivíduos e ao grupo boas oportunidades de desenvolvimento?",
            "18.  bom no planejamento do trabalho?",
            "19. A gerência confia nos seus funcionários para fazerem o seu trabalho bem?",
            "20. Confia na informação que lhe é transmitida pela gerência?",
            "21. Os conflitos são resolvidos de uma forma justa?",
            "22. O trabalho é igualmente distribuído pelos funcionários?",
            "23. Sou sempre capaz de resolver problemas, se tentar o suficiente."
        ] 
        
        for i, q in enumerate(q_text_2, 17):
            respostas[f'q{i}'] = st.radio(q, options=ESCALA_FREQUENCIA_2, index=None, horizontal=True)

        # --- Bloco 3 ---
        st.subheader("Critério: interface trabalho-indivíduo")
        st.caption("Escala: 1- Nada/ quase nada, 2- Um pouco, 3- Moderadamente, 4- Muito, 5- Extremamente")
        
        q_text_3 = [
            "24. O seu trabalho tem algum significado para si?",
            "25. Sente que o seu trabalho é importante?",
            "26. Sente que os problemas do seu local de trabalho são seus também?",
            "27. Quão satisfeito está com o seu trabalho de uma forma global?",
            "28. Sente-se preocupado em ficar desempregado?"
        ] 
        
        for i, q in enumerate(q_text_3, 24):
            respostas[f'q{i}'] = st.radio(q, options=ESCALA_INTENSIDADE_1, index=None, horizontal=True)

        # --- Bloco 4 ---
        st.subheader("Critério: saúde geral")
        respostas['q29'] = st.radio(
            "29.Em geral, sente que a sua saúde é:",
            options=ESCALA_SAUDE, index=None, horizontal=True
        )

        # --- Bloco 5 ---
        st.subheader("Critério: conflito trabalho/família")
        st.caption("Escala: 1- Nada/ quase nada, 2- Um pouco, 3- Moderadamente, 4- Muito, 5- Extremamente")
        
        q_text_5 = [
            "30. Sente que o seu trabalho lhe exige muita energia que acaba por afetar a sua vida privada negativamente?",
            "31. Sente que o seu trabalho lhe exige muito tempo que acaba por afetar a sua vida privada negativamente?"
        ]
        
        for i, q in enumerate(q_text_5, 30):
            respostas[f'q{i}'] = st.radio(q, options=ESCALA_INTENSIDADE_2, index=None, horizontal=True)

        # --- Bloco 6 ---
        st.subheader("Critério: saúde e bem-estar")
        st.caption("Com que frequência durante as últimas 4 semanas sentiu... Escala: 1- Nunca/ quase nunca, 2- Raramente, 3- s vezes, 4- Frequentemente, 5- Sempre")

        q_text_6 = [
            "32. Acordou várias vezes durante a noite e depois não conseguia adormecer novamente?",
            "33. Fisicamente exausto?",
            "34. Emocionalmente exausto?",
            "35. Irritado?",
            "36. Ansioso?",
            "37. Triste?"
        ] 
        
        for i, q in enumerate(q_text_6, 32):
            respostas[f'q{i}'] = st.radio(q, options=ESCALA_FREQUENCIA_3, index=None, horizontal=True)

        # --- Bloco 7 ---
        st.subheader("Critério: comportamentos ofensivos")
        st.caption("Nos últimos 12 meses, no seu local de trabalho... Escala: 1- Nunca/quase nunca, 2- Raramente, 3- s vezes, 4- Frequentemente, 5- Sempre")

        q_text_7 = [
            "38. Tem sido alvo de insultos ou provocações verbais?",
            "39. Tem sido exposto a assédio sexual indesejado?",
            "40. Tem sido exposto a ameaças de violência?",
            "41. Tem sido exposto a violência física?"
        ] 
        
        for i, q in enumerate(q_text_7, 38):
            respostas[f'q{i}'] = st.radio(q, options=ESCALA_FREQUENCIA_4, index=None, horizontal=True)

        # --- Submissão ---
        st.divider()
        submitted = st.form_submit_button("Enviar Respostas")

    if submitted:
        try:
            # --- MAPEAMENTO (igual ao anterior) ---
            respostas_numericas = {
                'q1': map_freq_1.get(respostas['q1']), 'q2': map_freq_1.get(respostas['q2']),
                'q3': map_freq_1.get(respostas['q3']), 'q4': map_freq_1.get(respostas['q4']),
                'q5': map_freq_1.get(respostas['q5']), 'q6': map_freq_1.get(respostas['q6']),
                'q7': map_freq_1.get(respostas['q7']), 'q8': map_freq_1.get(respostas['q8']),
                'q9': map_freq_1.get(respostas['q9']), 'q10': map_freq_1.get(respostas['q10']),
                'q11': map_freq_1.get(respostas['q11']), 'q12': map_freq_1.get(respostas['q12']),
                'q13': map_freq_1.get(respostas['q13']), 'q14': map_freq_1.get(respostas['q14']),
                'q15': map_freq_1.get(respostas['q15']), 'q16': map_freq_1.get(respostas['q16']),
                'q17': map_freq_2.get(respostas['q17']), 'q18': map_freq_2.get(respostas['q18']),
                'q19': map_freq_2.get(respostas['q19']), 'q20': map_freq_2.get(respostas['q20']),
                'q21': map_freq_2.get(respostas['q21']), 'q22': map_freq_2.get(respostas['q22']),
                'q23': map_freq_2.get(respostas['q23']), 'q24': map_int_1.get(respostas['q24']),
                'q25': map_int_1.get(respostas['q25']), 'q26': map_int_1.get(respostas['q26']),
                'q27': map_int_1.get(respostas['q27']), 'q28': map_int_1.get(respostas['q28']),
                'q29': respostas['q29'], 
                'q30': map_int_2.get(respostas['q30']), 'q31': map_int_2.get(respostas['q31']),
                'q32': map_freq_3.get(respostas['q32']), 'q33': map_freq_3.get(respostas['q33']),
                'q34': map_freq_3.get(respostas['q34']), 'q35': map_freq_3.get(respostas['q35']),
                'q36': map_freq_3.get(respostas['q36']), 'q37': map_freq_3.get(respostas['q37']),
                'q38': map_freq_4.get(respostas['q38']), 'q39': map_freq_4.get(respostas['q39']),
                'q40': map_freq_4.get(respostas['q40']), 'q41': map_freq_4.get(respostas['q41']),
            }
            
            dados_validos = CopsoqII(**respostas_numericas)
            
            st.success("Formulário validado com sucesso!")
            
            # --- CÁLCULO E EXIBIO DOS RESULTADOS (DESCOMENTADO) ---
            df_resultados = calcular_pontuacao_copsoq_ii(dados_validos)
            
            st.subheader("Resultados da Avaliação (Semáforo de Risco)")
            st.caption("Pontuação 0-100 (0 = Risco Mínimo, 100 = Risco Máximo)")
            
            # Aplicar o estilo (semáforo)
            st.dataframe(
                df_resultados.style.applymap(colorir_risco, subset=['Nível de Risco']),
                width='stretch'
            )
            
            with st.expander("Ver dados brutos (JSON)"):
                st.json(dados_validos.model_dump_json(indent=2))


        except Exception as e:
            st.error(f"Erro ao processar o formulário: {e}")
            st.warning("Por favor, responda todas as perguntas.")

if __name__ == "__main__":
    st.sidebar.success("Módulo COPSOQ II (AEP) carregado.")
    render_form()


