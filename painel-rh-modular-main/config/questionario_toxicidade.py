"""
Configuração do Questionário de Toxicidade em Lideranças
Projeto SER | Marcos Simões Bellini, CRP 04/37811
"""

from models.toxicidade_model import (
    QuestionarioToxicidade, Dimensao, Questao, TipoQuestao
)


# ============================================================================
# ESCALA LIKERT
# ============================================================================

ESCALA_LIKERT = {
    1: "Discordo Totalmente",
    2: "Discordo",
    3: "Neutro",
    4: "Concordo",
    5: "Concordo Totalmente"
}


# ============================================================================
# FUNO PRINCIPAL DE CRIAO DO QUESTIONÁRIO
# ============================================================================

def criar_questionario_toxicidade() -> QuestionarioToxicidade:
    """
    Cria e retorna o questionário completo de toxicidade
    
    Returns:
        QuestionarioToxicidade: Questionário configurado
    """
    
    # Cria questionário
    questionario = QuestionarioToxicidade(
        titulo="Avaliação de Toxicidade em Lideranças",
        descricao="Questionário estruturado para identificação de comportamentos tóxicos em ambientes de liderança organizacional",
        versao="2.0"
    )
    
    # ========== DIMENSO 1: COMUNICAO E FEEDBACK ==========
    dim_comunicacao = Dimensao(
        id="comunicacao",
        nome="Comunicação e Feedback",
        descricao="Avalia a qualidade e clareza da comunicação e feedback fornecidos pela liderança"
    )
    
    dim_comunicacao.questoes = [
        Questao(
            id=1,
            texto="Meu gestor comunica expectativas de forma clara e objetiva.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="comunicacao"
        ),
        Questao(
            id=2,
            texto="O feedback que recebo é construtivo e visa meu desenvolvimento profissional.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="comunicacao"
        ),
        Questao(
            id=3,
            texto="Meu gestor demonstra respeito na forma de se comunicar, mesmo em situações de tensão.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="comunicacao"
        ),
        Questao(
            id=4,
            texto="Há momentos em que o gestor usa sarcasmo, ironia ou expõe pessoas em reuniões.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="comunicacao"
        ),
        Questao(
            id=5,
            texto="Sinto que meu gestor ouve genuinamente minhas ideias e preocupações.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="comunicacao"
        )
    ]
    
    questionario.adicionar_dimensao(dim_comunicacao)
    
    # ========== DIMENSO 2: RECONHECIMENTO E VALORIZAO ==========
    dim_reconhecimento = Dimensao(
        id="reconhecimento",
        nome="Reconhecimento e Valorização",
        descricao="Mede o nível de reconhecimento e valorização do trabalho e esforços da equipe"
    )
    
    dim_reconhecimento.questoes = [
        Questao(
            id=6,
            texto="Meu gestor reconhece e valoriza meu trabalho e esforço.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="reconhecimento"
        ),
        Questao(
            id=7,
            texto="Sinto que meus resultados são frequentemente minimizados ou ignorados.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="reconhecimento"
        ),
        Questao(
            id=8,
            texto="Meu gestor atribui os sucessos da equipe a si mesmo(a).",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="reconhecimento"
        ),
        Questao(
            id=9,
            texto="Há equidade no reconhecimento entre os membros da equipe.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="reconhecimento"
        ),
        Questao(
            id=10,
            texto="Sinto que preciso me esforçar excessivamente para obter reconhecimento básico.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="reconhecimento"
        )
    ]
    
    questionario.adicionar_dimensao(dim_reconhecimento)
    
    # ========== DIMENSO 3: EQUIDADE E JUSTIA ==========
    dim_equidade = Dimensao(
        id="equidade",
        nome="Equidade e Justiça",
        descricao="Avalia a imparcialidade e justiça nas decisões e tratamento da equipe"
    )
    
    dim_equidade.questoes = [
        Questao(
            id=11,
            texto="Meu gestor trata todos os membros da equipe com equidade e imparcialidade.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="equidade"
        ),
        Questao(
            id=12,
            texto="Percebo favoritismo ou tratamento diferenciado entre colegas.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="equidade"
        ),
        Questao(
            id=13,
            texto="As decisões do meu gestor são baseadas em critérios claros e objetivos.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="equidade"
        ),
        Questao(
            id=14,
            texto="Sinto que algumas pessoas têm mais oportunidades do que outras sem justificativa clara.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="equidade"
        ),
        Questao(
            id=15,
            texto="Meu gestor responsabiliza pessoas de forma justa quando há problemas.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="equidade"
        )
    ]
    
    questionario.adicionar_dimensao(dim_equidade)
    
    # ========== DIMENSO 4: CONFIANA E TRANSPARNCIA ==========
    dim_confianca = Dimensao(
        id="confianca",
        nome="Confiança e Transparência",
        descricao="Mede o nível de confiança e transparência nas relações e comunicações"
    )
    
    dim_confianca.questoes = [
        Questao(
            id=16,
            texto="Confio nas informações e promessas do meu gestor.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="confianca"
        ),
        Questao(
            id=17,
            texto="Meu gestor é transparente sobre decisões que afetam a equipe.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="confianca"
        ),
        Questao(
            id=18,
            texto="Há falta de coerência entre o que meu gestor diz e faz.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="confianca"
        ),
        Questao(
            id=19,
            texto="Sinto que informações importantes são omitidas ou distorcidas.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="confianca"
        ),
        Questao(
            id=20,
            texto="Meu gestor admite erros e assume responsabilidades quando necessário.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="confianca"
        )
    ]
    
    questionario.adicionar_dimensao(dim_confianca)
    
    # ========== DIMENSO 5: EMPODERAMENTO E AUTONOMIA ==========
    dim_empoderamento = Dimensao(
        id="empoderamento",
        nome="Empoderamento e Autonomia",
        descricao="Avalia o nível de autonomia e empoderamento proporcionado à equipe"
    )
    
    dim_empoderamento.questoes = [
        Questao(
            id=21,
            texto="Meu gestor me dá autonomia para realizar meu trabalho.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="empoderamento"
        ),
        Questao(
            id=22,
            texto="Sinto que há microgerenciamento excessivo sobre meu trabalho.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="empoderamento"
        ),
        Questao(
            id=23,
            texto="Meu gestor confia em minha capacidade de tomar decisões.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="empoderamento"
        ),
        Questao(
            id=24,
            texto="Preciso de aprovação constante mesmo para tarefas simples.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="empoderamento"
        ),
        Questao(
            id=25,
            texto="Meu gestor me encoraja a buscar soluções e inovar.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="empoderamento"
        )
    ]
    
    questionario.adicionar_dimensao(dim_empoderamento)
    
    # ========== DIMENSO 6: PRESSO E ESTRESSE ==========
    dim_pressao = Dimensao(
        id="pressao",
        nome="Pressão e Estresse",
        descricao="Mede o nível de pressão inadequada e geração de estresse pela liderança"
    )
    
    dim_pressao.questoes = [
        Questao(
            id=26,
            texto="Meu gestor estabelece prazos e metas realistas e alcançáveis.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="pressao"
        ),
        Questao(
            id=27,
            texto="Sinto pressão excessiva e constante no ambiente de trabalho.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="pressao"
        ),
        Questao(
            id=28,
            texto="Meu gestor considera meu bem-estar ao definir demandas.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="pressao"
        ),
        Questao(
            id=29,
            texto="Há expectativas de disponibilidade além do horário de trabalho de forma recorrente.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="pressao"
        ),
        Questao(
            id=30,
            texto="Meu gestor usa táticas de intimidação ou ameaças para obter resultados.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="pressao"
        )
    ]
    
    questionario.adicionar_dimensao(dim_pressao)
    
    # ========== DIMENSO 7: RESPEITO E DIGNIDADE ==========
    dim_respeito = Dimensao(
        id="respeito",
        nome="Respeito e Dignidade",
        descricao="Avalia o nível de respeito e preservação da dignidade no ambiente de trabalho"
    )
    
    dim_respeito.questoes = [
        Questao(
            id=31,
            texto="Meu gestor trata todos com respeito e dignidade.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="respeito"
        ),
        Questao(
            id=32,
            texto="Já presenciei ou vivenciei situações de humilhação ou constrangimento.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="respeito"
        ),
        Questao(
            id=33,
            texto="Meu gestor valoriza a diversidade e as diferenças individuais.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="respeito"
        ),
        Questao(
            id=34,
            texto="Há comentários inapropriados ou piadas ofensivas vindos da liderança.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="respeito"
        ),
        Questao(
            id=35,
            texto="Sinto que posso expressar minhas opiniões sem medo de retaliação.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="respeito"
        )
    ]
    
    questionario.adicionar_dimensao(dim_respeito)
    
    # ========== DIMENSO 8: EXPECTATIVAS E CLAREZA ==========
    dim_expectativas = Dimensao(
        id="expectativas",
        nome="Expectativas e Clareza",
        descricao="Mede a clareza nas expectativas e objetivos estabelecidos pela liderança"
    )
    
    dim_expectativas.questoes = [
        Questao(
            id=36,
            texto="Meu gestor define expectativas claras sobre meu papel e responsabilidades.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="expectativas"
        ),
        Questao(
            id=37,
            texto="Frequentemente me sinto confuso(a) sobre o que é esperado de mim.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="expectativas"
        ),
        Questao(
            id=38,
            texto="As metas e objetivos são comunicados de forma consistente.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="expectativas"
        ),
        Questao(
            id=39,
            texto="Há mudanças frequentes de direção sem explicação adequada.",
            tipo=TipoQuestao.DIRETA,
            dimensao_id="expectativas"
        ),
        Questao(
            id=40,
            texto="Meu gestor me fornece os recursos necessários para atingir as expectativas.",
            tipo=TipoQuestao.INVERSA,
            dimensao_id="expectativas"
        )
    ]
    
    questionario.adicionar_dimensao(dim_expectativas)
    
    return questionario


