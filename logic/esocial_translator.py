# logic/esocial_translator.py

"""
Módulo responsável pela lógica de "tradução" dos riscos psicossociais,
identificados por ferramentas como o COPSOQ, para a terminologia e
codificação exigidas pelo evento S-2240 do eSocial.
"""

# Dicionário que mapeia as dimensões de risco para os códigos e textos do eSocial.
# Esta é a "inteligência" da tradução. Versão completa para o COPSOQ III - Média.
ESOCIAL_MAP = {
    # --- GRUPO 1: EXIGÊNCIAS E RECURSOS ---
    'Ritmo de Trabalho': {
        'codigo': '05.01.001',
        'descricao_codigo': 'Ritmo de trabalho penoso',
        'template_texto': (
            "Exposição a fator de risco ergonômico (código 05.01.001), caracterizado por ritmo de trabalho penoso "
            "imposto por demandas de produção, com prazos exíguos para tarefas de alta complexidade e ausência "
            "de pausas adequadas para recuperação psicofisiológica."
        ),
        'justificativa': "Este código é aplicável pois a dimensão 'Ritmo de Trabalho' do COPSOQ avalia diretamente a intensidade e a pressão temporal das tarefas, que são os elementos centrais do conceito de 'ritmo penoso' da NR-17."
    },
    'Exigências Quantitativas': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Exposição a fator de risco ergonômico organizacional (código 05.01.004), caracterizado por "
            "excessiva carga de trabalho quantitativa. Evidenciado pelo volume elevado de tarefas, "
            "acúmulo de trabalho e pressão constante para cumprimento de metas com prazos exíguos, "
            "impactando a organização do tempo e a jornada laboral."
        ),
        'justificativa': "As exigências quantitativas (volume, sobrecarga) são um elemento central da organização do trabalho. O código 05.01.004 é o mais adequado para registrar este tipo de risco."
    },
    'Exigências Emocionais': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Exposição a fator de risco ergonômico organizacional (código 05.01.004), evidenciado pela elevada "
            "exigência emocional no contato direto e constante com público ou clientes em situações de conflito, "
            "requerendo controle emocional para mediação."
        ),
        'justificativa': "As exigências emocionais são um aspecto da organização do trabalho, especialmente em serviços. O código 05.01.004 é o mais adequado para abranger este fator."
    },
    'Exigências Cognitivas': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Exposição a fator de risco ergonômico organizacional (código 05.01.004), relacionado a elevadas "
            "exigências cognitivas da tarefa. O trabalho requer atenção constante, memorização de informações, "
            "proposição de novas ideias e tomada de decisões difíceis, sobrecarregando os processos mentais."
        ),
        'justificativa': "As exigências cognitivas são um aspecto central da organização do trabalho, conforme a NR-17. O código 05.01.004 é o mais adequado para registrar este tipo de demanda."
    },
    'Influência no Trabalho': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) devido à baixa "
            "influência no trabalho. O trabalhador possui pouca ou nenhuma autonomia para influenciar "
            "decisões, a quantidade de tarefas, a forma de execução do trabalho e seu conteúdo."
        ),
        'justificativa': "A falta de controle e autonomia sobre o próprio trabalho é um conhecido fator de risco psicossocial, diretamente ligado à forma como o trabalho é organizado."
    },
    'Possibilidades de Desenvolvimento': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) associado a "
            "baixas possibilidades de desenvolvimento. O trabalho oferece poucas oportunidades para "
            "aprender coisas novas e para aplicar e desenvolver as competências do trabalhador."
        ),
        'justificativa': "Um trabalho que não permite o desenvolvimento profissional pode levar à desmotivação e ao estresse, sendo um risco ligado ao conteúdo das tarefas."
    },
    'Controlo sobre o Tempo de Trabalho': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) relacionado ao baixo "
            "controle sobre o tempo de trabalho. O trabalhador possui pouca flexibilidade para decidir "
            "o momento de suas pausas ou a marcação de suas férias."
        ),
        'justificativa': "A falta de controle sobre a própria jornada e pausas é um fator de estresse que afeta a recuperação psicofisiológica, tratando-se de uma regra da organização do trabalho."
    },

    # --- GRUPO 2: AMBIENTE SOCIAL, LIDERANÇA E CULTURA ---
    'Qualidade da Liderança': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) relacionado à baixa "
            "qualidade da liderança. As práticas de gestão apresentam deficiências no planejamento do trabalho, "
            "na resolução de conflitos, na oferta de oportunidades de desenvolvimento e na valorização da satisfação da equipe."
        ),
        'justificativa': "A qualidade da liderança é um dos principais pilares da organização do trabalho, impactando diretamente o clima, a clareza das tarefas e o suporte social."
    },
    'Suporte Social de Colegas': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) por baixo suporte social "
            "por parte dos pares. O ambiente de trabalho é caracterizado pela dificuldade em obter ajuda e apoio "
            "dos colegas e por um baixo grau de colaboração e escuta mútua."
        ),
        'justificativa': "Um ambiente com baixo suporte social entre colegas pode levar ao isolamento e agravar os efeitos do estresse, sendo um fator de risco ligado às relações socioprofissionais."
    },
    'Suporte Social de Superiores': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Exposição a fator de risco ergonômico organizacional (código 05.01.004) devido ao baixo suporte "
            "social da chefia imediata. Há pouca frequência de ajuda, apoio e diálogo sobre o desempenho e "
            "problemas de trabalho por parte do superior direto."
        ),
        'justificativa': "A falta de suporte do superior direto é um forte preditor de estresse e insatisfação, ligado diretamente ao papel da liderança na organização do trabalho."
    },
    'Sentido de Pertença a Comunidade': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) relacionado ao baixo "
            "sentido de pertencimento à comunidade. O ambiente de trabalho apresenta deficiências no clima "
            "organizacional, na cooperação entre colegas e no sentimento de fazer parte de uma equipe."
        ),
        'justificativa': "O senso de comunidade e pertencimento afeta a colaboração e a segurança psicológica, sendo um fator de risco ligado à cultura organizacional."
    },
    'Significado do Trabalho': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) associado à percepção de "
            "baixo significado do trabalho. As tarefas são vistas como pouco importantes ou sem propósito, "
            "gerando baixa motivação e engajamento."
        ),
        'justificativa': "A percepção de significado é um fator de proteção. Sua ausência é um risco ligado ao conteúdo e propósito das tarefas, um componente da organização do trabalho."
    },
    'Compromisso face ao Local de Trabalho': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) que se manifesta em um "
            "baixo compromisso com o local de trabalho. Há pouco orgulho em pertencer à organização e "
            "relutância em falar positivamente sobre a empresa."
        ),
        'justificativa': "O baixo compromisso é um sintoma de problemas mais profundos na cultura e organização do trabalho (ex: falta de reconhecimento, injustiça)."
    },
    'Previsibilidade': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) devido à baixa "
            "previsibilidade. A comunicação sobre decisões importantes, mudanças e planos futuros é "
            "insuficiente ou não ocorre com a devida antecedência, gerando um clima de incerteza."
        ),
        'justificativa': "A falta de previsibilidade impacta a capacidade de planejamento do trabalhador e gera estresse, sendo um risco ligado aos processos de comunicação e gestão."
    },
    'Reconhecimento': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) associado ao baixo "
            "reconhecimento. As práticas de gestão não valorizam ou apreciam o trabalho realizado, "
            "gerando percepção de desrespeito e tratamento injusto."
        ),
        'justificativa': "O reconhecimento é um fator de proteção essencial. Sua ausência é um risco organizacional crônico que afeta a motivação, o engajamento e a saúde mental."
    },
    'Transparência do Papel Laboral': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Exposição a fator de risco ergonômico organizacional (código 05.01.004) por falta de "
            "transparência do papel laboral. Os objetivos de trabalho são pouco claros e há ambiguidade "
            "sobre as responsabilidades e o que se espera do trabalhador."
        ),
        'justificativa': "A ambiguidade de papel é uma fonte significativa de estresse e conflitos, ligada à clareza na definição das tarefas e na organização do trabalho."
    },
    'Conflitos de Papéis Laborais': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) relacionado à inadequação do "
            "conteúdo e da clareza das tarefas, gerando demandas de trabalho contraditórias, sobreposição de funções "
            "e incerteza sobre as responsabilidades."
        ),
        'justificativa': "Conflitos de papéis são um clássico problema de organização do trabalho, enquadrando-se perfeitamente no escopo do código 05.01.004."
    },
    'Justiça Organizacional': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) relacionado à baixa "
            "justiça organizacional. Há percepção de que a resolução de conflitos, a distribuição de tarefas "
            "e o reconhecimento pelo bom trabalho não são conduzidos de forma justa e isonômica."
        ),
        'justificativa': "A percepção de injustiça é um forte estressor e afeta profundamente o clima organizacional e a confiança, sendo um risco diretamente relacionado às políticas e práticas de gestão."
    },
    'Insegurança Laboral': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) manifestado como "
            "insegurança laboral. O ambiente de trabalho e/ou o contexto organizacional geram preocupação "
            "constante sobre a manutenção do emprego."
        ),
        'justificativa': "A insegurança laboral é um risco psicossocial que pode ser agravado pela gestão da comunicação e estabilidade da empresa, afetando a saúde do trabalhador."
    },
    'Insegurança com as Condições de Trabalho': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) devido à insegurança "
            "com as condições de trabalho. Há preocupação com a possibilidade de alterações contratuais "
            "involuntárias (função, horário, remuneração)."
        ),
        'justificativa': "A incerteza sobre as condições de trabalho gera ansiedade e estresse, ligada à falta de transparência e previsibilidade nas políticas de gestão de pessoas."
    },
    'Qualidade do Trabalho': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) relacionado à baixa "
            "qualidade do trabalho. A organização do trabalho e as condições oferecidas levam a uma "
            "baixa satisfação do trabalhador com a qualidade do serviço que consegue realizar."
        ),
        'justificativa': "A impossibilidade de realizar um trabalho de qualidade, por falta de recursos ou tempo, é um estressor ético e profissional ligado à organização do trabalho."
    },
    'Confiança Horizontal': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Exposição a fator de risco ergonômico organizacional (código 05.01.004) por baixo nível de "
            "confiança horizontal. O ambiente de trabalho é caracterizado pela desconfiança entre colegas "
            "e pela ocultação de informações, prejudicando a colaboração."
        ),
        'justificativa': "A confiança entre pares é a base para o trabalho em equipe eficaz. Sua ausência indica problemas nas relações socioprofissionais e na cultura da empresa."
    },
    'Confiança Vertical': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) devido ao baixo nível de "
            "confiança vertical. A relação entre trabalhadores e gestão é marcada pela desconfiança mútua "
            "e pela dificuldade dos empregados em expressar suas opiniões livremente."
        ),
        'justificativa': "A confiança vertical é fundamental para a segurança psicológica e a comunicação eficaz. A falta dela é um grave risco organizacional que inibe a melhoria contínua."
    },
    'Conflito Trabalho-Família': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Presença de fator de risco ergonômico organizacional (código 05.01.004) que gera conflito "
            "trabalho-família. As exigências de tempo e energia do trabalho afetam negativamente "
            "a vida privada e familiar do trabalhador."
        ),
        'justificativa': "O desequilíbrio trabalho-vida pessoal é um risco ligado à organização da jornada, volume de trabalho e cultura de longas horas, sendo um fator organizacional."
    },

    # --- GRUPO 3: RESULTADOS E PERCEPÇÕES INDIVIDUAIS ---
    'Satisfação com o trabalho': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) que se manifesta em "
            "baixa satisfação com o trabalho. A organização do trabalho e as condições oferecidas "
            "resultam em baixa satisfação com as perspectivas, o uso das habilidades e o emprego como um todo."
        ),
        'justificativa': "A baixa satisfação é um indicador de resultado de outros riscos organizacionais (falta de reconhecimento, baixo desenvolvimento, etc.) e deve ser registrada como tal."
    },
    'Auto-Avaliação da Saúde': {
        'codigo': 'N/A',
        'descricao_codigo': 'Não aplicável diretamente ao S-2240',
        'template_texto': (
            "Esta dimensão é um indicador de saúde e um resultado da exposição aos riscos. Deve ser usada "
            "pelo PCMSO (S-2220) para direcionar ações de saúde, e não como um fator de risco no PGR (S-2240)."
        ),
        'justificativa': "O evento S-2240 descreve os riscos do ambiente, enquanto a autoavaliação da saúde é um desfecho na saúde do trabalhador, a ser gerenciado pelo PCMSO."
    },
    'Auto-Eficácia': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) que afeta negativamente "
            "a autoeficácia. O ambiente de trabalho, por meio de baixa autonomia ou suporte, mina a "
            "percepção do trabalhador de sua capacidade de resolver problemas e atingir objetivos."
        ),
        'justificativa': "A autoeficácia é uma característica pessoal, mas é fortemente influenciada por fatores organizacionais como suporte da liderança e autonomia."
    },
    'Problemas de Sono': {
        'codigo': 'N/A',
        'descricao_codigo': 'Não aplicável diretamente ao S-2240',
        'template_texto': (
            "Esta dimensão é um sintoma e um indicador de saúde. Deve ser usada pelo PCMSO (S-2220) para "
            "ações de vigilância da saúde. A causa-raiz (ex: sobrecarga, estresse) deve ser registrada como o risco no PGR (S-2240)."
        ),
        'justificativa': "O evento S-2240 descreve os riscos do ambiente, enquanto problemas de sono são um desfecho na saúde do trabalhador, a ser gerenciado pelo PCMSO."
    },
    'Burnout': {
        'codigo': '05.01.004',
        'descricao_codigo': 'Fatores ergonômicos organizacionais',
        'template_texto': (
            "Identificado fator de risco ergonômico organizacional (código 05.01.004) associado à organização do trabalho, "
            "com indícios de esgotamento profissional (Burnout), decorrente de sobrecarga laboral crônica, "
            "conflitos de papéis e baixo suporte social, conforme metodologia de avaliação aplicada."
        ),
        'justificativa': "O Burnout é um desfecho de saúde, mas sua causa-raiz está em fatores organizacionais. Portanto, descrevemos o risco na organização do trabalho que leva a esse desfecho."
    },
    'Stress': {
        'codigo': 'N/A',
        'descricao_codigo': 'Não aplicável diretamente ao S-2240',
        'template_texto': (
            "Esta dimensão é um sintoma e um indicador de saúde. Deve ser usada pelo PCMSO (S-2220) para "
            "ações de vigilância da saúde. A causa-raiz (ex: ritmo penoso, baixo suporte) deve ser registrada como o risco no PGR (S-2240)."
        ),
        'justificativa': "O evento S-2240 descreve os riscos do ambiente, enquanto o estresse é um desfecho na saúde do trabalhador, a ser gerenciado pelo PCMSO."
    },
    'Sintomas Depressivos': {
        'codigo': 'N/A',
        'descricao_codigo': 'Não aplicável diretamente ao S-2240',
        'template_texto': (
            "Esta dimensão é um sintoma e um indicador de saúde. Deve ser usada pelo PCMSO (S-2220) para "
            "ações de vigilância da saúde. A causa-raiz (ex: injustiça, assédio) deve ser registrada como o risco no PGR (S-2240)."
        ),
        'justificativa': "O evento S-2240 descreve os riscos do ambiente, enquanto sintomas depressivos são um desfecho na saúde do trabalhador, a ser gerenciado pelo PCMSO."
    },
}

