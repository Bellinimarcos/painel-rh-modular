import streamlit as st
import pandas as pd
import plotly.express as px
import random
# Importa o banco de questionários que acabamos de criar
from data.questionarios_banco import QUESTIONARIOS_DISPONIVEIS

# Título da Página (visível no menu lateral do Streamlit)
st.set_page_config(layout="wide")

# --- Inicialização do Session State ---
# Guarda a campanha ativa
if 'campanha_ativa' not in st.session_state:
    # Define o primeiro questionário da lista como padrão
    default_nome = list(QUESTIONARIOS_DISPONIVEIS.keys())[0]
    default_data = QUESTIONARIOS_DISPONIVEIS[default_nome]
    
    st.session_state.campanha_ativa = {
        "nome": "Avaliação Anual 2025",
        "questionario_nome": default_nome, 
        "questionario_data": default_data
    }


# --- Funções de Lógica ---
# No seu projeto, isso estaria no diretório 'logic'

def calcular_pontuacao_dominio(respostas, pontuacao_map):
    """Calcula a pontuação média para um conjunto de respostas de um domínio."""
    if not respostas:
        return 0
    total_pontos = sum(pontuacao_map.get(resp, 0) for resp in respostas)
    max_pontos_possivel = len(respostas) * max(pontuacao_map.values())
    # Evita divisão por zero se max_pontos_possivel for 0
    if max_pontos_possivel == 0:
        return 0
    return (total_pontos / max_pontos_possivel) * 100  # Converte para %

def gerar_dados_mock_dashboard(setores, dominios_questionario):
    """Gera dados falsos para o dashboard (Módulo 3)."""
    data = []
    for setor in setores:
        for dominio in dominios_questionario:
            # Gera um "índice de risco" aleatório (0-100)
            score = random.randint(20, 90)
            data.append({"Setor": setor, "Domínio": dominio, "Índice de Risco (%)": score})
    return pd.DataFrame(data)

# --- Página Principal ---

st.title(" Módulo de Avaliação de Riscos Psicossiais")
st.markdown("""
Esta ferramenta é um módulo integrado ao Painel de RH para gerenciar o ciclo de avaliação
de riscos psicossiais, em linha com as NRs 01, 05 e 17.
""")

# Abas para simular os Módulos da proposta
tab1, tab2, tab3 = st.tabs([
    " Módulo 2: Responder Avaliação (Visão do Colaborador)",
    " Módulo 3: Dashboard de Resultados (Visão do RH/Gestor)",
    "️ Módulo 1 e 4: Configuração e Planos (Visão do RH)"
])

# --- Aba 1: Responder Avaliação (Módulo 2) ---
with tab1:
    st.header(f"Avaliação: {st.session_state.campanha_ativa['nome']}")
    st.subheader(f"Questionário: {st.session_state.campanha_ativa['questionario_nome']}")
    st.info("""
    **Sua participação é 100% anônima e confidencial.**
    Estas perguntas ajudam a empresa a entender e melhorar seu ambiente de trabalho.
    Não existem respostas 'certas' ou 'erradas'.
    """)
    
    # Carrega o questionário ativo do session_state
    questionario_ativo = st.session_state.campanha_ativa.get('questionario_data', {})
    
    if not questionario_ativo:
        st.error("Nenhum questionário configurado. Por favor, configure uma campanha na Aba 3.")
    else:
        with st.form("dynamic_copsoq_form"):
            # Itera sobre os domínios e perguntas do questionário ATIVO
            for dominio, data_dominio in questionario_ativo.items():
                st.subheader(dominio)
                perguntas = data_dominio.get('perguntas', [])
                opcoes = data_dominio.get('opcoes', [])
                
                # Define um índice padrão seguro
                default_index = len(opcoes) // 2 if opcoes else 0
                
                for i, pergunta in enumerate(perguntas):
                    key = f"{dominio}_{i}"
                    st.radio(
                        pergunta,
                        opcoes,
                        horizontal=True,
                        key=key,
                        index=default_index 
                    )
                st.divider()
            
            submitted = st.form_submit_button("Enviar Respostas Anônimas")
            
            if submitted:
                # Lógica de envio:
                respostas_coletadas = {}
                for dominio, data_dominio in questionario_ativo.items():
                    perguntas = data_dominio.get('perguntas', [])
                    for i, pergunta in enumerate(perguntas):
                        key = f"{dominio}_{i}"
                        if key in st.session_state:
                            respostas_coletadas[key] = {
                                "pergunta": pergunta,
                                "resposta": st.session_state[key],
                                "dominio": dominio
                            }
                
                # 3. Enviar 'respostas_coletadas' para o seu 'services' ou 'data'
                # st.write(respostas_coletadas) # Para debug
                
                st.success("Obrigado! Suas respostas foram registradas anonimamente.")
                st.balloons()

