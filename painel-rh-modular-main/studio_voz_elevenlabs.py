import streamlit as st
import io
import time
import subprocess
import tempfile
import os
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# Configuração da página
st.set_page_config(
    page_title="Estúdio de Voz Profissional - ElevenLabs",
    page_icon="️",
    layout="wide"
)

st.title("️ Estúdio de Voz Profissional - Alfa Bureau")
st.markdown("**Comercial Reforma Tributária 2026 - Powered by ElevenLabs PREMIUM**")

# Roteiro do comercial - VOZES PREMIUM: Daniel + Matilda
roteiro = [
    {"texto": "Atenção empreendedores! A Reforma Tributária de 2026 está chegando e vai revolucionar a rotina da sua empresa.", "voz": "onwK4e9ZLuTAKqWW03F9", "nome": "Daniel"},
    {"texto": "Os impostos atuais ISS, ICMS, PIS e Cofins serão substituídos por apenas dois novos tributos: o IBS e o CBS.", "voz": "XrExE9yKIg1WjnnlVkGX", "nome": "Matilda"},
    {"texto": "Isso significa mudanças profundas no cálculo de preços, no pagamento de impostos e no controle financeiro.", "voz": "onwK4e9ZLuTAKqWW03F9", "nome": "Daniel"},
    {"texto": "Será fundamental revisar contratos, atualizar sistemas e gerenciar créditos tributários com precisão.", "voz": "XrExE9yKIg1WjnnlVkGX", "nome": "Matilda"},
    {"texto": "Sua empresa está preparada para esta virada?", "voz": "onwK4e9ZLuTAKqWW03F9", "nome": "Daniel"},
    {"texto": "A Alfa Bureau está ao seu lado para decifrar mudanças, planejar estratégias e adaptar seu negócio.", "voz": "XrExE9yKIg1WjnnlVkGX", "nome": "Matilda"},
    {"texto": "Alfa Bureau: transformando complexidade em simplicidade, garantindo competitividade.", "voz": "onwK4e9ZLuTAKqWW03F9", "nome": "Daniel"}
]

# Verificar chave API
try:
    api_key = st.secrets["ELEVENLABS_API_KEY"]
    client = ElevenLabs(api_key=api_key)
    st.success(" ElevenLabs API PREMIUM carregada com sucesso!")
except Exception as e:
    st.error(" Erro ao carregar chave API do ElevenLabs")
    st.stop()

# Localizar FFmpeg
project_root = Path(__file__).parent
ffmpeg_path = project_root / "ffmpeg.exe"

if not ffmpeg_path.exists():
    st.warning(f"️ FFmpeg não encontrado em: {ffmpeg_path}")
    ffmpeg_path = "ffmpeg"

# Função para gerar áudio
def generate_audio_elevenlabs(texto, voice_id):
    try:
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=texto,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        )
        audio_bytes = b"".join(audio)
        return audio_bytes
    except Exception as e:
        st.error(f" Erro: {str(e)}")
        return None

# Função para combinar áudios usando FFmpeg
def combine_audios_ffmpeg(audio_segments):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Salvar todos os segmentos
            file_list = []
            for i, segment in enumerate(audio_segments):
                segment_path = temp_path / f"segment_{i}.mp3"
                with open(segment_path, 'wb') as f:
                    f.write(segment)
                file_list.append(segment_path)
            
            # Criar arquivo de lista para FFmpeg
            list_file = temp_path / "filelist.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for file_path in file_list:
                    f.write(f"file '{file_path.absolute()}'\n")
            
            # Arquivo de saída
            output_file = temp_path / "combined.wav"
            
            # Comando FFmpeg
            cmd = [
                str(ffmpeg_path),
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file),
                '-c:a', 'pcm_s16le',
                '-ar', '44100',
                str(output_file),
                '-y'
            ]
            
            # Executar FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            # Ler arquivo combinado
            with open(output_file, 'rb') as f:
                return f.read()
                
    except Exception as e:
        st.error(f" Erro ao combinar com FFmpeg: {str(e)}")
        return None