def traduzir_risco_para_esocial(risco_inventario: dict):
    """
    Recebe um dicionário de risco do inventário e retorna as informações formatadas para o eSocial.

    Args:
        risco_inventario (dict): Um dicionário representando um risco, 
                                 deve conter a chave 'dimensao'.

    Returns:
        dict: Um dicionário com as informações traduzidas para o formato eSocial.
    """
    # A chave para a tradução é a 'dimensao' do risco
    dimensao = risco_inventario.get('dimensao')

    # Se a dimensão estiver em nosso mapa, retorna a tradução específica
    if dimensao in ESOCIAL_MAP:
        return ESOCIAL_MAP[dimensao]
    
    # Se não houver um mapa específico, retorna um padrão genérico (fallback)
    else:
        return {
            'codigo': '05.01.004',
            'descricao_codigo': 'Fatores ergonômicos organizacionais',
            'template_texto': (
                f"Identificado fator de risco ergonômico organizacional (código 05.01.004) relacionado à dimensão '{dimensao}'. "
                f"Evidências apontam para problemas na organização do trabalho que requerem análise e plano de ação específico, "
                f"conforme descrito no PGR."
            ),
            'justificativa': "Este é um código padrão para riscos organizacionais não mapeados diretamente. A descrição deve ser refinada pelo profissional de SST com base nas evidências coletadas."
        }