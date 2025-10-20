# C:\painel_rh_modular\pages\5_🎵_Estudio_de_Jingles.py

import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
import os
import io

# --- Funções Auxiliares ---

def text_to_speech(text, lang='pt-br'):
    """Converte texto em um objeto de áudio em memória."""
    try:
        tts = gTTS(text=text, lang=lang)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return AudioSegment.from_mp3(audio_fp)
    except Exception as e:
        st.error(f"Erro ao gerar a locução: {e}")
        return None

def process_audio(voice_audio, background_audio, sfx_audio=None, sfx_position='inicio', bg_volume=-10, intro_delay=500):
    """
    Realiza a mixagem do áudio da voz, música de fundo e efeitos sonoros.
    """
    # Ajusta o volume da música de fundo
    background_audio = background_audio + bg_volume

    # Garante que a música de fundo seja longa o suficiente
    final_duration = len(voice_audio) + intro_delay * 2
    if len(background_audio) < final_duration:
        # Repete a música se for mais curta que a locução
        background_audio = background_audio * (int(final_duration / len(background_audio)) + 1)
    
    # Corta a música de fundo para o tamanho final
    background_final = background_audio[:final_duration]

    # Sobrepõe a voz sobre a música com um pequeno atraso no início
    composition = background_final.overlay(voice_audio, position=intro_delay)

    # Adiciona o efeito sonoro se existir
    if sfx_audio:
        if sfx_position == 'Início':
            composition = sfx_audio.overlay(composition)
        else: # Fim
            # Calcula a posição para o SFX começar um pouco antes do fim da locução
            sfx_start_pos = intro_delay + len(voice_audio) - len(sfx_audio) + 300
            if sfx_start_pos < 0: sfx_start_pos = intro_delay + len(voice_audio)
            composition = composition.overlay(sfx_audio, position=sfx_start_pos)
            
    # Aplica um fade out suave no final
    composition = composition.fade_out(1500)
    
    return composition

# --- Interface do Streamlit ---

st.set_page_config(layout="wide", page_title="Estúdio de Jingles e Vinhetas")

st.title("🎵 Estúdio de Jingles e Vinhetas")
st.markdown("Crie áudios curtos, vinhetas e jingles para seus projetos de comunicação interna.")

# Layout em colunas
col1, col2 = st.columns([2, 1.5])

with col1:
    st.subheader("1. Conteúdo da Locução")
    script_text = st.text_area(
        "Digite o texto para ser narrado:",
        height=150,
        placeholder="Ex: 'Prefeitura de Itajubá, cuidando do que é nosso!'",
        key="script_text"
    )

    st.subheader("2. Arquivos de Áudio")
    background_music_file = st.file_uploader(
        "Escolha a música de fundo (MP3 ou WAV)",
        type=['mp3', 'wav'],
        key="bg_music"
    )
    
    sfx_file = st.file_uploader(
        "Escolha um efeito sonoro (opcional)",
        type=['mp3', 'wav'],
        key="sfx"
    )

with col2:
    st.subheader("3. Configurações de Mixagem")
    bg_volume = st.slider(
        "Volume da música de fundo (em dB)", 
        min_value=-40, max_value=0, value=-12,
        help="Valores mais baixos deixam a música mais suave em relação à voz."
    )
    
    sfx_position = st.selectbox(
        "Posição do efeito sonoro",
        ('Início', 'Fim'),
        disabled=(sfx_file is None), # Desabilita se não houver SFX
        key="sfx_pos"
    )
    
    intro_delay = st.slider(
        "Silêncio inicial (em milissegundos)",
        min_value=0, max_value=2000, value=500, step=100,
        help="Tempo de música antes da locução começar."
    )


st.divider()

if st.button("✨ Gerar Áudio", use_container_width=True, type="primary"):
    if not script_text:
        st.warning("Por favor, insira o texto da locução.")
    elif not background_music_file:
        st.warning("Por favor, faça o upload de uma música de fundo.")
    else:
        with st.spinner("Gerando locução e mixando o áudio... Aguarde! 🎧"):
            # 1. Gerar a locução
            voice_audio = text_to_speech(script_text)
            
            # 2. Carregar arquivos de áudio
            background_audio = AudioSegment.from_file(background_music_file)
            sfx_audio = AudioSegment.from_file(sfx_file) if sfx_file else None
            
            if voice_audio and background_audio:
                # 3. Processar e mixar o áudio
                final_audio = process_audio(
                    voice_audio, 
                    background_audio, 
                    sfx_audio, 
                    sfx_position, 
                    bg_volume, 
                    intro_delay
                )
                
                # 4. Exportar e exibir o resultado
                final_audio_fp = io.BytesIO()
                final_audio.export(final_audio_fp, format="mp3")
                final_audio_fp.seek(0)
                
                st.success("Seu jingle foi gerado com sucesso!")
                st.audio(final_audio_fp, format='audio/mp3')
                
                st.download_button(
                    label="📥 Baixar Jingle/Vinheta (MP3)",
                    data=final_audio_fp,
                    file_name="jingle_final.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )