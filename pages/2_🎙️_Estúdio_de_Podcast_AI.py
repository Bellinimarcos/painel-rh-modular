import streamlit as st
import requests
import base64
import io
import wave
import os
from pathlib import Path
import time
import sys
import subprocess

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Estúdio de Podcast AI",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Estúdio de Podcast AI - Alfa Bureau")
st.markdown("Produza um podcast com duas vozes, edite o roteiro e controle o tempo.")

# --- VERIFICAÇÃO FORÇADA DO PYDUB ---
def install_pydub():
    """Instala o PyDub e recarrega o módulo"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydub"])
        return True
    except Exception as e:
        st.error(f"Erro na instalação: {e}")
        return False

def check_pydub():
    """Verifica se o PyDub está disponível"""
    try:
        # Tenta importar o pydub
        from pydub import AudioSegment
        # Testa funcionalidades básicas
        test_audio = AudioSegment.empty()
        return True, AudioSegment
    except ImportError:
        # Tenta instalar automaticamente
        if install_pydub():
            try:
                from pydub import AudioSegment
                return True, AudioSegment
            except ImportError:
                return False, None
        return False, None
    except Exception:
        return False, None

# Verificação inicial
has_pydub, AudioSegment = check_pydub()

# Configuração do FFmpeg
project_root = Path(__file__).parent.parent
ffmpeg_exe = project_root / "ffmpeg.exe"
ffprobe_exe = project_root / "ffprobe.exe"
has_ffmpeg = os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe)

# Configurar PyDub se disponível
if has_ffmpeg and has_pydub:
    try:
        AudioSegment.converter = str(ffmpeg_exe)
        AudioSegment.ffprobe = str(ffprobe_exe)
    except Exception as e:
        st.error(f"Erro ao configurar FFmpeg: {e}")

mode = "complete" if (has_ffmpeg and has_pydub) else "basic"

# --- EXIBIÇÃO DO STATUS ---
if has_ffmpeg and has_pydub:
    st.success("🎧 **Modo Completo Ativado!**")
    st.info("FFmpeg e PyDub detectados! O podcast será gerado como um único arquivo combinado.")
    
elif has_ffmpeg and not has_pydub:
    st.warning("🔊 **Modo Básico Ativado**")
    
    st.markdown("---")
    st.subheader("🔧 Instalação do PyDub Necessária")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Para ativar o Modo Completo:**
        - ✅ Combine todos os áudios em um único arquivo
        - ✅ Download do podcast completo  
        - ✅ Melhor qualidade de produção
        
        **Solução rápida:**
        1. Clique no botão ao lado para instalar
        2. Recarregue a página (F5)
        3. O Modo Completo será ativado automaticamente
        """)
    
    with col2:
        if st.button("📦 Instalar PyDub Agora", type="primary", use_container_width=True):
            with st.spinner("Instalando PyDub... Por favor, aguarde."):
                if install_pydub():
                    st.success("✅ PyDub instalado com sucesso!")
                    st.info("**Recarregue a página** para ativar o Modo Completo.")
                    st.rerun()
                else:
                    st.error("❌ Falha na instalação do PyDub")
    
    st.markdown("---")
    st.subheader("📋 Solução Manual")
    st.code("pip install pydub")
    st.markdown("Execute o comando acima no terminal e recarregue a página.")
    
else:
    st.warning("🔊 **Modo Básico Ativado**")
    st.info("FFmpeg não encontrado. Gerando áudios individuais.")

# --- FUNÇÕES DE ÁUDIO ---
def create_wav_from_pcm(pcm_data, sample_rate=24000, channels=1, sample_width=2):
    """Converte dados PCM para WAV usando bibliotecas nativas"""
    try:
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        wav_buffer.seek(0)
        return wav_buffer.read()
    except Exception as e:
        st.error(f"Erro ao criar arquivo WAV: {e}")
        return None

