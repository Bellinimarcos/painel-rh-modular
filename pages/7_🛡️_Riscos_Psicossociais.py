import streamlit as st
import pandas as pd
from datetime import datetime
import json

# --- 1. CONFIGURAÇÃO INICIAL DA PÁGINA E ESTILOS ---
st.set_page_config(page_title="COPSOQ III - Riscos Psicossociais", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stRadio > label {
        font-size: 14px;
        font-weight: 500;
    }
    .questao-titulo {
        font-size: 15px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. TÍTULO E CABEÇALHO ---
st.title("🛡️ Sistema de Gestão de Riscos Psicossociais")
st.markdown("**COPSOQ III - Brasil | Versão Média | Validação Dra. Teresa Cotrim**")
st.caption("⚠️ Material validado cientificamente - Uso restrito para pesquisa e consultoria profissional")

# --- 3. INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
# Garante que as variáveis persistam entre as interações do usuário
if 'projeto' not in st.session_state:
    st.session_state.projeto = {}
if 'respondentes' not in st.session_state:
    st.session_state.respondentes = []
if 'inventario_riscos' not in st.session_state:
    st.session_state.inventario_riscos = []
if 'planos_acao' not in st.session_state:
    st.session_state.planos_acao = []

# --- 4. CONSTANTES E DADOS DO QUESTIONÁRIO ---
DIMENSOES_COPSOQ = {
    'Exigências Quantitativas': ['EQ1', 'EQ2', 'EQ3'],
    'Ritmo de Trabalho': ['R1', 'R2'],
    'Exigências Cognitivas': ['EC1', 'EC2', 'EC3', 'EC4'],
    'Exigências Emocionais': ['EE1', 'EE2', 'EE3'],
    'Influência no Trabalho': ['IT1', 'IT2', 'IT3', 'IT4'],
    'Possibilidades de Desenvolvimento': ['PD1', 'PD2', 'PD3'],
    'Controlo sobre o Tempo de Trabalho': ['CTT1', 'CTT2', 'CTT3'],
    'Significado do Trabalho': ['ST1', 'ST2', 'ST3'],
    'Compromisso face ao Local de Trabalho': ['CLT1', 'CLT3'],
    'Previsibilidade': ['Prev1', 'Prev2'],
    'Reconhecimento': ['Rec1', 'Rec2', 'Rec3'],
    'Transparência do Papel Laboral': ['Transp1', 'Transp2', 'Transp3'],
    'Conflitos de Papéis Laborais': ['CPL1', 'CPL2', 'CPL3'],
    'Qualidade da Liderança': ['QL1', 'QL2', 'QL3', 'QL4'],
    'Suporte Social de Colegas': ['SSC1', 'SSC2', 'SSC3'],
    'Suporte Social de Superiores': ['SSup1', 'SSup2', 'SSup3'],
    'Sentido de Pertença a Comunidade': ['SPCom1', 'SPCom2', 'SPCom3'],
    'Insegurança Laboral': ['IL1', 'IL2'],
    'Insegurança com as Condições de Trabalho': ['ICL1', 'ICL2', 'ICL3'],
    'Qualidade do Trabalho': ['QT1'],
    'Confiança Horizontal': ['CH1', 'CH2', 'CH3'],
    'Confiança Vertical': ['CV1', 'CV2', 'CV3'],
    'Justiça Organizacional': ['JO1', 'JO2', 'JO3', 'JO4'],
    'Conflito Trabalho-Família': ['CTF1', 'CTF2', 'CTF3'],
    'Satisfação com o trabalho': ['Sat1', 'Sat2', 'Sat3'],
    'Auto-Avaliação da Saúde': ['Saude'],
    'Auto-Eficácia': ['AE1', 'AE2'],
    'Problemas de Sono': ['Sono1', 'Sono2'],
    'Burnout': ['Burnout1', 'Burnout2'],
    'Stress': ['Stress1', 'Stress2'],
    'Sintomas Depressivos': ['SD1', 'SD2']
}

QUESTOES = {
    'EQ1': 'A sua carga de trabalho é distribuída de modo desigual e pode se acumular?',
    'EQ2': 'Você fica com trabalho atrasado?',
    'EQ3': 'Com que frequência você não tem tempo para completar todas as suas tarefas de trabalho?',
    'R1': 'Você tem que trabalhar muito rápido?',
    'R2': 'Você trabalha a um ritmo muito rápido ao longo do dia?',
    'EC1': 'O seu trabalho exige a sua atenção constante?',
    'EC2': 'O seu trabalho exige que você lembre de muitas coisas?',
    'EC3': 'O seu trabalho requer que você crie novas ideias?',
    'EC4': 'O seu trabalho exige que você tenha que tomar decisões difíceis?',
    'EE1': 'O seu trabalho coloca você em situações emocionalmente perturbadoras?',
    'EE2': 'Você tem de lidar com os problemas pessoais dos outros como parte do seu trabalho?',
    'EE3': 'O seu trabalho é exigente emocionalmente?',
    'IT1': 'Você tem grande influência nas decisões sobre o seu trabalho?',
    'IT2': 'Você tem influência sobre a quantidade de trabalho que lhe é atribuída?',
    'IT3': 'Você tem alguma influência sobre O QUE faz no trabalho?',
    'IT4': 'Você tem influência sobre COMO faz o seu trabalho?',
    'PD1': 'Você tem a possibilidade de aprender coisas novas por meio do seu trabalho?',
    'PD2': 'Você consegue usar as suas habilidades ou a sua experiência no trabalho?',
    'PD3': 'O seu trabalho lhe dá a oportunidade de desenvolver as suas habilidades?',
    'CTT1': 'Você pode decidir quando fazer uma pausa?',
    'CTT2': 'Você pode tirar férias próximo a data que quiser?',
    'CTT3': 'Pode fazer uma pausa no trabalho para falar com um/a colega?',
    'ST1': 'O seu trabalho é significativo para você?',
    'ST2': 'Você sente que o trabalho que você faz é importante?',
    'ST3': 'Sente-se motivado e envolvido com o seu trabalho?',
    'CLT1': 'Você gosta de falar para aos outros sobre o seu local de trabalho?',
    'CLT3': 'Você tem orgulho de fazer parte desta organização?',
    'Prev1': 'No seu local de trabalho, você é informado antecedência suficiente sobre decisões importantes, alterações ou planos para o futuro?',
    'Prev2': 'Você recebe todas as informações de que precisa a fim de desempenhar bem o seu trabalho?',
    'Rec1': 'O seu trabalho é reconhecido e apreciado pela gerência?',
    'Rec2': 'Você é respeitado por sua gerência?',
    'Rec3': 'Você é tratado de maneira justa no seu local de trabalho?',
    'Transp1': 'O seu trabalho tem objetivos claros?',
    'Transp2': 'Você sabe exatamente quais as áreas são de sua responsabilidade?',
    'Transp3': 'Você sabe exatamente o que se espera de você no seu trabalho?',
    'CPL1': 'São solicitadas exigências contraditórias no seu trabalho?',
    'CPL2': 'Às vezes você precisa fazer coisas de modo diferente ao que elas deveriam ser feitas?',
    'CPL3': 'Às vezes você precisa fazer coisas que parecem desnecessárias?',
    'QL1': 'Em relação à sua chefia direta, até que ponto considera que garante que os membros da equipe tenham boas oportunidades para desenvolvimento?',
    'QL2': 'Em relação à sua chefia direta, até que ponto considera que é adequada no planejamento do trabalho?',
    'QL3': 'Em relação à sua chefia direta, até que ponto considera que é adequada na resolução de conflitos?',
    'QL4': 'Em relação à sua chefia direta, até que ponto considera que prioriza à satisfação com o trabalho?',
    'SSC1': 'Em caso de necessidade, com que frequência você conseguiria apoio e ajuda dos seus colegas?',
    'SSC2': 'Em caso de necessidade, com que frequência os seus colegas estariam dispostos a ouvir sobre os seus problemas no trabalho?',
    'SSC3': 'Com que frequência os seus colegas falam com você sobre o seu nível de desempenho no trabalho?',
    'SSup1': 'Em caso de necessidade, com que frequência a sua supervisão imediata estaria disposta a lhe ouvir sobre os seus problemas no trabalho?',
    'SSup2': 'Em caso de necessidade, com que frequência você conseguiria apoio e ajuda da sua supervisão imediata?',
    'SSup3': 'Com que frequência a sua supervisão imediata fala sobre o desempenho do seu trabalho?',
    'SPCom1': 'Há um clima bom entre você e os seus colegas?',
    'SPCom2': 'Você se sente como parte de uma equipe no seu local de trabalho?',
    'SPCom3': 'Há uma boa cooperação entre os colegas no trabalho?',
    'IL1': 'Você está preocupado com ficar desempregado(a)?',
    'IL2': 'Você está preocupado com a dificuldade em encontrar outro emprego caso fique desempregado(a)?',
    'ICL1': 'Você está preocupado com ser transferido(a) para outra função ou local contra a sua vontade?',
    'ICL2': 'Você está preocupado/a com que o cronograma seja alterado (turno, dias de semana, horário de entrada e saída...) contra a sua vontade?',
    'ICL3': 'Você está preocupado/a com uma diminuição no seu rendimento?',
    'QT1': 'Você está satisfeito (a) com a qualidade do trabalho realizado por si?',
    'CH1': 'Os empregados confiam uns nos outros, no geral?',
    'CH2': 'Os empregados escondem informações uns dos outros?',
    'CH3': 'Os empregados escondem informações da gerência?',
    'CV1': 'A gerência confia que os empregados façam um bom trabalho?',
    'CV2': 'Os empregados confiam nas informações vindas da gerência?',
    'CV3': 'Os empregados são capazes de expressar seus sentimentos e pontos de vista para a gerência?',
    'JO1': 'Os conflitos são resolvidos de modo justo?',
    'JO2': 'O trabalho é distribuído de maneira justa?',
    'JO3': 'As sugestões dos empregados são tratadas com seriedade pela gerência?',
    'JO4': 'Os empregados são reconhecidos por fazer um bom trabalho?',
    'CTF1': 'Você sente que o seu trabalho tira tanto a sua energia que provoca um efeito negativo na sua vida privada?',
    'CTF2': 'O seu trabalho requer muito do seu tempo, o que afeta negativamente sua vida privada?',
    'CTF3': 'As exigências do seu trabalho interferem na sua vida privada e familiar?',
    'Sat1': 'Em relação ao seu trabalho em geral, quão satisfeito(a) está com suas perspectivas de trabalho?',
    'Sat2': 'Em relação ao seu trabalho em geral, quão satisfeito(a) está com o seu emprego como um todo, levando tudo em conta?',
    'Sat3': 'Em relação ao seu trabalho em geral, quão satisfeito(a) está com o modo como as suas habilidades são usadas?',
    'Saude': 'Em geral, você diria que a sua saúde é:',
    'AE1': 'Quando tenho um problema, normalmente consigo encontrar diversas maneiras de resolvê-lo',
    'AE2': 'É fácil para mim manter os meus planos e alcançar os meus objetivos',
    'Sono1': 'Com que frequência durante as últimas 4 semanas tem encontrado dificuldade para dormir?',
    'Sono2': 'Com que frequência durante as últimas 4 semanas acorda muito cedo e não é capaz de voltar a dormir?',
    'Burnout1': 'Com que frequência durante as últimas 4 semanas se sente fisicamente exausto?',
    'Burnout2': 'Com que frequência durante as últimas 4 semanas se sente emocionalmente exausto?',
    'Stress1': 'Com que frequência durante as últimas 4 semanas se sente irritado/a?',
    'Stress2': 'Com que frequência durante as últimas 4 semanas se sente ansioso/a?',
    'SD1': 'Com que frequência durante as últimas 4 semanas vem se sentindo triste?',
    'SD2': 'Com que frequência durante as últimas 4 semanas sente falta de interesse pelas coisas cotidianas?'
}

ESCALA_NUNCA_SEMPRE = ['Nunca', 'Raramente', 'Às vezes', 'Frequentemente', 'Sempre']
ESCALA_NADA_EXTREMAMENTE = ['Nada', 'Um pouco', 'Moderadamente', 'Muito', 'Extremamente']
ESCALA_SAUDE = ['Fraca', 'Razoável', 'Boa', 'Muito boa', 'Excelente']

ESCALAS_POR_QUESTAO = {}
for cod in QUESTOES.keys():
    if cod in ['ST1', 'ST2', 'ST3', 'CLT1', 'CLT3', 'IL1', 'IL2', 'ICL1', 'ICL2', 'ICL3', 'QT1', 'Sat1', 'Sat2', 'Sat3']:
        ESCALAS_POR_QUESTAO[cod] = ESCALA_NADA_EXTREMAMENTE
    elif cod == 'Saude':
        ESCALAS_POR_QUESTAO[cod] = ESCALA_SAUDE
    else:
        ESCALAS_POR_QUESTAO[cod] = ESCALA_NUNCA_SEMPRE

# --- 5. FUNÇÕES DE CÁLCULO ---
def calcular_nivel_risco(prob, sev):
    """Calcula o nível de risco com base na probabilidade e severidade."""
    score = prob * sev
    if score >= 15:
        return {'nivel': 'CRÍTICO', 'cor': '🔴', 'score': score}
    elif score >= 9:
        return {'nivel': 'ALTO', 'cor': '🟠', 'score': score}
    elif score >= 4:
        return {'nivel': 'MÉDIO', 'cor': '🟡', 'score': score}
    else:
        return {'nivel': 'BAIXO', 'cor': '🟢', 'score': score}

def calcular_scores_dimensoes(respostas):
    """Calcula os scores de 0 a 100 para cada dimensão do COPSOQ."""
    scores = {}
    for dimensao, codigos in DIMENSOES_COPSOQ.items():
        valores = []
        for cod in codigos:
            if cod in respostas and respostas[cod] is not None:
                escala = ESCALAS_POR_QUESTAO[cod]
                if respostas[cod] in escala:
                    valor = escala.index(respostas[cod])
                    valores.append(valor)
        if valores:
            media = sum(valores) / len(valores)
            score_100 = (media / 4) * 100
            scores[dimensao] = round(score_100, 1)
        else:
            scores[dimensao] = None
    return scores

# --- 6. LAYOUT DA INTERFACE (ABAS) ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👥 Dados Sócio-Demográficos",
    "📋 COPSOQ III - Questionário",
    "📊 Resultados & Análise",
    "⚠️ Inventário de Riscos",
    "📈 Matriz de Risco",
    "✅ Planos 5W2H"
])

# --- ABA 1: DADOS SÓCIO-DEMOGRÁFICOS ---
with tab1:
    st.header("Parte 1: Caracterização Sócio-Demográfica")
    st.info("📝 Por favor, preencha o questionário com atenção e responda a todas as questões.")

    with st.form("form_demografico"):
        col1, col2 = st.columns(2)

        with col1:
            data_aplicacao = st.date_input("Data", value=datetime.now())
            sexo = st.radio("1. Sexo", ["Feminino", "Masculino"], horizontal=True)
            idade = st.number_input("2. Idade (anos)", min_value=16, max_value=100, value=30)
            escolaridade = st.selectbox("3. Escolaridade", [
                "Nunca estudou", "Ensino Fundamental (incompleto)", "Ensino Fundamental (completo)",
                "Ensino Médio", "Ensino Técnico", "Ensino Superior", "Especialização", "Mestrado", "Doutorado"
            ])

        with col2:
            estado_civil = st.selectbox("4. Estado Civil", [
                "Solteiro(a)", "Casado(a) / União de Fato", "Divorciado(a) / Separado(a)", "Viúvo(a)"
            ])
            tempo_empresa = st.number_input("5. Tempo na Empresa (anos completos)", min_value=0, max_value=50, value=0)
            setor_atividade = st.text_input("6. Setor de Atividade")

        submitted = st.form_submit_button("💾 Salvar e Iniciar Questionário COPSOQ III", use_container_width=True)

        if submitted:
            st.session_state.dados_demograficos = {
                'data': data_aplicacao.strftime('%d/%m/%Y'),
                'sexo': sexo,
                'idade': idade,
                'escolaridade': escolaridade,
                'estado_civil': estado_civil,
                'tempo_empresa': tempo_empresa,
                'setor': setor_atividade
            }
            st.session_state.respostas_copsoq = {}
            st.success("✅ Dados salvos! Vá para a aba 'COPSOQ III - Questionário' para responder.")

