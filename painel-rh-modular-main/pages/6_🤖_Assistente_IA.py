# pages/6__Assistente_IA.py
"""
Assistente IA com memória persistente, contexto de análises E verificação de fontes.
"""
import streamlit as st
import sys
import os
from datetime import datetime
import logging
import time

# --- Path setup ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from components.ui_components import UIComponents
from services.api_client import APIClient
from services.storage import get_persistent_storage
from services.conversation_memory import ConversationMemory
from services.knowledge_base import SimpleKnowledgeBase
from config.settings import AppConfig

logger = logging.getLogger(__name__)

# --- Inicialização ---
ui = UIComponents()
api_client = APIClient()
storage = get_persistent_storage()
config = AppConfig()

# Inicializa Base de Conhecimento (OTIMIZADO - só uma vez)
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = SimpleKnowledgeBase()

kb = st.session_state.knowledge_base

# Inicializa memória (persiste entre sessões)
if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory(user_id="default")

memory = st.session_state.conversation_memory


def get_analysis_context(analysis_id: str = None) -> str:
    """Obtém contexto de análises salvas"""
    analyses = storage.get_analyses()
    
    if not analyses:
        return "Nenhuma análise disponível no momento."
    
    if analysis_id:
        # Busca análise específica
        analysis = next((a for a in analyses if a.id == analysis_id), None)
        if analysis:
            return format_analysis_summary(analysis)
        return f"Análise {analysis_id} não encontrada."
    
    # Retorna resumo das últimas análises
    recent = sorted(analyses, key=lambda x: x.timestamp, reverse=True)[:3]
    summaries = [format_analysis_summary(a) for a in recent]
    return "\n\n".join(summaries)


def format_analysis_summary(analysis) -> str:
    """Formata resumo de uma análise"""
    summary = f"""
Análise: {analysis.name}
Tipo: {analysis.type.value}
Data: {analysis.timestamp.strftime('%d/%m/%Y %H:%M')}
Risco: {analysis.risk_level.label if analysis.risk_level else 'N/A'}
"""
    
    # Adiciona dados principais (primeiros 3 itens)
    if analysis.data:
        data_items = list(analysis.data.items())[:3]
        for key, value in data_items:
            if isinstance(value, (int, float)):
                summary += f"   {key}: {value:.2f}\n"
    
    return summary.strip()


def render_document_sources(kb_results, auto_expand=True, message_id=None):
    """Renderiza painel com documentos fonte encontrados (CORRIGIDO - sem botão duplicado)"""
    if not kb_results:
        st.info("️ Nenhum documento consultado para esta resposta (baseada em conhecimento geral da IA)")
        return
    
    # Gera ID único para esta renderização
    if message_id is None:
        message_id = str(datetime.now().timestamp()).replace('.', '')
    
    # Banner destacado
    st.success(f" {len(kb_results)} documento(s) consultado(s) - Confira abaixo as fontes!")
    
    with st.expander(f" **FONTES: Documentos Consultados ({len(kb_results)})**", expanded=auto_expand):
        st.warning("️ **IMPORTANTE:** Sempre confira os trechos abaixo para validar se a resposta da IA está correta!")
        
        for i, result in enumerate(kb_results, 1):
            doc = result['document']
            snippet = result['snippet']
            score = result['score']
            
            # Container com borda destacada
            with st.container():
                st.markdown(f"###  {i}. {doc['title']}")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.caption(f"**Categoria:** {doc['category']}")
                with col2:
                    st.caption(f"**Relevância:** {score} pts")
                with col3:
                    st.caption(f"**Total:** {doc['word_count']:,} palavras")
                
                if doc.get('tags'):
                    st.caption(f"️ **Tags:** {', '.join(doc['tags'])}")
                
                # Exibe snippet com destaque visual
                st.markdown("####  Trecho Relevante Encontrado:")
                st.info(snippet)
                
                # Expander para documento completo
                with st.expander(" Ver documento completo"):
                    st.text_area(
                        "Conteúdo completo do documento (Use Ctrl+A e Ctrl+C para copiar)",
                        value=doc['content'],
                        height=400,
                        disabled=True,
                        key=f"doc_full_{message_id}_{doc['id']}_{i}",
                        help="Texto completo do documento para conferência. Use Ctrl+A e Ctrl+C para copiar."
                    )
                
                if i < len(kb_results):
                    st.divider()