def combine_audio_segments(segments):
    """Combina múltiplos segmentos de áudio em um único arquivo"""
    if not has_pydub:
        return None
        
    try:
        if not segments:
            return None
            
        final_audio = AudioSegment.empty()
        for segment_data in segments:
            if segment_data:
                segment = AudioSegment.from_wav(io.BytesIO(segment_data))
                final_audio += segment
        
        combined_buffer = io.BytesIO()
        final_audio.export(combined_buffer, format="wav")
        combined_buffer.seek(0)
        return combined_buffer.read()
    except Exception as e:
        st.error(f"Erro ao combinar áudio: {e}")
        return None

# --- FUNÇÃO DA API COM PROTEÇÃO CONTRA LIMITES ---
@st.cache_data(show_spinner=False)
def generate_audio_segment(text, style, voice_name, api_key):
    """Chama a API do Gemini para gerar um segmento de áudio"""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": f"{style}: {text}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}}
        },
        "model": "gemini-2.5-flash-preview-tts"
    }
    
    try:
        # Delay para evitar limites
        time.sleep(2)
        
        response = requests.post(api_url, json=payload, timeout=60)
        
        if response.status_code == 429:
            st.error("🚫 **Limite de API excedido.** Aguarde 1 hora ou use outra chave.")
            return None
        elif response.status_code == 403:
            st.error("🔐 **Erro de autorização.** Verifique sua chave API.")
            return None
            
        response.raise_for_status()
        
        result = response.json()
        audio_data_b64 = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("inlineData", {}).get("data")
        
        if audio_data_b64:
            return base64.b64decode(audio_data_b64)
        else:
            st.error(f"API não retornou áudio para: '{text[:30]}...'")
            return None
            
    except requests.exceptions.RequestException as e:
        if "429" in str(e):
            st.error("⏳ **Limite atingido.** Aguarde antes de tentar novamente.")
        else:
            st.error(f"Erro de conexão: {e}")
        return None

# --- VERIFICAÇÃO DA API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("Chave da API do Gemini não encontrada!")
    st.info("Adicione sua `GEMINI_API_KEY` ao arquivo `secrets.toml`")
    st.stop()

# --- INTERFACE DO USUÁRIO ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Vozes do Podcast")
    
    voices = {
        "Moderno": {"style": "Diga com uma voz jovem, conversada e energética", "voice": "Puck"},
        "Corporativo": {"style": "Diga com um tom de voz profissional, claro e executivo", "voice": "Kore"},
        "Jornalismo": {"style": "Diga com um tom formal, sério e jornalístico", "voice": "Orus"}
    }
    
    locutor1 = st.radio(
        "**Locutor 1 (Apresentador)**",
        options=list(voices.keys()),
        index=0,
        key="loc1"
    )
    
    locutor2 = st.radio(
        "**Locutor 2 (Especialista)**",
        options=list(voices.keys()),
        index=1,
        key="loc2"
    )

with col2:
    st.subheader("Produção")
    audio_placeholder = st.empty()
    download_placeholder = st.empty()

# --- EDITOR DE ROTEIRO ---
st.subheader("Roteiro do Podcast")

default_script = """[LOCUTOR 1]: Atenção, empresário! A Reforma Tributária de 2026 está chegando.
[LOCUTOR 2]: A mudança é grande. Cinco impostos viram apenas dois.
[LOCUTOR 1]: E qual o segredo para se preparar?
[LOCUTOR 2]: O planejamento. É preciso revisar contratos.
[LOCUTOR 1]: E a Alfa Bureau pode ajudar?
[LOCUTOR 2]: Com certeza. Oferecemos diagnóstico completo."""

script_text = st.text_area(
    "Edite o roteiro abaixo. Cada linha deve começar com `[LOCUTOR 1]:` ou `[LOCUTOR 2]:`",
    value=default_script,
    height=200,
    key="script_editor"
)

