# Este arquivo armazena as perguntas dos questionários
# Por favor, substitua as perguntas de exemplo pelas perguntas reais.

# Mapeamento de opções para pontuação (exemplo)
OPCOES_SEMPRE = ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"]
PONTUACAO_5_SEMPRE = {"Nunca": 1, "Raramente": 2, "Às vezes": 3, "Frequentemente": 4, "Sempre": 5}

OPCOES_EXTREMAMENTE = ["Nada", "Um pouco", "Moderadamente", "Muito", "Extremamente"]
PONTUACAO_5_EXTREMAMENTE = {"Nada": 1, "Um pouco": 2, "Moderadamente": 3, "Muito": 4, "Extremamente": 5}

OPCOES_SAUDE = ["Fraca", "Razoável", "Boa", "Muito boa", "Excelente"]
PONTUACAO_5_SAUDE = {"Fraca": 1, "Razoável": 2, "Boa": 3, "Muito boa": 4, "Excelente": 5}


# --- COPSOQ II (VERSÃO CURTA) ---
# Atualizado com as perguntas reais fornecidas
COPSOQ_II_CURTO = {
    "Ritmo de Trabalho": {
        "perguntas": [
            "Você tem que trabalhar muito rápido?",
            "O seu trabalho exige que você trabalhe em um ritmo acelerado?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Exigências Cognitivas": {
        "perguntas": [
            "O seu trabalho exige que você memorize muitas coisas?",
            "O seu trabalho exige que você tome decisões difíceis?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Exigências Emocionais": {
        "perguntas": [
            "Seu trabalho está em situações emocionais difíceis?",
            "Você precisa lidar com os problemas pessoais de outras pessoas no seu trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Influência": {
        "perguntas": [
            "Você tem influência sobre as coisas que afetam seu trabalho?",
            "Você tem influência sobre seu ritmo de trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Possibilidades de Desenvolvimento": {
        "perguntas": [
            "O seu trabalho te dá a possibilidade de aprender coisas novas?",
            "Seu trabalho lhe dá a oportunidade de desenvolver suas competências?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Sentido do Trabalho": {
        "perguntas": [
            "O seu trabalho é significativo para você?",
            "Você sente que o trabalho que você faz é importante?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Comprometimento com o Local de Trabalho": {
        "perguntas": [
            "Você gosta de falar sobre seu trabalho com outras pessoas?",
            "Você se sente orgulhoso(a) de trabalhar nesta organização?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Previsibilidade": {
        "perguntas": [
            "Você recebe com antecedência as informações sobre decisões importantes?",
            "Você recebe todas as informações necessárias para fazer bem o seu trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Clareza de Papel": {
        "perguntas": [
            "Você sabe exatamente o que espera de você no trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Conflito de Papel": {
        "perguntas": [
            "Você recebe tarefas com critérios contraditórios?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Qualidade da Liderança": {
        "perguntas": [
            "O seu chefe imediatamente é bom em planejar o trabalho?",
            "O seu chefe imediato é bom em resolver conflitos?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Apoio Social do Superior": {
        "perguntas": [
            "Você consegue ajuda e apoio do seu chefe imediatamente, se necessário?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Apoio Social dos Colegas": {
        "perguntas": [
            "Você consegue ajuda e apoio de seus colegas, se necessário?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Sentido de Comunidade": {
        "perguntas": [
            "Existe um bom ambiente de trabalho entre você e seus colegas?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Insegurança no Emprego": {
        "perguntas": [
            "Você está preocupado(a) em perder seu emprego?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Conflito Trabalho-Família": {
        "perguntas": [
            "Como a exigência do seu trabalho interfere na sua vida familiar e doméstica?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Satisfação no Trabalho": {
        "perguntas": [
            "De um modo geral, o quão satisfeito(a) você está com seu trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Saúde em Geral": {
        "perguntas": [
            "Em geral, como você diria que é a sua saúde?",
        ],
        "opcoes": OPCOES_SEMPRE, # De acordo com o texto, usa a mesma escala
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Esgotamento": {
        "perguntas": [
            "Com que frequência você se sente físico e emocionalmente esgotado(a)?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Estresse": {
        "perguntas": [
            "Com que frequência você se sente tenso(a) ou estressado(a)?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Problemas de Sono": {
        "perguntas": [
            "Com que frequência você dorme mal e acorda cansado(a)?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Sintomas Depressivos": {
        "perguntas": [
            "Com que frequência você se sente triste ou deprimido(a)?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Assédio Moral": {
        "perguntas": [
            "Você já foi submetido(a) a assédio moral (bullying) no seu trabalho nos últimos 12 meses?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
}

# --- COPSOQ III (VERSÃO LONGA) ---
# Atualizado com as perguntas reais fornecidas
COPSOQ_III_LONGO = {
    "Exigências Quantitativas": {
        "perguntas": [
            "EQ1. A sua carga de trabalho é distribuída de maneira desejada e pode se acumular?",
            "EQ2. Você fica com trabalho atrasado?",
            "EQ3. Com que frequência você não tem tempo para completar todas as suas tarefas de trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Ritmo de Trabalho": {
        "perguntas": [
            "R1. Você tem que trabalhar muito rápido?",
            "R2. Você trabalha a um ritmo muito rápido ao longo do dia?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Exigências Cognitivas": {
        "perguntas": [
            "EC1. O seu trabalho exige sua atenção constante?",
            "EC2. O seu trabalho exige que você lembre de muitas coisas?",
            "EC3. O seu trabalho exige que você crie novas ideias?",
            "EC4. O seu trabalho exige que você tenha que tomar decisões difíceis?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Exigências Emocionais": {
        "perguntas": [
            "EE1. O seu trabalho coloca você em situações emocionais perturbadoras?",
            "EE2. Você tem lidado com os problemas pessoais dos outros como parte do seu trabalho?",
            "EE3. O seu trabalho é exigente emocionalmente?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Influência no Trabalho": {
        "perguntas": [
            "TI1. Você tem grande influência nas decisões sobre seu trabalho?",
            "TI2. Você tem influência sobre a quantidade de trabalho que ele é atribuído?",
            "TI3. Você tem alguma influência sobre O QUE faz no trabalho?",
            "TI4. Você tem influência sobre COMO faz o seu trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Possibilidades de Desenvolvimento": {
        "perguntas": [
            "PD1. Você tem a possibilidade de aprender coisas novas por meio do seu trabalho?",
            "PD2. Você consegue usar suas habilidades ou sua experiência no trabalho?",
            "PD3. Seu trabalho lhe dá a oportunidade de desenvolver suas habilidades?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Controle sobre o Tempo de Trabalho": {
        "perguntas": [
            "CTT1. Você pode decidir quando fazer uma pausa?",
            "CTT2. Você pode tirar férias próximas a dados que quiser?",
            "CTT3. Pode fazer uma pausa no trabalho para falar com um/a colega?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Significado do Trabalho": {
        "perguntas": [
            "ST1. O seu trabalho é significativo para você?",
            "ST2. Você sente que o trabalho que você faz é importante?",
            "ST3. Sente-se motivado e envolvido com o seu trabalho?",
        ],
        "opcoes": OPCOES_EXTREMAMENTE,
        "pontuacao": PONTUACAO_5_EXTREMAMENTE
    },
    "Compromisso face ao Local de Trabalho": {
        "perguntas": [
            "CLT1. Você gosta de falar para os outros sobre seu local de trabalho?",
            "CLT3. Você tem orgulho de fazer parte desta organização?",
        ],
        "opcoes": OPCOES_EXTREMAMENTE,
        "pontuacao": PONTUACAO_5_EXTREMAMENTE
    },
    "Previsibilidade": {
        "perguntas": [
            "Anterior1. No seu local de trabalho, você é informado com antecedência suficiente sobre decisões importantes, alterações ou planos para o futuro?",
            "Anterior2. Você recebe todas as informações de que precisa para terminar bem o seu trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Reconhecimento": {
        "perguntas": [
            "Rec1. O seu trabalho é reconhecido e apreciado pela gerência?",
            "Rec2. Você é respeitado por sua gestão?",
            "Rec3. Você é tratado de maneira justa no seu local de trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Transparência do Papel Laboral": {
        "perguntas": [
            "Transp1. Seu trabalho tem objetivos claros?",
            "Transp2. Você sabe exatamente quais são as áreas de sua responsabilidade?",
            "Transp3. Você sabe exatamente o que espera de você no seu trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Conflitos de Papéis Laborais": {
        "perguntas": [
            "CPL1. São solicitadas critérios contraditórios no seu trabalho?",
            "CPL2. Às vezes você precisa fazer coisas de maneira diferente do que elas deveriam ser feitas?",
            "CPL3. Às vezes você precisa fazer coisas que sejam supérfluas?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Qualidade da Liderança": {
        "perguntas": [
            "QL1. Em relação à sua chefia direta, até que ponto considera que garante que os membros da equipe tenham boas oportunidades de desenvolvimento?",
            "QL2. Em relação à sua chefia direta, até que ponto considera que é adequado no planejamento do trabalho?",
            "QL3. Em relação à sua chefia direta, até que ponto considera que é adequado na resolução de conflitos?",
            "QL4. Em relação à sua chefia direta, até que ponto considera que prioriza a satisfação com o trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Suporte Social de Colegas": {
        "perguntas": [
            "SSC1. Em caso de necessidade, com que frequência você conseguiria apoio e ajuda de seus colegas?",
            "SSC2. Em caso de necessidade, com que frequência seus colegas estariam interessados ​​em ouvir sobre seus problemas no trabalho?",
            "SSC3. Com que frequência seus colegas falam com você sobre seu nível de desempenho no trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Suporte Social de Superiores": {
        "perguntas": [
            "SSup1. Em caso de necessidade, com que frequência a sua supervisão imediata estaria disposto a ouvir sobre os seus problemas no trabalho?",
            "SSup2. Em caso de necessidade, com que frequência você conseguiria apoio e ajuda da sua supervisão imediata?",
            "SSup3. Com que frequência a sua supervisão imediata fala sobre o desempenho do seu trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Sentido de Pertença à Comunidade": {
        "perguntas": [
            "SPCom1. Há um clima bom entre você e seus colegas?",
            "SPCom2. Você se sente como parte de uma equipe no seu local de trabalho?",
            "SPCom3. Há uma boa cooperação entre os colegas no trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Insegurança Laboral": {
        "perguntas": [
            "IL1. Você está preocupado em ficar desempregado(a)?",
            "IL2. Você está preocupado com a dificuldade em encontrar outro emprego caso fique desempregado(a)?",
        ],
        "opcoes": OPCOES_EXTREMAMENTE,
        "pontuacao": PONTUACAO_5_EXTREMAMENTE
    },
    "Insegurança com as Condições de Trabalho": {
        "perguntas": [
            "ICL1. Você está preocupado em ser transferido(a) para outra função ou local contra sua vontade?",
            "ICL2. Você está preocupado/a com que o cronograma seja alterado (turno, dias de semana, horário de entrada e saída...) contra sua vontade?",
            "ICL3. Você está preocupado/a com uma diminuição no seu rendimento?",
        ],
        "opcoes": OPCOES_EXTREMAMENTE,
        "pontuacao": PONTUACAO_5_EXTREMAMENTE
    },
    "Qualidade do Trabalho": {
        "perguntas": [
            "QT1. Você está satisfeito (a) com a qualidade do trabalho realizado por si?",
        ],
        "opcoes": OPCOES_EXTREMAMENTE,
        "pontuacao": PONTUACAO_5_EXTREMAMENTE
    },
    "Confiança Horizontal": {
        "perguntas": [
            "CH1. Os trabalhadores trabalharam nos outros, no geral?",
            "CH2. Os funcionários esconderam informações uns dos outros?",
            "CH3. Os funcionários esconderam informações da gestão?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Confiança Vertical": {
        "perguntas": [
            "CV1. A gerência confia que os trabalhadores fazem um bom trabalho?",
            "CV2. Os funcionários foram incluídos nas informações recebidas da gerência?",
            "CV3. Os funcionários são capazes de expressar seus sentimentos e pontos de vista para a gerência?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Justiça Organizacional": {
        "perguntas": [
            "JO1. Os conflitos são resolvidos de modo justo?",
            "JO2. O trabalho é distribuído de maneira justa?",
            "JO3. As sugestões dos funcionários são trabalhados com seriedade pela gerência?",
            "JO4. Os trabalhadores são reconhecidos por fazer um bom trabalho?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Conflito Trabalho-Família": {
        "perguntas": [
            "CTF1. Você sente que seu trabalho tira tanto a sua energia que provoca um efeito negativo em sua vida privada?",
            "CTF2. O seu trabalho exige muito do seu tempo, o que afeta as qualidades de sua vida privada?",
            "CTF3. Como a critério do seu trabalho interfere na sua vida privada e familiar?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Satisfação com o trabalho": {
        "perguntas": [
            "Sábado1. Em relação ao seu trabalho em geral, quão satisfeito(a) está com suas perspectivas de trabalho?",
            "Sáb2. Em relação ao seu trabalho em geral, quão satisfeito(a) está com o seu trabalho como um todo, levando tudo em conta?",
            "Sábado3. Em relação ao seu trabalho em geral, quão satisfeito(a) está com o modo como suas habilidades são usadas?",
        ],
        "opcoes": OPCOES_EXTREMAMENTE,
        "pontuacao": PONTUACAO_5_EXTREMAMENTE
    },
    "Auto-Avaliação da Saúde": {
        "perguntas": [
            "Saúde. Em geral, você diria que a sua saúde é:",
        ],
        "opcoes": OPCOES_SAUDE,
        "pontuacao": PONTUACAO_5_SAUDE
    },
    "Auto-Eficácia": {
        "perguntas": [
            "AE1. Quando tenho um problema, normalmente consigo encontrar diversas maneiras de resolvê-lo",
            "AE2. É fácil para mim manter meus planos e alcançar meus objetivos",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Problemas de Sono": {
        "perguntas": [
            "Sono1. Com que frequência durante as últimas 4 semanas tem encontrado dificuldade para dormir?",
            "Sono2. Com que frequência durante as últimas 4 semanas acorda muito cedo e não é capaz de voltar a dormir?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Esgotamento": {
        "perguntas": [
            "Esgotamento1. Com que frequência durante as últimas 4 semanas se sente fisicamente exausto?",
            "Esgotamento2. Com que frequência durante as últimas 4 semanas se sente emocionalmente exausto?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Estresse": {
        "perguntas": [
            "Estresse1. Com que frequência durante as últimas 4 semanas se sente irritado/a?",
            "Estresse2. Com que frequência durante as últimas 4 semanas se sente ansioso/a?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
    "Sintomas Depressivos": {
        "perguntas": [
            "SD1. Com que frequência durante as últimas 4 semanas vem se sentindo triste?",
            "SD2. Com que frequência durante as últimas 4 semanas sente falta de interesse pelas coisas do dia a dia?",
        ],
        "opcoes": OPCOES_SEMPRE,
        "pontuacao": PONTUACAO_5_SEMPRE
    },
}


# --- OUTROS QUESTIONÁRIOS ---
# Você pode adicionar CBI, DUWAS, etc. da mesma forma
CBI_ESGOTAMENTO = {
     "Esgotamento Pessoal (CBI)": {
         "perguntas": ["Pergunta 1 de CBI...", "Pergunta 2 de CBI..."],
         "opcoes": OPCOES_SEMPRE,
         "pontuacao": PONTUACAO_5_SEMPRE
     }
     # ... outros domínios do CBI
}


# Mapeamento central para o SelectBox
QUESTIONARIOS_DISPONIVEIS = {
    "COPSOQ II (Versão Curta)": COPSOQ_II_CURTO,
    "COPSOQ III (Versão Longa)": COPSOQ_III_LONGO,
    "CBI (Esgotamento)": CBI_ESGOTAMENTO
    # Adicione outros aqui
}