# --- ABA 2: QUESTIONÁRIO COPSOQ III ---
with tab2:
    st.header("Parte 2: COPSOQ III - Questionário Completo (84 questões)")

    if 'dados_demograficos' not in st.session_state:
        st.warning("⚠️ Por favor, preencha primeiro os Dados Sócio-Demográficos na aba anterior.")
    else:
        st.info(f"👤 Respondente: {st.session_state.dados_demograficos['sexo']}, {st.session_state.dados_demograficos['idade']} anos")

        if 'respostas_copsoq' not in st.session_state:
            st.session_state.respostas_copsoq = {}

        with st.form("form_copsoq"):
            for dimensao, codigos in DIMENSOES_COPSOQ.items():
                st.subheader(f"📌 {dimensao}")

                for cod in codigos:
                    questao_texto = QUESTOES[cod]
                    escala = ESCALAS_POR_QUESTAO[cod]
                    st.markdown(f"<div class='questao-titulo'>{cod}. {questao_texto}</div>", unsafe_allow_html=True)
                    resposta = st.radio(f"Selecione sua resposta para {cod}:", escala, key=f"q_{cod}", horizontal=True, label_visibility="collapsed")
                    st.session_state.respostas_copsoq[cod] = resposta

                st.divider()

            submitted_copsoq = st.form_submit_button("✅ Finalizar e Calcular Resultados", use_container_width=True)

            if submitted_copsoq:
                novo_respondente = {
                    'id': len(st.session_state.respondentes) + 1,
                    'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    **st.session_state.dados_demograficos,
                    'respostas': st.session_state.respostas_copsoq.copy(),
                    'scores': calcular_scores_dimensoes(st.session_state.respostas_copsoq)
                }
                st.session_state.respondentes.append(novo_respondente)
                st.success(f"✅ Questionário finalizado! Total de respondentes: {len(st.session_state.respondentes)}")
                st.balloons()