# --- ESTIMADOR DE DURAÇÃO ---
char_count = len(script_text)
estimated_seconds = round(char_count / 15)
st.info(f"**Duração estimada:** `{char_count}` caracteres ≈ `{estimated_seconds}` segundos")

# --- BOTÕES DE GERAÇÃO ---
st.markdown("---")

# Verificação de limites da API
if st.button("🔍 Verificar Status da API"):
    test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
    try:
        response = requests.post(test_url, json={"contents": [{"parts": [{"text": "Teste: Olá"}]}]}, timeout=10)
        if response.status_code == 200:
            st.success("✅ API está funcionando normalmente!")
        elif response.status_code == 429:
            st.error("❌ Limite de API excedido. Aguarde 1 hora.")
        else:
            st.error(f"❌ API retornou erro: {response.status_code}")
    except Exception as e:
        st.error(f"Erro ao verificar API: {e}")

col_test, col_full = st.columns(2)

with col_test:
    if st.button("🧪 Teste Rápido (2 linhas)", type="secondary", use_container_width=True):
        if not script_text.strip():
            st.warning("Por favor, insira um roteiro.")
        else:
            script_lines = [line.strip() for line in script_text.split('\n') if line.strip()]
            test_lines = script_lines[:2]  # Apenas 2 linhas para teste
            
            if test_lines:
                st.info(f"🧪 **Teste rápido:** Gerando {len(test_lines)} trechos...")
                
                all_segments = []
                success_count = 0
                
                for i, line in enumerate(test_lines):
                    clean_text = ""
                    preset = None

                    if line.startswith("[LOCUTOR 1]:"):
                        clean_text = line.replace("[LOCUTOR 1]:", "").strip()
                        preset = voices[locutor1]
                    elif line.startswith("[LOCUTOR 2]:"):
                        clean_text = line.replace("[LOCUTOR 2]:", "").strip()
                        preset = voices[locutor2]
                    else:
                        continue

                    if clean_text and preset:
                        with st.spinner(f"Testando {i+1}/{len(test_lines)}..."):
                            pcm_data = generate_audio_segment(clean_text, preset["style"], preset["voice"], api_key)
                            
                            if pcm_data:
                                wav_data = create_wav_from_pcm(pcm_data)
                                if wav_data:
                                    all_segments.append(wav_data)
                                    success_count += 1
                                    st.success(f"✅ {clean_text[:30]}...")
                
                if all_segments:
                    st.session_state.individual_segments = all_segments
                    st.session_state.test_mode = True
                    st.success(f"🎉 Teste concluído! {success_count}/{len(test_lines)} trechos gerados.")
                else:
                    st.error("❌ Teste falhou. Aguarde e tente novamente.")

