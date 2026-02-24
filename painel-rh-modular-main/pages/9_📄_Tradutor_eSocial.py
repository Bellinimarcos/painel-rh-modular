# pages/9__Tradutor_eSocial.py

import streamlit as st

# Tenta importar a função de tradução. Se este arquivo falhar em carregar,
# o erro provavelmente está no arquivo 'esocial_translator.py' ou na estrutura de pastas.
try:
    from logic.esocial_translator import traduzir_risco_para_esocial
except ImportError:
    st.error("ERRO CRÍTICO: Não foi possível importar a lógica de tradução. Verifique o arquivo 'logic/esocial_translator.py' e se a pasta 'logic' contém um arquivo `__init__.py` vazio.")
    st.stop()


# --- Configuração da Página ---
st.set_page_config(page_title="Tradutor para eSocial", page_icon="", layout="wide")


# --- Título e Descrição ---
st.title(" Assistente de Conformidade para o eSocial (S-2240)")
st.markdown("""
Esta ferramenta utiliza os dados do seu **Inventário de Riscos** para gerar sugestões de texto e códigos
compatíveis com o evento S-2240 do eSocial. O texto gerado deve ser **revisado e validado por um
profissional de Saúde e Segurança do Trabalho (SST)** antes de ser incluído no PGR e enviado ao eSocial.
""")

st.divider()


# --- Lógica Principal da Página ---

# 1. Verifica se o inventário de riscos existe e não está vazio.
#    A variável `st.session_state.inventario_riscos` é criada na página "Riscos Psicossociais".
if 'inventario_riscos' not in st.session_state or not st.session_state.inventario_riscos:
    st.warning("️ Nenhum risco encontrado no Inventário.", icon="️")
    st.info("Por favor, primeiro utilize a ferramenta de 'Riscos Psicossociais' para identificar e adicionar riscos ao inventário.")

# 2. Se o inventário tiver riscos, mostra a interface do tradutor.
else:
    inventario = st.session_state.inventario_riscos
    
    # Cria uma lista de nomes amigáveis para exibir no dropdown.
    # Ex: "RISCO #1 - Dimensão: Ritmo de Trabalho"
    try:
        opcoes_risco = [f"RISCO #{risco['id']} - Dimensão: {risco['dimensao']}" for risco in inventario]
    except KeyError:
        st.error("Erro nos dados do inventário. Certifique-se de que cada risco tem 'id' e 'dimensao'.")
        st.stop()


    st.subheader("1. Selecione o Risco a ser Traduzido")
    risco_selecionado_str = st.selectbox(
        "Selecione um risco do seu inventário:",
        options=opcoes_risco,
        index=0,
        help="Esta lista é populada com os riscos que você adicionou na ferramenta de Riscos Psicossociais."
    )

    # Encontra o objeto de risco completo com base na seleção do usuário.
    if risco_selecionado_str:
        risco_id_selecionado = int(risco_selecionado_str.split('#')[1].split(' ')[0])
        risco_obj = next((r for r in inventario if r['id'] == risco_id_selecionado), None)

        if risco_obj:
            st.subheader("2. Análise do Risco Original")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Dimensão COPSOQ:** {risco_obj.get('dimensao', 'N/A')}")
                st.info(f"**Fator de Risco:** {risco_obj.get('fator_risco', 'N/A')}")
            with col2:
                st.text_area("Evidências Coletadas:", value=risco_obj.get('evidencias', 'N/A'), height=120, disabled=True)

            st.divider()

            st.subheader("3. Resultado da Tradução para o eSocial (S-2240)")
            
            # Chama a função de tradução da nossa lógica.
            traducao = traduzir_risco_para_esocial(risco_obj)

            st.success(f"**Código eSocial Sugerido:** `{traducao['codigo']}` - {traducao['descricao_codigo']}")

            st.markdown("**Texto Sugerido para o PGR / Campo `dscAgNoc` do eSocial:**")
            st.text_area(
                "Texto para o PGR:",
                value=traducao['template_texto'],
                height=150,
                key=f"texto_traduzido_{risco_id_selecionado}", # Chave única para evitar bugs
                help="Este texto pode ser editado antes de ser copiado para o seu documento oficial."
            )

            st.markdown("**Justificativa Técnica da Sugestão:**")
            st.info(traducao['justificativa'], icon="")