# --- ABA 3: RESULTADOS E ANÁLISE ---
with tab3:
    st.header("📊 Resultados & Análise Coletiva")

    if not st.session_state.respondentes:
        st.info("📝 Ainda não há respondentes. Aplique o questionário COPSOQ III primeiro.")
    else:
        st.success(f"✅ Total de respondentes: **{len(st.session_state.respondentes)}**")
        st.subheader("Scores Médios por Dimensão (0-100)")

        df_scores = pd.DataFrame([r['scores'] for r in st.session_state.respondentes])
        medias = df_scores.mean().sort_values(ascending=True)

        st.bar_chart(medias)

        st.subheader("Detalhamento por Dimensão")
        df_detalhado = pd.DataFrame({
            'Dimensão': medias.index,
            'Score Médio': medias.values.round(1),
            'Mín': df_scores.min()[medias.index].values.round(1),
            'Máx': df_scores.max()[medias.index].values.round(1)
        })
        st.dataframe(df_detalhado, use_container_width=True, hide_index=True)

        st.subheader("🚨 Identificação Automática de Riscos")
        st.info("Dimensões com score médio < 40 são consideradas áreas de risco")

        riscos_identificados = medias[medias < 40]

        if len(riscos_identificados) > 0:
            for dimensao, score in riscos_identificados.items():
                if st.button(f"➕ Adicionar '{dimensao}' ao Inventário de Riscos", key=f"add_{dimensao}"):
                    novo_risco = {
                        'id': len(st.session_state.inventario_riscos) + 1,
                        'dimensao': dimensao,
                        'fator_risco': f"Score baixo em {dimensao}",
                        'evidencias': f"Score médio de {score:.1f}/100 na avaliação COPSOQ III com {len(st.session_state.respondentes)} respondentes",
                        'probabilidade': 4,
                        'severidade': 3,
                        'nivel_risco': calcular_nivel_risco(4, 3)
                    }
                    st.session_state.inventario_riscos.append(novo_risco)
                    st.success(f"✅ Risco adicionado ao inventário!")
                    st.rerun()
        else:
            st.success("✅ Nenhuma dimensão com score crítico identificada.")

        st.divider()
        st.subheader("📥 Exportar Dados")

        dados_export = []
        for resp in st.session_state.respondentes:
            linha = {
                'data': resp.get('data', ''),
                'sexo': resp.get('sexo', ''),
                'idade': resp.get('idade', ''),
                'escolaridade': resp.get('escolaridade', ''),
                'estado_civil': resp.get('estado_civil', ''),
                'tempo_empresa': resp.get('tempo_empresa', ''),
                'setor': resp.get('setor', ''),
                **resp.get('respostas', {}),
                **resp.get('scores', {})
            }
            dados_export.append(linha)

        df_export = pd.DataFrame(dados_export)
        csv = df_export.to_csv(index=False).encode('utf-8-sig')

        st.download_button(
            label="📊 Download Dados Completos (CSV)",
            data=csv,
            file_name=f"COPSOQ_III_Dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# --- ABA 4: INVENTÁRIO DE RISCOS ---
with tab4:
    st.header("⚠️ Inventário de Riscos Psicossociais")

    with st.expander("➕ Adicionar Risco Manualmente", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            dimensao_manual = st.selectbox("Dimensão", list(DIMENSOES_COPSOQ.keys()), key="dim_manual")
            fator_manual = st.text_input("Fator de Risco", key="fator_manual")

        with col2:
            evidencias_manual = st.text_area("Evidências", key="evid_manual")

        col3, col4 = st.columns(2)
        with col3:
            prob_manual = st.slider("Probabilidade", 1, 5, 3, key="prob_manual")
        with col4:
            sev_manual = st.slider("Severidade", 1, 5, 3, key="sev_manual")

        if st.button("➕ Adicionar Risco Manual"):
            if fator_manual:
                novo_risco = {
                    'id': len(st.session_state.inventario_riscos) + 1,
                    'dimensao': dimensao_manual,
                    'fator_risco': fator_manual,
                    'evidencias': evidencias_manual,
                    'probabilidade': prob_manual,
                    'severidade': sev_manual,
                    'nivel_risco': calcular_nivel_risco(prob_manual, sev_manual)
                }
                st.session_state.inventario_riscos.append(novo_risco)
                st.success("✅ Risco adicionado!")
                st.rerun()

    st.subheader(f"Riscos Identificados ({len(st.session_state.inventario_riscos)})")

    for i, risco in enumerate(st.session_state.inventario_riscos):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                **{risco['nivel_risco']['cor']} {risco['nivel_risco']['nivel']}** | **Dimensão:** {risco['dimensao']}
                
                **Fator:** {risco['fator_risco']}
                
                **Evidências:** {risco['evidencias']}
                
                📊 P: {risco['probabilidade']}/5 | S: {risco['severidade']}/5 | Score: {risco['nivel_risco']['score']}
                """)

            with col2:
                if st.button("🗑️", key=f"del_risco_{i}"):
                    st.session_state.inventario_riscos.pop(i)
                    st.rerun()

            st.divider()

# --- ABA 5: MATRIZ DE RISCO ---
with tab5:
    st.header("📈 Matriz de Probabilidade × Severidade")

    matriz_data = []
    for prob in range(5, 0, -1):
        linha = [f"**{prob}**"]
        for sev in range(1, 6):
            score = prob * sev
            nivel = calcular_nivel_risco(prob, sev)
            riscos_celula = [r for r in st.session_state.inventario_riscos
                             if r['probabilidade'] == prob and r['severidade'] == sev]
            linha.append(f"{nivel['cor']} {score}\n({len(riscos_celula)})")
        matriz_data.append(linha)

    df_matriz = pd.DataFrame(matriz_data, columns=['P↓\\S→', '1', '2', '3', '4', '5'])
    st.dataframe(df_matriz, use_container_width=True, hide_index=True)

    st.subheader("Distribuição por Nível de Risco")
    col1, col2, col3, col4 = st.columns(4)

    total_baixo = len([r for r in st.session_state.inventario_riscos if r['nivel_risco']['nivel'] == 'BAIXO'])
    total_medio = len([r for r in st.session_state.inventario_riscos if r['nivel_risco']['nivel'] == 'MÉDIO'])
    total_alto = len([r for r in st.session_state.inventario_riscos if r['nivel_risco']['nivel'] == 'ALTO'])
    total_critico = len([r for r in st.session_state.inventario_riscos if r['nivel_risco']['nivel'] == 'CRÍTICO'])

    col1.metric("🟢 BAIXO", total_baixo)
    col2.metric("🟡 MÉDIO", total_medio)
    col3.metric("🟠 ALTO", total_alto)
    col4.metric("🔴 CRÍTICO", total_critico)

# --- ABA 6: PLANOS DE AÇÃO 5W2H ---
with tab6:
    st.header("✅ Planos de Ação 5W2H")

    if st.button("➕ Novo Plano de Ação"):
        novo_plano = {
            'id': len(st.session_state.planos_acao) + 1,
            'what': '', 'why': '', 'where': '', 'when': '',
            'who': '', 'how': '', 'how_much': '', 'risco_relacionado': ''
        }
        st.session_state.planos_acao.append(novo_plano)
        st.rerun()

    if st.session_state.planos_acao:
        for i, plano in enumerate(st.session_state.planos_acao):
            with st.expander(f"📋 Plano de Ação #{i+1}", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    what = st.text_input("O QUÊ (What)", value=plano['what'], key=f"what_{i}")
                    why = st.text_input("POR QUÊ (Why)", value=plano['why'], key=f"why_{i}")
                    where = st.text_input("ONDE (Where)", value=plano['where'], key=f"where_{i}")
                    when = st.text_input("QUANDO (When)", value=plano['when'], key=f"when_{i}")

                with col2:
                    who = st.text_input("QUEM (Who)", value=plano['who'], key=f"who_{i}")
                    how = st.text_input("COMO (How)", value=plano['how'], key=f"how_{i}")
                    how_much = st.text_input("QUANTO (How Much)", value=plano['how_much'], key=f"hm_{i}")

                    riscos_opcoes = [''] + [r['fator_risco'] for r in st.session_state.inventario_riscos]
                    idx = riscos_opcoes.index(plano['risco_relacionado']) if plano['risco_relacionado'] in riscos_opcoes else 0
                    risco_rel = st.selectbox("Risco Relacionado", riscos_opcoes, index=idx, key=f"rr_{i}")

                st.session_state.planos_acao[i] = {
                    'id': plano['id'],
                    'what': what, 'why': why, 'where': where, 'when': when,
                    'who': who, 'how': how, 'how_much': how_much, 'risco_relacionado': risco_rel
                }

                if st.button("🗑️ Remover Plano", key=f"del_plano_{i}"):
                    st.session_state.planos_acao.pop(i)
                    st.rerun()
    else:
        st.info("Nenhum plano de ação criado ainda.")

# --- 7. SEÇÃO FINAL: RELATÓRIO E FOOTER ---
st.divider()
st.subheader("📥 Gerar Relatório Completo")

col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Gerar e Baixar Relatório Completo (.txt)", disabled=len(st.session_state.inventario_riscos)==0):
        relatorio = f"""
RELATÓRIO DE AVALIAÇÃO DE RISCOS PSICOSSOCIAIS
COPSOQ III - BRASIL (Versão Média)
==============================================

DADOS DA AVALIAÇÃO
Número de Respondentes: {len(st.session_state.respondentes)}
Data do Relatório: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

RESULTADOS COPSOQ III - SCORES MÉDIOS POR DIMENSÃO
===================================================

"""
        if st.session_state.respondentes:
            df_scores = pd.DataFrame([r['scores'] for r in st.session_state.respondentes])
            medias = df_scores.mean().sort_values(ascending=True)

            for dimensao, score in medias.items():
                relatorio += f"- {dimensao}: {score:.1f}/100\n"

        relatorio += "\n\nINVENTÁRIO DE RISCOS IDENTIFICADOS\n===================================\n\n"

        for i, r in enumerate(st.session_state.inventario_riscos, 1):
            relatorio += f"""
{i}. {r['dimensao']}
   Fator de Risco: {r['fator_risco']}
   Evidências: {r['evidencias']}
   Probabilidade: {r['probabilidade']}/5
   Severidade: {r['severidade']}/5
   Nível de Risco: {r['nivel_risco']['nivel']}

"""

        relatorio += "\nPLANOS DE AÇÃO 5W2H\n===================\n"
        for i, p in enumerate(st.session_state.planos_acao, 1):
            relatorio += f"""
Plano {i}:
  O QUÊ: {p['what']}
  POR QUÊ: {p['why']}
  ONDE: {p['where']}
  QUANDO: {p['when']}
  QUEM: {p['who']}
  COMO: {p['how']}
  QUANTO: {p['how_much']}
  Risco Relacionado: {p['risco_relacionado']}

"""

        relatorio += f"""
RECOMENDAÇÕES
=============
- Priorizar ações para riscos CRÍTICOS e ALTOS
- Estabelecer cronograma de monitoramento trimestral
- Realizar nova avaliação COPSOQ III em 6-12 meses
- Implementar ciclo PDCA para melhoria contínua

FUNDAMENTOS LEGAIS E METODOLÓGICOS
===================================
Brasil: NR-1 (GRO/PGR), NR-17 (Ergonomia), CLT Art. 157-158
Internacional: OIT (C155, C187), EU-OSHA Framework Directive 89/391/EEC
Metodologia: COPSOQ III (Copenhagen) - Versão Brasil validada por Dra. Teresa Cotrim
ISO 45003:2021 - Gestão de Saúde e Segurança Psicológica no Trabalho

---
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Material confidencial - Uso restrito para pesquisa e consultoria profissional
"""

        st.download_button(
            label="✅ Clique aqui para baixar o Relatório",
            data=relatorio.encode('utf-8'),
            file_name=f"Relatorio_COPSOQ_III_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

with col2:
    if st.session_state.respondentes:
        st.info(f"✅ {len(st.session_state.respondentes)} respondentes avaliados")
        st.info(f"⚠️ {len(st.session_state.inventario_riscos)} riscos identificados")
        st.info(f"📋 {len(st.session_state.planos_acao)} planos de ação criados")

st.divider()
st.caption("""
**COPSOQ III - Copenhagen Psychosocial Questionnaire (Versão Média Brasil)** 🔬 Validação: Dra. Teresa Cotrim | Parceria Internacional  
🇧🇷 Adaptação para países de língua portuguesa  
⚠️ Material validado cientificamente - Uso restrito  
📚 31 Dimensões | 84 Questões | Protocolo Internacional
""")