# --- Aba 2: Dashboard de Resultados (Módulo 3) ---
with tab2:
    st.header("Dashboard de Resultados (Visão Gerencial)")
    st.markdown(f"Análise dos dados da campanha: **{st.session_state.campanha_ativa['nome']}**")

    # Simulação de dados (em um app real, viria do seu 'data')
    setores_mock = ["Vendas", "Engenharia", "Marketing", "Operações", "RH"]
    # Pega os domínios do questionário ATIVO
    dominios_ativos = list(st.session_state.campanha_ativa.get('questionario_data', {}).keys())
    
    if not dominios_ativos:
         st.warning("Nenhum questionário ativo para exibir dados.")
    else:
        df_resultados = gerar_dados_mock_dashboard(setores_mock, dominios_ativos)

        st.subheader("Mapa de Calor (Heatmap) por Setor e Domínio")
        
        # Criar o Heatmap
        heatmap_fig = px.imshow(
            df_resultados.pivot(index="Domínio", columns="Setor", values="Índice de Risco (%)"),
            text_auto=True,
            aspect="auto",
            color_continuous_scale=[
                (0, "green"), (0.33, "green"),  # Bom
                (0.33, "yellow"), (0.66, "yellow"), # Alerta
                (0.66, "red"), (1.0, "red")      # Crítico
            ],
            range_color=[0, 100],
            title="Índice de Risco Psicossocial (Quanto maior, pior)"
        )
        heatmap_fig.update_layout(
            xaxis_title="Setores",
            yaxis_title="Domínios de Risco",
            height=max(500, len(dominios_ativos) * 20) # Ajusta altura dinamicamente
        )
        st.plotly_chart(heatmap_fig, width='stretch')

        st.subheader("Análise Detalhada por Filtro")
        
        col1, col2 = st.columns(2)
        
        with col1:
            setor_filtro = st.selectbox("Selecione o Setor", ["Todos"] + setores_mock, key="filtro_setor")
            
            # Filtra o DF
            if setor_filtro != "Todos":
                df_filtrado_setor = df_resultados[df_resultados["Setor"] == setor_filtro]
            else:
                df_filtrado_setor = df_resultados.groupby("Domínio")["Índice de Risco (%)"].mean().reset_index()

            # Gráfico de Barras por Domínio
            bar_fig = px.bar(
                df_filtrado_setor,
                x="Domínio",
                y="Índice de Risco (%)",
                title=f"Média de Risco para: {setor_filtro}",
                color="Índice de Risco (%)",
                color_continuous_scale=[(0, "green"), (0.5, "yellow"), (1, "red")],
                range_color=[0, 100]
            )
            bar_fig.update_layout(height=400)
            st.plotly_chart(bar_fig, width='stretch')

        with col2:
            dominio_filtro = st.selectbox("Selecione o Domínio", ["Todos"] + dominios_ativos, key="filtro_dominio")

            # Filtra o DF
            if dominio_filtro != "Todos":
                df_filtrado_dominio = df_resultados[df_resultados["Domínio"] == dominio_filtro]
            else:
                df_filtrado_dominio = df_resultados.groupby("Setor")["Índice de Risco (%)"].mean().reset_index()

            # Gráfico de Barras por Setor
            bar_fig_setor = px.bar(
                df_filtrado_dominio,
                x="Setor",
                y="Índice de Risco (%)",
                title=f"Média de Risco para: {dominio_filtro}",
                color="Índice de Risco (%)",
                color_continuous_scale=[(0, "green"), (0.5, "yellow"), (1, "red")],
                range_color=[0, 100]
            )
            bar_fig_setor.update_layout(height=400)
            st.plotly_chart(bar_fig_setor, width='stretch')