# Exibir roteiro
st.markdown("---")
st.subheader(" Roteiro do Comercial")
for i, item in enumerate(roteiro, 1):
    tipo_voz = "Masculina - Energética" if item['nome'] == "Daniel" else "Feminina - Profissional"
    with st.expander(f"**Trecho {i} - {item['nome']} ({tipo_voz})**"):
        st.write(item['texto'])

# Informações sobre as vozes
with st.expander(" Sobre as Vozes PREMIUM Selecionadas"):
    st.markdown("""
    ###  Daniel (Apresentador)
    -  Voz masculina jovem e energética
    -  Tom profissional e confiante
    -  Perfeito para chamar atenção e engajar
    -  Excelente dicção e naturalidade
    
    ###  Matilda (Especialista)
    -  Voz feminina multilíngue
    -  Tom profissional e técnico
    -  Perfeita para explicações complexas
    -  Clareza e credibilidade
    
    ** Combo ideal para comerciais corporativos!**
    """)

# Botão para ver vozes
if st.button(" Ver Todas as Vozes Disponíveis"):
    try:
        voices_response = client.voices.get_all()
        st.write("###  Vozes Disponíveis na sua Conta PAGA:")
        for voice in voices_response.voices:
            emoji = "" if voice.voice_id in ["onwK4e9ZLuTAKqWW03F9", "XrExE9yKIg1WjnnlVkGX"] else ""
            marca = " ⭐ **USANDO AGORA**" if voice.voice_id in ["onwK4e9ZLuTAKqWW03F9", "XrExE9yKIg1WjnnlVkGX"] else ""
            st.write(f"{emoji} **{voice.name}** (ID: `{voice.voice_id}`){marca}")
    except Exception as e:
        st.error(f"Erro: {e}")

# Botão de geração
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("️ **GERAR COMERCIAL COM VOZES PREMIUM**", type="primary", width='stretch'):
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        audio_segments = []
        
        for i, item in enumerate(roteiro):
            status_text.text(f" Gerando trecho {i+1}/{len(roteiro)} com {item['nome']} (PREMIUM)...")
            progress_bar.progress((i / len(roteiro)) * 0.7)
            
            audio = generate_audio_elevenlabs(item['texto'], item['voz'])
            
            if audio:
                audio_segments.append(audio)
                st.success(f" Trecho {i+1} gerado com voz premium {item['nome']}!")
            else:
                st.error(f" Falha no trecho {i+1}")
                break
            
            if i < len(roteiro) - 1:
                time.sleep(0.5)
        
        if len(audio_segments) == len(roteiro):
            status_text.text(" Combinando com FFmpeg em qualidade máxima...")
            progress_bar.progress(0.85)
            
            combined_audio = combine_audios_ffmpeg(audio_segments)
            
            if combined_audio:
                progress_bar.progress(1.0)
                status_text.text(" Comercial PREMIUM pronto!")
                
                st.markdown("---")
                st.subheader(" Comercial Completo - Qualidade PREMIUM")
                st.info(" Gerado com vozes **Daniel** (apresentador) e **Matilda** (especialista)")
                st.audio(combined_audio, format="audio/wav")
                
                st.download_button(
                    label=" Download do Comercial PREMIUM (.wav)",
                    data=combined_audio,
                    file_name="comercial_alfa_bureau_PREMIUM.wav",
                    mime="audio/wav",
                    width='stretch'
                )
                
                st.success(" Comercial PREMIUM gerado com sucesso!")
                st.balloons()
            else:
                st.error(" Erro ao combinar. Baixe os trechos individuais:")
                for i, audio in enumerate(audio_segments):
                    st.audio(audio, format="audio/mp3")
                    st.download_button(
                        label=f" Trecho {i+1} - {roteiro[i]['nome']}",
                        data=audio,
                        file_name=f"trecho_{i+1}_{roteiro[i]['nome']}.mp3",
                        mime="audio/mp3",
                        key=f"dl_{i}"
                    )
        else:
            st.error(" Não foi possível gerar todos os trechos")

st.markdown("---")
st.info(" **Versão PREMIUM com vozes Daniel + Matilda** | Usando FFmpeg para combinação perfeita")
total_chars = sum(len(item['texto']) for item in roteiro)
st.caption(f" Total: {total_chars} caracteres | Vozes: Daniel (masculina) + Matilda (feminina)")


