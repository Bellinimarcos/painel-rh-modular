# pages/7__Base_de_Conhecimento.py
"""
Interface para gerenciar base de conhecimento do assistente IA.
Permite upload de documentos (TXTs, MDs, PDFs) que o bot pode consultar.
"""
import streamlit as st
import sys
import os
from datetime import datetime

# --- Path setup ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from components.ui_components import UIComponents
from services.knowledge_base import SimpleKnowledgeBase

# --- Inicialização ---
ui = UIComponents()

# Inicializa KB no session_state (otimização do Gemini)
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = SimpleKnowledgeBase()

kb = st.session_state.knowledge_base


def render_upload_section():
    """Seção de upload de documentos"""
    st.subheader(" Adicionar Documento")
    
    with st.form(key="doc_upload_form"):
        title = st.text_input(
            "Título do Documento *",
            placeholder="Ex: Política de Férias 2025"
        )
        
        category = st.selectbox(
            "Categoria",
            ["Política", "Procedimento", "Manual", "Guia", "FAQ", "Regulamento", "Outro"]
        )
        
        # Métodos de input
        input_method = st.radio(
            "Método de entrada:",
            ["️ Digitar texto", " Upload de arquivo"],
            horizontal=True
        )
        
        content = ""
        
        if input_method == "️ Digitar texto":
            content = st.text_area(
                "Conteúdo do documento",
                height=300,
                placeholder="Cole ou digite o conteúdo aqui..."
            )
        else:
            # UPLOAD DE ARQUIVO (TXT, MD, PDF)
            uploaded_file = st.file_uploader(
                "Selecione arquivo",
                type=['txt', 'md', 'pdf'],
                help="Arquivos de texto (.txt, .md, .pdf)"
            )
            
            if uploaded_file:
                try:
                    # Detecta tipo de arquivo
                    file_type = uploaded_file.name.split('.')[-1].lower()
                    
                    if file_type == 'pdf':
                        # Lê PDF com pdfplumber (MUITO MELHOR)
                        import pdfplumber
                        
                        with pdfplumber.open(uploaded_file) as pdf:
                            content = ""
                            for page in pdf.pages:
                                text = page.extract_text()
                                if text:
                                    # Limpa tabs e espaços extras
                                    text = text.replace('\t', ' ')
                                    # Remove múltiplos espaços
                                    text = ' '.join(text.split())
                                    content += text + "\n\n"
                        
                        st.info(f" PDF lido: {len(content)} caracteres, {len(content.split())} palavras")
                    else:
                        # Lê TXT/MD
                        content = uploaded_file.read().decode('utf-8')
                        st.info(f" Arquivo lido: {len(content)} caracteres")
                        
                except UnicodeDecodeError:
                    try:
                        uploaded_file.seek(0)
                        content = uploaded_file.read().decode('latin-1')
                        st.info(f" Arquivo lido (latin-1): {len(content)} caracteres")
                    except Exception as e:
                        st.error(f"Erro ao ler arquivo: {e}")
                except Exception as e:
                    st.error(f"Erro ao processar PDF: {e}")
        
        # TAGS
        tags_input = st.text_input(
            "Tags (separadas por vírgula)",
            placeholder="rh, férias, benefícios"
        )
        
        tags = [t.strip() for t in tags_input.split(',') if t.strip()]
        
        # BOTO SUBMIT
        submitted = st.form_submit_button(" Adicionar à Base", type="primary", width='stretch')
        
        if submitted:
            if not title:
                st.error(" Título é obrigatório")
            elif not content or len(content) < 10:
                st.error(" Conteúdo muito curto (mínimo 10 caracteres)")
            else:
                try:
                    doc_id = kb.add_document(
                        title=title,
                        content=content,
                        category=category,
                        tags=tags
                    )
                    st.success(f" Documento adicionado: {title}")
                    st.info(f"ID: {doc_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao adicionar documento: {e}")