def call_ai_with_memory(user_prompt: str, analysis_context: str = ""):
    """
    Chama IA com contexto de memória E base de conhecimento (COM RETRY).
    Retorna: (resposta, kb_results) - tupla com resposta e documentos encontrados
    """
    
    # Configuração de retry
    max_retries = 3
    retry_delay = 1  # segundos
    
    for attempt in range(1, max_retries + 1):
        try:
            # Busca na base de conhecimento
            kb_results = kb.search(user_prompt, top_k=5)
            
            kb_context = ""
            if kb_results:
                kb_context = "\n" + "="*100 + "\n"
                kb_context += "DOCUMENTOS DA BASE DE CONHECIMENTO DISPONIVEIS\n"
                kb_context += "="*100 + "\n\n"
                
                for i, result in enumerate(kb_results, 1):
                    doc = result['document']
                    snippet = result['snippet']
                    
                    kb_context += f"""
DOCUMENTO #{i}: {doc['title']}
Categoria: {doc['category']} | Relevancia: {result['score']} pontos
Total de palavras no documento: {doc['word_count']}

CONTEUDO DO DOCUMENTO (TRECHOS RELEVANTES):

{snippet}

{"="*100}

"""
            
            # Obtém histórico recente
            recent_context = memory.get_recent_context(n=6)
            
            # Monta prompt completo COM ANTI-LERO-LERO
            prompt_text = f"""Voce e um consultor especializado em Recursos Humanos e psicologia organizacional.

{kb_context}

{"="*100}
HISTORICO DA CONVERSA:
{"="*100}
{recent_context}

{"="*100}
CONTEXTO DAS ANALISES DISPONIVEIS:
{"="*100}
{analysis_context if analysis_context else "Nenhuma analise carregada no momento."}

{"="*100}
NOVA PERGUNTA DO USUARIO:
{"="*100}
{user_prompt}

{"="*100}
INSTRUCOES OBRIGATORIAS - LEIA COM ATENCAO:
{"="*100}

1. SE voce recebeu DOCUMENTOS DA BASE DE CONHECIMENTO acima:
   - Voce DEVE usar essas informacoes para responder
   - Voce TEM ACESSO COMPLETO a esses trechos
   - NUNCA diga que nao tem acesso ou nao possui o texto completo
   - CITE especificamente os trechos e artigos mostrados acima

2. O documento completo tem milhares de palavras (veja Total de palavras)
   - Os trechos mostrados sao as partes MAIS RELEVANTES
   - Se a resposta esta nos trechos acima, ela esta disponivel para voce
   - NAO peca o documento completo - voce ja tem o necessario

3. Como responder corretamente:
   CORRETO: De acordo com o Art. X do documento Y: [texto exato do documento]
   CORRETO: Conforme o trecho acima: [citacao direta]
   ERRADO: Nao tenho acesso ao documento completo...
   ERRADO: Preciso do texto integral para responder...
   ERRADO: O documento so mostra o preambulo...

4. Se os documentos NAO contiverem a resposta:
   - AI SIM voce pode dizer que nao encontrou
   - Mas baseie sua resposta no conhecimento geral

5. Use os dados das analises quando apropriado

6. Mantenha contexto do historico da conversa

7. Seja especifico e forneca recomendacoes acionaveis

8. ADAPTE seu estilo a pergunta:
   - Pergunta simples/objetiva: Resposta direta em 1-3 paragrafos curtos
   - Pergunta complexa/analise: Resposta detalhada com fundamentacao completa
   - Use seu julgamento: gestores as vezes precisam de velocidade, as vezes de profundidade

{"="*100}
PROIBICOES ABSOLUTAS - NAO FACA ISSO:
{"="*100}

NUNCA diga: Com base na minha experiencia...
NUNCA diga: E praticamente certo que...
NUNCA diga: Invariavelmente contem...
NUNCA diga: A pratica padrao e...
NUNCA diga: Embora o trecho nao mostre...
NUNCA diga: Tipicamente os estatutos...
NUNCA diga: De forma geral a legislacao...
NUNCA use raciocinio generico quando o documento tem a resposta

SE O DOCUMENTO ACIMA CONTEM A RESPOSTA:
- CITE O ARTIGO/TRECHO EXATO mostrado acima
- USE as palavras do documento (pode ate copiar entre aspas)
- NAO raciocine genericamente sobre o que estatutos normalmente dizem

EXEMPLO DE RESPOSTA CORRETA:
Usuario: O estatuto proibe bebida alcoolica?
Voce: Sim. De acordo com o Art. XI mostrado no documento acima: ingerir bebida alcoolica ou fazer uso de substancia entorpecente durante o horario de trabalho ou apresentar-se habitualmente sob sua influencia ao servico e proibido.

EXEMPLO DE RESPOSTA ERRADA (NAO FACA ISSO):
Usuario: O estatuto proibe bebida alcoolica?
Voce: Com base na minha experiencia, estatutos de servidores invariavelmente contem artigos que proibem...

{"="*100}
SUA RESPOSTA (use os documentos acima e siga as instrucoes):
{"="*100}"""

            # CHAMA A API (com possível retry)
            response = api_client.call_gemini(prompt_text)
            
            if response:
                # Sucesso! Retorna a resposta E os documentos encontrados
                if attempt > 1:
                    logger.info(f"Sucesso na tentativa {attempt}/{max_retries}")
                return response, kb_results
            else:
                # Resposta vazia, tenta novamente
                logger.warning(f"Tentativa {attempt}/{max_retries} retornou vazia")
                if attempt < max_retries:
                    time.sleep(retry_delay * attempt)
                    continue
                else:
                    return "Desculpe, nao consegui processar sua pergunta apos varias tentativas. Por favor, tente novamente em alguns instantes.", kb_results
        
        except ConnectionError as e:
            logger.error(f"Erro de conexao (tentativa {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
                continue
            else:
                return "Erro de conexao com a API apos varias tentativas. Verifique sua internet e tente novamente.", []
        
        except ValueError as e:
            logger.error(f"Erro de validacao (tentativa {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
                continue
            else:
                return "Erro ao processar a requisicao apos varias tentativas. Verifique suas configuracoes de API.", []
        
        except Exception as e:
            logger.error(f"Erro inesperado (tentativa {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
                continue
            else:
                return f"Ocorreu um erro inesperado apos varias tentativas. Por favor, tente novamente. (Detalhe: {str(e)[:100]})", []
    
    # Fallback (nunca deve chegar aqui)
    return "Desculpe, nao foi possivel processar sua pergunta. Tente novamente.", []


# --- Interface Principal ---
ui.render_header(
    "Assistente IA com Memoria", 
    "Converse sobre suas analises de RH com contexto persistente e verificacao de fontes"
)

# BANNER DE AVISO DESTACADO
st.warning("""
️ **IMPORTANTE - SEMPRE CONFIRA AS FONTES!**

Este assistente usa IA para analisar documentos e dados. **Para consultas legais ou normativas (estatutos, leis, regulamentos):**
-  Sempre confira o painel **" FONTES: Documentos Consultados"** que aparece abaixo de cada resposta
-  Verifique se a citação da IA corresponde ao trecho original do documento
-  Em caso de dúvida, consulte o texto completo do documento ou um profissional jurídico

A IA fornece **análises e recomendações**, mas as **fontes oficiais** são sempre os documentos originais.
""")

# Sidebar com controles
with st.sidebar:
    st.subheader("Controles")
    
    # Estatísticas da conversa
    stats = memory.get_statistics()
    if stats['total_messages'] > 0:
        st.metric("Mensagens", stats['total_messages'])
        st.caption(f"Desde: {stats['first_message']}")
    else:
        st.info("Nenhuma conversa ainda")
    
    st.divider()
    
    # Seleção de análise para contexto
    analyses = storage.get_analyses()
    if analyses:
        analysis_options = {
            "Todas as analises recentes": None,
            **{f"{a.name} ({a.type.value})": a.id for a in sorted(analyses, key=lambda x: x.timestamp, reverse=True)[:10]}
        }
        selected_label = st.selectbox("Focar em analise:", list(analysis_options.keys()))
        selected_analysis_id = analysis_options[selected_label]
    else:
        st.warning("Nenhuma analise salva")
        selected_analysis_id = None
    
    st.divider()
    
    # Info sobre documentos
    kb_stats = kb.get_statistics()
    if kb_stats['total_documents'] > 0:
        st.metric("Documentos na Base", kb_stats['total_documents'])
        st.caption(f"{kb_stats['total_words']:,} palavras")
        
        with st.expander("Ver categorias"):
            for cat, count in kb_stats.get('categories', {}).items():
                st.caption(f" {cat}: {count}")
    else:
        st.info("Nenhum documento na base ainda")
    
    st.divider()
    
    # Ações
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Limpar", width='stretch'):
            memory.clear()
            st.session_state.conversation_memory = ConversationMemory(user_id="default")
            st.rerun()
    
    with col2:
        if st.button("Exportar", width='stretch'):
            if stats['total_messages'] > 0:
                export_path = memory.export_conversation()
                st.success(f"Exportado!")
                st.caption(export_path)
            else:
                st.warning("Nada para exportar")

# Perguntas sugeridas (se não há histórico)
if memory.get_statistics()['total_messages'] == 0 and analyses:
    st.subheader("Perguntas Sugeridas")
    
    suggestions = [
        "Quais sao os principais riscos identificados nas analises?",
        "Como esta a saude organizacional geral?",
        "Que acoes devo priorizar com base nos dados?",
        "Compare as ultimas analises de absentismo",
        "O estatuto permite acumulo de ferias?"
    ]
    
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(f"{suggestion}", key=f"sug_{i}"):
                # Adiciona à conversa
                memory.add_message("user", suggestion)
                st.rerun()

st.divider()

# Área de conversação
st.subheader("Conversa")

# Renderiza histórico
for msg in memory.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Mostra timestamp em pequeno
        st.caption(datetime.fromisoformat(msg["timestamp"]).strftime("%d/%m/%Y %H:%M"))
        
        # Se tem metadados de documentos, mostra fontes (não expandido automaticamente no histórico)
        if msg["role"] == "assistant" and msg.get("metadata", {}).get("kb_results"):
            render_document_sources(
                msg["metadata"]["kb_results"], 
                auto_expand=False, 
                message_id=msg.get("timestamp", "")
            )

# Input do usuário
if prompt := st.chat_input("Faca uma pergunta sobre seus dados de RH..."):
    # Adiciona mensagem do usuário
    memory.add_message("user", prompt, metadata={"analysis_id": selected_analysis_id})
    
    # Mostra imediatamente
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Resposta da IA
    with st.chat_message("assistant"):
        with st.spinner("Pensando e consultando documentos..."):
            # Obtém contexto da análise selecionada
            analysis_context = get_analysis_context(selected_analysis_id)
            
            # Chama IA e recebe documentos encontrados
            response, kb_results = call_ai_with_memory(prompt, analysis_context)
            
            # Mostra resposta
            st.markdown(response)
            
            # Mostra fontes consultadas (SEMPRE EXPANDIDO para nova resposta)
            render_document_sources(
                kb_results, 
                auto_expand=True, 
                message_id=str(datetime.now().timestamp())
            )
            
            # Salva na memória COM referência aos documentos
            memory.add_message(
                "assistant", 
                response, 
                metadata={
                    "analysis_id": selected_analysis_id,
                    "kb_results": kb_results
                }
            )

# Informação de rodapé
if analyses:
    with st.expander("Analises Disponiveis"):
        for analysis in sorted(analyses, key=lambda x: x.timestamp, reverse=True)[:5]:
            st.caption(f" {analysis.name} ({analysis.type.value}) - {analysis.timestamp.strftime('%d/%m/%Y')}")


