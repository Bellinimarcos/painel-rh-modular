"""
Diagnóstico completo da API ElevenLabs
Verifica créditos, permissões e conexão
"""

import streamlit as st
from elevenlabs.client import ElevenLabs
import requests

st.title(" Diagnóstico Completo - ElevenLabs")

# ==================== VERIFICAR API KEY ====================
st.subheader("1️ Verificar API Key")

try:
    api_key = st.secrets["ELEVENLABS_API_KEY"]
    st.success(f" API Key encontrada: {api_key[:20]}...")
    
    # Mostrar API Key completa (ocultar parte)
    st.code(f"sk-...{api_key[-10:]}")
    
except Exception as e:
    st.error(f" Erro ao carregar API Key: {str(e)}")
    st.stop()

# ==================== CONECTAR CLIENT ====================
st.markdown("---")
st.subheader("2️ Conectar ao ElevenLabs")

try:
    client = ElevenLabs(api_key=api_key)
    st.success(" Cliente conectado!")
except Exception as e:
    st.error(f" Erro ao conectar: {str(e)}")
    st.stop()

# ==================== VERIFICAR CONTA ====================
st.markdown("---")
st.subheader("3️ Informações da Conta")

if st.button(" Buscar Informações da Conta", type="primary"):
    try:
        user = client.user.get()
        
        st.success(" Conta encontrada!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Plano", user.subscription.tier)
            st.metric("Caracteres Usados", f"{user.subscription.character_count:,}")
        
        with col2:
            st.metric("Limite de Caracteres", f"{user.subscription.character_limit:,}")
            
            # Calcular percentual usado
            if user.subscription.character_limit > 0:
                percentual = (user.subscription.character_count / user.subscription.character_limit) * 100
                st.metric("% Usado", f"{percentual:.1f}%")
        
        # Verificar se tem créditos
        if user.subscription.character_count >= user.subscription.character_limit:
            st.error(" CRDITOS ESGOTADOS! Sua conta atingiu o limite mensal.")
            st.info(" Aguarde o reset mensal ou faça upgrade do plano.")
        else:
            restante = user.subscription.character_limit - user.subscription.character_count
            st.success(f" Você ainda tem {restante:,} caracteres disponíveis!")
        
        # Mostrar detalhes completos
        with st.expander(" Detalhes Completos da Conta"):
            st.json({
                "tier": user.subscription.tier,
                "character_count": user.subscription.character_count,
                "character_limit": user.subscription.character_limit,
                "can_extend_character_limit": user.subscription.can_extend_character_limit,
                "allowed_to_extend_character_limit": user.subscription.allowed_to_extend_character_limit,
                "next_character_count_reset_unix": user.subscription.next_character_count_reset_unix,
            })
        
    except Exception as e:
        st.error(f" Erro ao buscar informações: {str(e)}")
        st.code(str(e))

# ==================== LISTAR VOZES ====================
st.markdown("---")
st.subheader("4️ Listar Vozes Disponíveis")

if st.button(" Listar Vozes"):
    try:
        voices = client.voices.get_all()
        
        st.success(f" Encontradas {len(voices.voices)} vozes!")
        
        for voice in voices.voices[:5]:  # Mostrar apenas 5 primeiras
            st.write(f"**{voice.name}** - ID: `{voice.voice_id}`")
        
        if len(voices.voices) > 5:
            st.info(f"... e mais {len(voices.voices) - 5} vozes")
        
    except Exception as e:
        st.error(f" Erro ao listar vozes: {str(e)}")
        st.code(str(e))

# ==================== TESTE DE CONEXO ====================
st.markdown("---")
st.subheader("5️ Teste de Conexão Direta")

if st.button(" Testar Conexão com API", type="secondary"):
    st.info("Testando conexão direta com a API...")
    
    try:
        url = "https://api.elevenlabs.io/v1/user"
        headers = {
            "xi-api-key": api_key
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        st.write(f"**Status Code:** {response.status_code}")
        
        if response.status_code == 200:
            st.success(" Conexão OK!")
            data = response.json()
            st.json(data)
        elif response.status_code == 401:
            st.error(" API Key INVÁLIDA!")
            st.warning("Verifique se a API Key está correta no secrets.toml")
        elif response.status_code == 403:
            st.error(" API Key SEM PERMISSO!")
            st.warning("Esta API Key não tem permissão para usar TTS")
        else:
            st.error(f" Erro: {response.status_code}")
            st.code(response.text)
            
    except requests.exceptions.Timeout:
        st.error(" TIMEOUT - Conexão muito lenta")
    except Exception as e:
        st.error(f" Erro: {str(e)}")

# ==================== TESTE SIMPLES DE ÁUDIO ====================
st.markdown("---")
st.subheader("6️ Teste Simples de Geração")

texto_simples = st.text_input("Texto curto para testar", "Olá")
voice_id_teste = st.text_input("Voice ID", "21m00Tcm4TlvDq8ikWAM")

if st.button(" Gerar Áudio Teste", type="primary"):
    st.info("Gerando...")
    
    try:
        from elevenlabs import VoiceSettings
        
        audio = client.text_to_speech.convert(
            voice_id=voice_id_teste,
            model_id="eleven_turbo_v2_5",
            text=texto_simples,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.5
            ),
            output_format="mp3_44100_192"
        )
        
        audio_bytes = b"".join(audio)
        
        st.write(f"**Tamanho:** {len(audio_bytes):,} bytes")
        
        if len(audio_bytes) > 1000:
            st.success(" Áudio gerado!")
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.error(" Áudio muito pequeno (corrompido)")
            
    except Exception as e:
        st.error(f" ERRO: {str(e)}")
        st.code(str(e))
        
        # Mostrar detalhes do erro
        import traceback
        with st.expander(" Detalhes do Erro"):
            st.code(traceback.format_exc())

# ==================== RESUMO ====================
st.markdown("---")
st.info("""
** Checklist de Problemas:**

 = Funcionou |  = Problema

1. [ ] API Key carregada
2. [ ] Cliente conectado  
3. [ ] Créditos disponíveis
4. [ ] Vozes listadas
5. [ ] Conexão com API OK
6. [ ] Áudio gerado

**Se algum item falhar, esse é o problema!**
""")