def render_search_section():
    """Seção de busca na base"""
    st.subheader(" Buscar Documentos")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Pesquisar",
            placeholder="Digite palavras-chave...",
            label_visibility="collapsed"
        )
    
    with col2:
        categories = kb.get_all_categories()
        category_filter = st.selectbox(
            "Categoria",
            ["Todas"] + categories if categories else ["Todas"],
            label_visibility="collapsed"
        )
    
    if query:
        cat = None if category_filter == "Todas" else category_filter
        results = kb.search(query, top_k=5, category=cat)
        
        if results:
            st.success(f"Encontrados {len(results)} documento(s)")
            
            for result in results:
                doc = result['document']
                score = result['score']
                snippet = result['snippet']
                
                with st.container():
                    st.markdown(f"###  {doc['title']}")
                    st.caption(f"Categoria: {doc['category']} | Relevância: {score} pontos")
                    
                    if doc.get('tags'):
                        tags_str = ", ".join(doc['tags'])
                        st.caption(f"️ Tags: {tags_str}")
                    
                    st.markdown(f"**Trecho relevante:**")
                    st.info(snippet)
                    
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        if st.button("️ Remover", key=f"del_{doc['id']}"):
                            if kb.delete_document(doc['id']):
                                st.success("Documento removido")
                                st.rerun()
                    
                    with col2:
                        with st.expander(" Ver conteúdo completo"):
                            st.text_area(
                                "Conteúdo",
                                value=doc['content'],
                                height=300,
                                disabled=True,
                                key=f"full_{doc['id']}"
                            )
                    
                    st.divider()
        else:
            st.warning("Nenhum documento encontrado com esses critérios")
    elif query == "":
        st.info(" Digite palavras-chave acima para buscar documentos")


def render_library_section():
    """Seção de biblioteca completa"""
    st.subheader(" Biblioteca Completa")
    
    stats = kb.get_statistics()
    
    if stats['total_documents'] == 0:
        st.info(" Nenhum documento na base ainda. Adicione documentos na aba 'Adicionar'.")
        return
    
    # Estatísticas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Documentos", stats['total_documents'])
    
    with col2:
        st.metric("Total de Palavras", f"{stats['total_words']:,}")
    
    with col3:
        st.metric("Média Palavras/Doc", stats['avg_words_per_doc'])
    
    # Documentos por categoria
    if stats.get('categories'):
        st.markdown("** Documentos por Categoria:**")
        for cat, count in sorted(stats['categories'].items()):
            st.text(f" {cat}: {count}")
    
    st.divider()
    
    # Filtro de categoria
    categories = kb.get_all_categories()
    selected_cat = st.selectbox(
        "Filtrar por categoria:",
        ["Todas"] + categories if categories else ["Todas"]
    )
    
    # Lista documentos filtrados
    st.markdown("** Documentos:**")
    
    docs_to_show = kb.documents if selected_cat == "Todas" else kb.get_by_category(selected_cat)
    
    if not docs_to_show:
        st.info(f"Nenhum documento na categoria '{selected_cat}'")
    else:
        for doc in docs_to_show:
            with st.expander(f" {doc['title']} ({doc['category']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.caption(f" Criado em: {doc['created_at'][:10]}")
                    st.caption(f" Palavras: {doc['word_count']}")
                
                with col2:
                    if doc.get('tags'):
                        st.caption(f"️ Tags: {', '.join(doc['tags'])}")
                
                st.text_area(
                    "Conteúdo",
                    value=doc['content'],
                    height=200,
                    disabled=True,
                    key=f"content_{doc['id']}"
                )
                
                if st.button("️ Remover documento", key=f"remove_{doc['id']}"):
                    if kb.delete_document(doc['id']):
                        st.success("Documento removido")
                        st.rerun()


# --- Interface Principal ---
ui.render_header(
    " Base de Conhecimento",
    "Gerencie documentos que o Assistente IA pode consultar"
)

st.info("""
**Como funciona:**

1. **Adicione documentos** com políticas, procedimentos ou manuais da sua organização
2. **O Assistente IA** busca automaticamente informações nestes documentos ao responder
3. **Organize por categorias e tags** para facilitar a busca

**Dica:** Quanto mais específico e bem organizado o conteúdo, melhores as respostas da IA.
""")

# Mostra integração com IA
with st.expander(" Como o Assistente IA usa estes documentos"):
    st.markdown("""
    Quando você pergunta algo ao Assistente IA, ele:
    
    1.  **Busca** palavras-chave da sua pergunta nesta base
    2.  **Encontra** os documentos mais relevantes
    3.  **Responde** usando o conteúdo desses documentos
    
    **Exemplo:**
    - Você adiciona: "Política de Férias - 30 dias por ano"
    - Você pergunta: "Quantos dias de férias tenho?"
    - IA responde: "De acordo com a Política de Férias, você tem direito a 30 dias por ano"
    """)

st.divider()

# Tabs para organizar interface
tab1, tab2, tab3 = st.tabs([" Adicionar", " Buscar", " Biblioteca"])

with tab1:
    render_upload_section()

with tab2:
    render_search_section()

with tab3:
    render_library_section()

# Footer com estatísticas rápidas
st.divider()
stats = kb.get_statistics()
if stats['total_documents'] > 0:
    st.caption(f" Base de conhecimento: {stats['total_documents']} documento(s) | {stats['total_words']:,} palavras")