# ============================================================================
# FUNO DE INTERPRETAO
# ============================================================================

def obter_interpretacao(nivel_risco: str) -> str:
    """
    Retorna interpretação textual do nível de risco
    
    Args:
        nivel_risco: Nível de risco (Excelente, Baixo, Moderado, Alto)
        
    Returns:
        str: Texto interpretativo
    """
    
    interpretacoes = {
        "Excelente": """
        ** Ambiente de Liderança Exemplar**
        
        Os resultados indicam uma liderança saudável e positiva. O ambiente apresenta 
        características de uma gestão eficaz, com comunicação clara, reconhecimento adequado, 
        e respeito mútuo. Continue fortalecendo essas práticas e sirva como exemplo para 
        outras lideranças na organização.
        
        **Recomendações:**
        - Mantenha as práticas atuais
        - Documente e compartilhe boas práticas
        - Continue desenvolvendo habilidades de liderança
        - Seja mentor de outras lideranças
        """,
        
        "Baixo": """
        ** Ambiente Aceitável com Pontos de Atenção**
        
        A situação geral está dentro de parâmetros aceitáveis, mas há aspectos que merecem 
        atenção.  importante identificar as áreas específicas com pontuações mais elevadas 
        e desenvolver planos de melhoria focados.
        
        **Recomendações:**
        - Identifique dimensões com pontuações mais altas
        - Implemente melhorias graduais e monitoradas
        - Estabeleça canais de feedback regular
        - Considere treinamento em áreas específicas
        """,
        
        "Moderado": """
        **️ Sinais Significativos de Toxicidade**
        
        Os resultados apontam para problemas consideráveis no ambiente de liderança que 
        requerem atenção imediata.  fundamental realizar uma avaliação mais aprofundada 
        e desenvolver um plano de ação estruturado com metas claras e prazos definidos.
        
        **Recomendações:**
        - Avaliação 360° da liderança
        - Plano de desenvolvimento individual (PDI)
        - Coaching ou mentoria especializada
        - Acompanhamento mensal do RH
        - Estabelecer métricas de melhoria
        """,
        
        "Alto": """
        ** SITUAO CRÍTICA - Intervenção Urgente Necessária**
        
        Os resultados indicam um ambiente de trabalho tóxico que pode estar causando danos 
        significativos à saúde mental e produtividade da equipe.  imperativo que ações 
        corretivas sejam tomadas IMEDIATAMENTE.
        
        **Recomendações Urgentes:**
        - Intervenção imediata do RH
        - Avaliação por profissional de psicologia organizacional
        - Entrevistas confidenciais com membros da equipe
        - Considerar afastamento temporário ou realocação da liderança
        - Suporte psicológico para equipe afetada
        - Plano de ação corretivo com prazo de 30-60 dias
        - Avaliação de possíveis danos e responsabilidades
        """
    }
    
    return interpretacoes.get(nivel_risco, "Interpretação não disponível.")


# ============================================================================
# FUNES AUXILIARES
# ============================================================================

def obter_descricao_escala(valor: int) -> str:
    """Retorna a descrição textual de um valor da escala"""
    return ESCALA_LIKERT.get(valor, "Valor inválido")


def validar_resposta(resposta: int) -> bool:
    """Valida se uma resposta está dentro da escala"""
    return resposta in ESCALA_LIKERT.keys()