with col_full:
    if st.button("🚀 Gerar Podcast Completo", type="primary", use_container_width=True):
        if not script_text.strip():
            st.warning("Por favor, insira um roteiro.")
        else:
            script_lines = [line.strip() for line in script_text.split('\n') if line.strip()]
            
            # Aviso para textos longos
            if len(script_lines) > 6:
                st.warning("⚠️ **Texto longo pode exceder limites.**")
                if not st.checkbox("Continuar mesmo assim"):
                    st.stop()
            
            all_segments = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            success_count = 0
            
            for i, line in enumerate(script_lines):
                clean_text = ""
                preset = None

                if line.startswith("[LOCUTOR 1]:"):
                    clean_text = line.replace("[LOCUTOR 1]:", "").strip()
                    preset = voices[locutor1]
                elif line.startswith("[LOCUTOR 2]:"):
                    clean_text = line.replace("[LOCUTOR 2]:", "").strip()
                    preset = voices[locutor2]
                else:
                    continue

                if clean_text and preset:
                    status_text.text(f"Gerando {i+1}/{len(script_lines)}...")
                    pcm_data = generate_audio_segment(clean_text, preset["style"], preset["voice"], api_key)
                    
                    if pcm_data:
                        wav_data = create_wav_from_pcm(pcm_data)
                        if wav_data:
                            all_segments.append(wav_data)
                            success_count += 1
                    
                    # Para se encontrar muitos erros
                    if i >= 2 and success_count == 0:
                        st.error("❌ Muitas falhas consecutivas. Parando...")
                        break
                
                progress_bar.progress((i + 1) / len(script_lines))
            
            progress_bar.empty()
            status_text.empty()
            
            # PROCESSAMENTO FINAL
            if all_segments:
                if mode == "complete" and has_pydub:
                    try:
                        combined_audio = combine_audio_segments(all_segments)
                        if combined_audio:
                            st.session_state.podcast_audio = combined_audio
                            st.session_state.individual_segments = all_segments
                            st.success(f"✅ Podcast completo gerado! {success_count} trechos combinados.")
                        else:
                            st.error("Erro ao combinar áudio. Exibindo trechos individuais.")
                            st.session_state.individual_segments = all_segments
                    except Exception as e:
                        st.error(f"Erro no modo completo: {e}")
                        st.session_state.individual_segments = all_segments
                else:
                    st.session_state.individual_segments = all_segments
                    st.success(f"✅ {success_count} trechos de áudio gerados com sucesso!")
            else:
                st.error("Não foi possível gerar áudio. Aguarde e tente novamente.")

# --- EXIBIÇÃO DOS RESULTADOS ---
if 'podcast_audio' in st.session_state and st.session_state.podcast_audio:
    st.markdown("---")
    st.subheader("🎧 Podcast Completo")
    audio_placeholder.audio(st.session_state.podcast_audio, format='audio/wav')
    download_placeholder.download_button(
        label="📥 Download do Podcast Completo (.wav)",
        data=st.session_state.podcast_audio,
        file_name="podcast_alfa_bureau.wav",
        mime="audio/wav",
        use_container_width=True
    )

if 'individual_segments' in st.session_state and st.session_state.individual_segments:
    st.markdown("---")
    
    if st.session_state.get('test_mode', False):
        st.subheader("🎧 Trechos de Teste Gerados")
    else:
        st.subheader("🎧 Trechos de Áudio")
    
    script_lines = [line.strip() for line in script_text.split('\n') if line.strip()]
    valid_lines = [line for line in script_lines if line.startswith(("[LOCUTOR 1]:", "[LOCUTOR 2]:"))]
    
    display_lines = valid_lines[:len(st.session_state.individual_segments)]
    
    for i, (line, audio_data) in enumerate(zip(display_lines, st.session_state.individual_segments)):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{line}**")
            st.audio(audio_data, format='audio/wav')
        with col2:
            st.download_button(
                label=f"📥 Trecho {i+1}",
                data=audio_data,
                file_name=f"trecho_{i+1}.wav",
                mime="audio/wav",
                key=f"download_{i}"
            )
        st.divider()

# --- SOLUÇÃO PARA LIMITES DA API ---
st.markdown("---")
st.subheader("🚨 Solução para Limites da API")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **⏳ Aguarde 1 hora:**
    - Limites resetam automaticamente
    - Use este tempo para ajustar o roteiro
    - Teste com textos mais curtos depois
    """)
    
with col2:
    st.markdown("""
    **🔑 Use outra chave API:**
    - Crie nova chave no Google AI Studio
    - Atualize o arquivo `secrets.toml`
    - Recarregue a aplicação
    """)

st.info("""
**💡 Dica:** Use o **botão de teste rápido** primeiro para verificar se a API já está respondendo,
antes de gerar o podcast completo.
""")

# --- REINICIALIZAÇÃO DO PYDUB ---
if not has_pydub and has_ffmpeg:
    st.markdown("---")
    st.subheader("🔧 Configuração do Modo Completo")
    
    if st.button("🔄 Tentar Detecção Novamente do PyDub", use_container_width=True):
        st.rerun()