# --- Aba 3: Configuração e Planos (Módulos 1 e 4) ---
with tab3:
    st.header("Configuração de Campanhas (Módulo 1)")
    st.markdown("Aqui você configuraria o início e fim das campanhas, selecionaria o público e o questionário (COPSOQ II, III, etc.).")
    
    # Pega os nomes dos questionários disponíveis do arquivo que importamos
    nomes_questionarios = list(QUESTIONARIOS_DISPONIVEIS.keys())
    
    # Se a lista estiver vazia, adiciona um item placeholder
    if not nomes_questionarios:
        nomes_questionarios = ["Nenhum questionário em data/questionarios_banco.py"]
        
    
    novo_nome_campanha = st.text_input("Nome da Campanha", st.session_state.campanha_ativa.get('nome', 'Campanha Padrão'))
    st.date_input("Data de Início") # Apenas visual por enquanto
    st.date_input("Data de Fim") # Apenas visual por enquanto
    
    # Encontra o índice do questionário ativo para definir como padrão no selectbox
    try:
        nome_ativo = st.session_state.campanha_ativa.get('questionario_nome')
        indice_ativo = nomes_questionarios.index(nome_ativo)
    except (ValueError, TypeError):
        indice_ativo = 0 # Padrão
        
    novo_questionario_nome = st.selectbox(
        "Questionário", 
        nomes_questionarios, 
        index=indice_ativo
    )

    if st.button("Agendar / Atualizar Campanha"):
        # ATUALIZA O SESSION STATE
        if novo_questionario_nome in QUESTIONARIOS_DISPONIVEIS:
            st.session_state.campanha_ativa = {
                "nome": novo_nome_campanha,
                "questionario_nome": novo_questionario_nome,
                "questionario_data": QUESTIONARIOS_DISPONIVEIS[novo_questionario_nome]
            }
            st.success(f"Campanha '{novo_nome_campanha}' agendada com o questionário '{novo_questionario_nome}'!")
            # Idealmente, aqui você salvaria essa configuração no seu 'data'
            st.rerun() # Força a atualização das outras abas
        else:
            st.error(f"Questionário '{novo_questionario_nome}' não encontrado. Verifique 'data/questionarios_banco.py'.")


    st.divider()

    st.header("Plano de Ação (Módulo 4)")
    st.markdown("""
    Com base nos resultados do **Módulo 3**, esta área permite criar e acompanhar planos de ação (5W2H)
    para mitigar os riscos identificados. Estes planos podem ser exportados para o PGR.
    """)
    
    with st.expander("Criar Novo Plano de Ação para 'Vendas' (Risco Alto em Demandas)"):
        st.text_input("O que fazer (What)?", "Revisar metas e prazos do time de Vendas")
        st.text_input("Por que fazer (Why)?", "Reduzir o 'Índice de Risco' em Demandas Psicológicas (85%)")
        st.text_input("Quem (Who)?", "Diretor Comercial + Gerente de RH")
        st.date_input("Quando (When)?", key="plano_data")
        st.text_area("Como (How)?", "1. Workshop com a equipe para feedback\n2. Reunião de redefinição de metas\n3. Contratação de 1 SDR")
        st.button("Salvar Plano de Ação")




