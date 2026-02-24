"""
Diagnóstico Avançado - Identificar causa do chiado
"""

import streamlit as st
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

st.title(" Diagnóstico Avançado - Chiado")

# API
try:
    api_key = st.secrets["ELEVENLABS_API_KEY"]
    client = ElevenLabs(api_key=api_key)
    st.success(" API conectada")
except Exception as e:
    st.error(f" {str(e)}")
    st.stop()

st.markdown("---")
st.subheader(" Teste de Modelos e Formatos")

# Configurações
texto_teste = st.text_area(
    "Texto para testar",
    value="Olá, este é um teste de qualidade de áudio. A Reforma Tributária vai mudar tudo.",
    height=100
)

voice_id = st.text_input(
    "Voice ID",
    value="m151rjrbWXbBqyq56tly",
    help="Carla Institucional"
)

# Teste de modelos
st.markdown("### ️ Teste 1: Diferentes Modelos")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(" Modelo Multilingual V2"):
        st.info("Gerando com eleven_multilingual_v2...")
        try:
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=texto_teste,
                voice_settings=VoiceSettings(
                    stability=0.7,
                    similarity_boost=0.75,
                    style=0.3,
                    use_speaker_boost=True
                ),
                output_format="mp3_44100_128"
            )
            audio_bytes = b"".join(audio)
            st.audio(audio_bytes, format="audio/mp3")
            st.success(f" {len(audio_bytes):,} bytes")
        except Exception as e:
            st.error(f" {str(e)}")

with col2:
    if st.button(" Modelo Turbo V2.5"):
        st.info("Gerando com eleven_turbo_v2_5...")
        try:
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_turbo_v2_5",
                text=texto_teste,
                voice_settings=VoiceSettings(
                    stability=0.7,
                    similarity_boost=0.75,
                    style=0.3,
                    use_speaker_boost=True
                ),
                output_format="mp3_44100_128"
            )
            audio_bytes = b"".join(audio)
            st.audio(audio_bytes, format="audio/mp3")
            st.success(f" {len(audio_bytes):,} bytes")
        except Exception as e:
            st.error(f" {str(e)}")

with col3:
    if st.button(" Modelo Multilingual V1"):
        st.info("Gerando com eleven_multilingual_v1...")
        try:
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v1",
                text=texto_teste,
                voice_settings=VoiceSettings(
                    stability=0.7,
                    similarity_boost=0.75
                ),
                output_format="mp3_44100_128"
            )
            audio_bytes = b"".join(audio)
            st.audio(audio_bytes, format="audio/mp3")
            st.success(f" {len(audio_bytes):,} bytes")
        except Exception as e:
            st.error(f" {str(e)}")

# Teste de formatos
st.markdown("---")
st.markdown("###  Teste 2: Diferentes Formatos de Saída")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("MP3 44100 128"):
        st.info("Formato: mp3_44100_128...")
        try:
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=texto_teste,
                voice_settings=VoiceSettings(
                    stability=0.7,
                    similarity_boost=0.75,
                    style=0.3,
                    use_speaker_boost=True
                ),
                output_format="mp3_44100_128"
            )
            audio_bytes = b"".join(audio)
            st.audio(audio_bytes, format="audio/mp3")
            st.success(f" {len(audio_bytes):,} bytes")
        except Exception as e:
            st.error(f" {str(e)}")

with col2:
    if st.button("MP3 44100 192"):
        st.info("Formato: mp3_44100_192...")
        try:
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=texto_teste,
                voice_settings=VoiceSettings(
                    stability=0.7,
                    similarity_boost=0.75,
                    style=0.3,
                    use_speaker_boost=True
                ),
                output_format="mp3_44100_192"
            )
            audio_bytes = b"".join(audio)
            st.audio(audio_bytes, format="audio/mp3")
            st.success(f" {len(audio_bytes):,} bytes")
        except Exception as e:
            st.error(f" {str(e)}")

with col3:
    if st.button("PCM 44100"):
        st.info("Formato: pcm_44100...")
        try:
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=texto_teste,
                voice_settings=VoiceSettings(
                    stability=0.7,
                    similarity_boost=0.75,
                    style=0.3,
                    use_speaker_boost=True
                ),
                output_format="pcm_44100"
            )
            audio_bytes = b"".join(audio)
            st.audio(audio_bytes, format="audio/wav")
            st.success(f" {len(audio_bytes):,} bytes")
        except Exception as e:
            st.error(f" {str(e)}")

# Teste de estabilidade
st.markdown("---")
st.markdown("### ️ Teste 3: Ajuste de Estabilidade")

stability_test = st.slider("Stability", 0.0, 1.0, 0.7, 0.05)
similarity_test = st.slider("Similarity Boost", 0.0, 1.0, 0.75, 0.05)

if st.button(" Testar com Configurações Personalizadas", type="primary"):
    st.info("Gerando...")
    try:
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=texto_teste,
            voice_settings=VoiceSettings(
                stability=stability_test,
                similarity_boost=similarity_test,
                use_speaker_boost=True
            ),
            output_format="mp3_44100_192"
        )
        audio_bytes = b"".join(audio)
        st.audio(audio_bytes, format="audio/mp3")
        st.success(f" Gerado: {len(audio_bytes):,} bytes")
        
        st.info(f"**Configurações usadas:** Stability={stability_test}, Similarity={similarity_test}")
    except Exception as e:
        st.error(f" {str(e)}")

# Informações
st.markdown("---")
st.info("""
**Como usar este diagnóstico:**

1. **Teste os 3 modelos** - veja qual tem menos chiado
2. **Teste os formatos** - MP3 192kbps geralmente é melhor
3. **Ajuste a estabilidade** - valores entre 0.6-0.8 funcionam melhor
4. **Anote qual combinação funcionou melhor**

**Se TODOS tiverem chiado:**
- Pode ser problema no Voice ID
- Tente outras vozes (Jessica, etc)
- Verifique se a voz não está "clonada" com áudio de baixa qualidade
""")


