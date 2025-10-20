import streamlit as st
import io
import time
import subprocess
import tempfile
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# Configuração da página
st.set_page_config(
    page_title="Podcast 60s - Alfa Bureau",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Podcast Profissional 60s - Alfa Bureau")
st.markdown("**Reforma Tributária 2026 - Formato Podcast com Vinhetas**")

# ========== ROTEIRO COMPLETO ==========
roteiro = [
    # VINHETA ABERTURA (3s)
    {
        "tipo": "vinheta_abertura",
        "texto": "Alfa Bureau Cast. Seu negócio preparado para o futuro.",
        "voz": "onwK4e9ZLuTAKqWW03F9",
        "nome": "Daniel",
        "descricao": "Vinheta de Abertura"
    },
    
    # DIÁLOGO PRINCIPAL (~50s)
    {
        "tipo": "dialogo",
        "texto": "Olá! Bem-vindos ao Alfa Bureau Cast! Hoje vamos falar sobre a Reforma Tributária de 2026. E para nos ajudar, temos nossa especialista em tributação. Como você está?",
        "voz": "onwK4e9ZLuTAKqWW03F9",
        "nome": "Daniel",
        "descricao": "Apresentador - Abertura"
    },
    {
        "tipo": "dialogo",
        "texto": "Ótima! Obrigada por me receber. A Reforma Tributária é um dos maiores desafios que as empresas vão enfrentar nos próximos anos.",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "Especialista - Introdução"
    },
    {
        "tipo": "dialogo",
        "texto": "E o que muda exatamente? Muitos empresários ainda estão confusos.",
        "voz": "onwK4e9ZLuTAKqWW03F9",
        "nome": "Daniel",
        "descricao": "Apresentador - Pergunta"
    },
    {
        "tipo": "dialogo",
        "texto": "Simplificando: cinco impostos viram dois. O ICMS, ISS, PIS e Cofins serão substituídos pelo IBS e CBS. Parece simples, mas o impacto é enorme!",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "Especialista - Explicação"
    },
    {
        "tipo": "dialogo",
        "texto": "E como as empresas devem se preparar?",
        "voz": "onwK4e9ZLuTAKqWW03F9",
        "nome": "Daniel",
        "descricao": "Apresentador - Pergunta"
    },
    {
        "tipo": "dialogo",
        "texto": "Três passos fundamentais: revisar todos os contratos, atualizar os sistemas de gestão, e fazer um planejamento tributário detalhado. A Alfa Bureau está ajudando centenas de empresas nesse processo.",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "Especialista - Solução"
    },
    {
        "tipo": "dialogo",
        "texto": "Perfeito! E para quem quer saber mais, basta entrar em contato com a Alfa Bureau.",
        "voz": "onwK4e9ZLuTAKqWW03F9",
        "nome": "Daniel",
        "descricao": "Apresentador - CTA"
    },
    
    # JINGLE (4s)
    {
        "tipo": "jingle",
        "texto": "Alfa Bureau. Transformando complexidade em simplicidade. Garantindo sua competitividade!",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "Jingle Marca"
    },
    
    # VINHETA ENCERRAMENTO (3s)
    {
        "tipo": "vinheta_encerramento",
        "texto": "Alfa Bureau Cast. Até o próximo episódio!",
        "voz": "onwK4e9ZLuTAKqWW03F9",
        "nome": "Daniel",
        "descricao": "Vinheta de Encerramento"
    }
]

# Verificar chave API
try:
    api_key = st.secrets["ELEVENLABS_API_KEY"]
    client = ElevenLabs(api_key=api_key)
    st.success("✅ ElevenLabs API PREMIUM carregada!")
except Exception as e:
    st.error("❌ Erro ao carregar chave API")
    st.stop()

# Localizar FFmpeg
project_root = Path(__file__).parent
ffmpeg_path = project_root / "ffmpeg.exe"
if not ffmpeg_path.exists():
    ffmpeg_path = "ffmpeg"

# Função para gerar áudio
def generate_audio(texto, voice_id, tipo_conteudo):
    try:
        # Ajustar configurações por tipo
        if tipo_conteudo in ["vinheta_abertura", "vinheta_encerramento"]:
            # Vinhetas: mais dramáticas
            settings = VoiceSettings(
                stability=0.7,
                similarity_boost=0.8,
                style=0.3,
                use_speaker_boost=True
            )
        elif tipo_conteudo == "jingle":
            # Jingle: mais animado
            settings = VoiceSettings(
                stability=0.6,
                similarity_boost=0.9,
                style=0.5,
                use_speaker_boost=True
            )
        else:
            # Diálogo: natural
            settings = VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=texto,
            voice_settings=settings
        )
        return b"".join(audio)
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        return None

# Função para combinar áudios
def combine_audios_ffmpeg(audio_segments):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_list = []
            
            for i, segment in enumerate(audio_segments):
                segment_path = temp_path / f"segment_{i}.mp3"
                with open(segment_path, 'wb') as f:
                    f.write(segment)
                file_list.append(segment_path)
            
            list_file = temp_path / "filelist.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for file_path in file_list:
                    f.write(f"file '{file_path.absolute()}'\n")
            
            output_file = temp_path / "podcast_60s.wav"
            
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
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            with open(output_file, 'rb') as f:
                return f.read()
    except Exception as e:
        st.error(f"❌ Erro ao combinar: {str(e)}")
        return None

# ========== INTERFACE ==========

st.markdown("---")
st.subheader("📻 Estrutura do Podcast")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**🎵 Vinheta Abertura**\n\n~3 segundos\n\nDaniel")
with col2:
    st.success("**🎙️ Diálogo Principal**\n\n~50 segundos\n\nDaniel + Matilda")
with col3:
    st.warning("**🎶 Jingle + Encerramento**\n\n~7 segundos\n\nMatilda + Daniel")

# Mostrar roteiro
st.markdown("---")
st.subheader("📝 Roteiro Completo do Podcast")

for i, item in enumerate(roteiro, 1):
    icone = "🎵" if "vinheta" in item["tipo"] else "🎶" if item["tipo"] == "jingle" else "🎙️"
    with st.expander(f"{icone} **{item['descricao']}** - {item['nome']}"):
        st.write(f"**Tipo:** {item['tipo']}")
        st.write(f"**Texto:** {item['texto']}")

# Info sobre vozes
with st.expander("🎤 Configurações de Voz por Tipo"):
    st.markdown("""
    - **Vinhetas:** Voz mais dramática e enfática
    - **Diálogo:** Voz natural e conversacional
    - **Jingle:** Voz animada e memorável
    
    **Vozes:**
    - 👨 **Daniel** (apresentador) - Tom energético e profissional
    - 👩 **Matilda** (especialista) - Tom técnico e confiável
    """)

# Botão de geração
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎙️ **GERAR PODCAST 60s COMPLETO**", type="primary", use_container_width=True):
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        audio_segments = []
        
        for i, item in enumerate(roteiro):
            status_text.text(f"🎤 Gerando: {item['descricao']}...")
            progress_bar.progress((i / len(roteiro)) * 0.8)
            
            audio = generate_audio(item['texto'], item['voz'], item['tipo'])
            
            if audio:
                audio_segments.append(audio)
                st.success(f"✅ {item['descricao']} - {item['nome']}")
            else:
                st.error(f"❌ Falha: {item['descricao']}")
                break
            
            time.sleep(0.5)
        
        if len(audio_segments) == len(roteiro):
            status_text.text("🔗 Montando podcast completo...")
            progress_bar.progress(0.9)
            
            final_podcast = combine_audios_ffmpeg(audio_segments)
            
            if final_podcast:
                progress_bar.progress(1.0)
                status_text.text("✅ Podcast pronto!")
                
                st.markdown("---")
                st.subheader("🎧 Podcast 60s - Alfa Bureau Cast")
                st.audio(final_podcast, format="audio/wav")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        label="📥 Download Podcast (.wav)",
                        data=final_podcast,
                        file_name="alfa_bureau_podcast_60s.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
                with col_b:
                    st.metric("Duração Estimada", "~60 segundos")
                
                st.success("🎉 Podcast gerado com sucesso!")
                st.balloons()
            else:
                st.error("❌ Erro ao combinar")
        else:
            st.error("❌ Não foi possível gerar todos os trechos")

st.markdown("---")
st.info("💎 **Podcast Premium** com vozes Daniel + Matilda | Estrutura: Vinheta → Diálogo → Jingle → Encerramento")

total_chars = sum(len(item['texto']) for item in roteiro)
st.caption(f"📊 {len(roteiro)} segmentos | {total_chars} caracteres | Duração: ~60 segundos")