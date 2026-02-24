"""
SPOT DE RÁDIO COMERCIAL - ALFA BUREAU
Reforma Tributária 2026
Duração: 55-60 segundos (EXATO)
APROVADO PARA VEICULAO
"""

import streamlit as st
import time
import subprocess
import tempfile
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

st.set_page_config(
    page_title="Spot Rádio 60s - Alfa Bureau",
    page_icon="",
    layout="wide"
)

st.title(" Spot Comercial para Rádio - Alfa Bureau")
st.markdown("**Reforma Tributária 2026 - 55-60 segundos**")

# ==================== UPLOAD DE JINGLES ====================
st.markdown("---")
st.subheader(" Upload de Jingles (3-5 segundos cada)")

st.warning("️ **IMPORTANTE:** Use jingles curtos (3-5s) para não ultrapassar 60 segundos totais!")

col1, col2 = st.columns(2)

with col1:
    st.info("** Jingle Abertura (3-5s)**")
    jingle_abertura = st.file_uploader(
        "Vinheta de abertura",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
        key="abertura"
    )
    if jingle_abertura:
        st.success(f" {jingle_abertura.name}")
        st.audio(jingle_abertura)

with col2:
    st.warning("** Assinatura Final (3-5s)**")
    jingle_encerramento = st.file_uploader(
        "Assinatura da marca",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
        key="encerramento"
    )
    if jingle_encerramento:
        st.success(f" {jingle_encerramento.name}")
        st.audio(jingle_encerramento)

# ==================== ROTEIRO RÁDIO (55-60s) ====================

# OPO 1: Spot Informativo
roteiro_opcao1 = [
    {
        "texto": "Atenção empresário! A Reforma Tributária de 2026 está chegando e vai mudar completamente a forma como sua empresa paga impostos.",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "tempo_estimado": "8s",
        "descricao": " Gancho - Atenção"
    },
    {
        "texto": "Cinco impostos atuais serão substituídos por apenas dois. O sistema de créditos tributários muda totalmente. E quem não se preparar agora pode ter sérios problemas em 2026.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "tempo_estimado": "14s",
        "descricao": " Problema/Urgência"
    },
    {
        "texto": "A Alfa Bureau está ajudando empresas a se prepararem com diagnóstico completo, análise de impactos e plano de ação personalizado. Não deixe para a última hora!",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "tempo_estimado": "13s",
        "descricao": " Solução Alfa Bureau"
    },
    {
        "texto": "Entre em contato com a Alfa Bureau e garanta que sua empresa esteja pronta para essa transformação. Alfa Bureau: transformando complexidade em simplicidade.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "tempo_estimado": "12s",
        "descricao": " CTA + Assinatura"
    }
]

# OPO 2: Spot Mais Direto
roteiro_opcao2 = [
    {
        "texto": "2026 está logo ali! A Reforma Tributária vai revolucionar os impostos da sua empresa. Você está preparado?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "tempo_estimado": "7s",
        "descricao": " Gancho Direto"
    },
    {
        "texto": "CBS e IBS substituem cinco impostos atuais. Sistema de créditos totalmente novo. Notas fiscais eletrônicas diferentes. Sua empresa precisa se adaptar já!",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "tempo_estimado": "13s",
        "descricao": " Mudanças Principais"
    },
    {
        "texto": "A Alfa Bureau oferece diagnóstico completo da sua situação tributária e cria um plano de ação sob medida. Não arrisque a saúde financeira do seu negócio!",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "tempo_estimado": "14s",
        "descricao": " Oferta"
    },
    {
        "texto": "Alfa Bureau: especialistas em gestão tributária. Fale conosco e prepare sua empresa para 2026. Alfa Bureau, simplificando sua gestão.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "tempo_estimado": "11s",
        "descricao": " CTA Final"
    }
]

# OPO 3: Spot Consultor
roteiro_opcao3 = [
    {
        "texto": "Empresário, sua empresa está pronta para a Reforma Tributária de 2026?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "tempo_estimado": "5s",
        "descricao": " Pergunta Direta"
    },
    {
        "texto": "A maior mudança tributária em décadas está chegando. Novos impostos, novas regras, novo sistema de créditos. Quem não se preparar pode enfrentar multas, perder dinheiro e ter problemas com a fiscalização.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "tempo_estimado": "16s",
        "descricao": "️ Riscos"
    },
    {
        "texto": "A Alfa Bureau tem a solução! Fazemos análise completa dos impactos na sua empresa, mapeamos oportunidades e criamos estratégia personalizada para 2026.",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "tempo_estimado": "13s",
        "descricao": " Solução Completa"
    },
    {
        "texto": "Entre em contato agora com a Alfa Bureau. Sua tranquilidade tributária começa aqui!",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "tempo_estimado": "7s",
        "descricao": " CTA Urgente"
    }
]

# ==================== SELEO DE ROTEIRO ====================
st.markdown("---")
st.subheader(" Escolha o Roteiro")

opcao_roteiro = st.radio(
    "Selecione a versão do spot:",
    options=[
        ("Opção 1: Informativo (Problema  Solução)", roteiro_opcao1),
        ("Opção 2: Direto (Mudanças  Ação)", roteiro_opcao2),
        ("Opção 3: Consultivo (Pergunta  Solução)", roteiro_opcao3)
    ],
    format_func=lambda x: x[0]
)

roteiro = opcao_roteiro[1]

# Mostrar roteiro selecionado
with st.expander(" Ver Roteiro Completo Selecionado"):
    tempo_total_fala = 0
    for i, item in enumerate(roteiro, 1):
        tempo = int(item['tempo_estimado'].replace('s', ''))
        tempo_total_fala += tempo
        st.write(f"**{i}. {item['descricao']}** ({item['tempo_estimado']})")
        st.write(f"_{item['nome']}: {item['texto']}_")
        st.divider()
    
    st.info(f"⏱️ **Tempo total das falas:** ~{tempo_total_fala} segundos")
    st.warning(f" **+ Jingles:** 6-10s (abertura + encerramento)")
    st.success(f" **TOTAL ESTIMADO:** {tempo_total_fala + 8} segundos (objetivo: 55-60s)")

# ==================== API ====================
try:
    api_key = st.secrets["ELEVENLABS_API_KEY"]
    client = ElevenLabs(api_key=api_key)
    st.success(" API conectada")
except Exception as e:
    st.error(f" {str(e)}")
    st.stop()

project_root = Path(__file__).parent
ffmpeg_path = project_root / "ffmpeg.exe"
if not ffmpeg_path.exists():
    ffmpeg_path = "ffmpeg"

# ==================== FUNES ====================

def generate_audio_stable(texto, voice_id, nome_voz):
    """Gera áudio otimizado para rádio"""
    try:
        # Configurações para RÁDIO (mais estáveis)
        if voice_id == "nPczCjzI2devNBz1zQrb":
            settings = VoiceSettings(
                stability=0.90,  # Máxima estabilidade para rádio
                similarity_boost=0.85,
                style=0.15,
                use_speaker_boost=True
            )
        else:
            settings = VoiceSettings(
                stability=0.90,
                similarity_boost=0.85,
                style=0.15,
                use_speaker_boost=True
            )
        
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_turbo_v2_5",
            text=texto,
            voice_settings=settings,
            output_format="mp3_44100_192"
        )
        
        audio_bytes = b"".join(audio_generator)
        
        if len(audio_bytes) < 1000:
            raise Exception(f"Áudio de {nome_voz} muito pequeno")
            
        return audio_bytes
        
    except Exception as e:
        st.error(f" {str(e)}")
        return None


def combine_audios_with_jingles(audio_segments, jingle_start=None, jingle_end=None):
    """Combina áudios com jingles"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_list = []
            
            if jingle_start:
                jingle_start_path = temp_path / "jingle_start.mp3"
                jingle_temp = temp_path / f"jingle_orig.{jingle_start.name.split('.')[-1]}"
                with open(jingle_temp, 'wb') as ft:
                    ft.write(jingle_start.read())
                
                subprocess.run([
                    str(ffmpeg_path), '-i', str(jingle_temp),
                    '-acodec', 'libmp3lame', '-ar', '44100',
                    '-b:a', '192k', str(jingle_start_path), '-y'
                ], capture_output=True)
                
                if jingle_start_path.exists():
                    file_list.append(jingle_start_path)
            
            for i, segment in enumerate(audio_segments):
                segment_path = temp_path / f"segment_{i:02d}.mp3"
                with open(segment_path, 'wb') as f:
                    f.write(segment)
                file_list.append(segment_path)
            
            if jingle_end:
                jingle_end_path = temp_path / "jingle_end.mp3"
                jingle_temp = temp_path / f"jingle_end_orig.{jingle_end.name.split('.')[-1]}"
                with open(jingle_temp, 'wb') as ft:
                    ft.write(jingle_end.read())
                
                subprocess.run([
                    str(ffmpeg_path), '-i', str(jingle_temp),
                    '-acodec', 'libmp3lame', '-ar', '44100',
                    '-b:a', '192k', str(jingle_end_path), '-y'
                ], capture_output=True)
                
                if jingle_end_path.exists():
                    file_list.append(jingle_end_path)
            
            list_file = temp_path / "filelist.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for file_path in file_list:
                    f.write(f"file '{str(file_path).replace(chr(92), '/')}'\n")
            
            output_file = temp_path / "spot_final.mp3"
            
            subprocess.run([
                str(ffmpeg_path), '-f', 'concat', '-safe', '0',
                '-i', str(list_file), '-c', 'copy',
                str(output_file), '-y'
            ], capture_output=True)
            
            with open(output_file, 'rb') as f:
                return f.read()
                
    except Exception as e:
        st.error(f" {str(e)}")
        return None

# ==================== GERAO ====================

st.markdown("---")
st.markdown("### ️ Gerar Spot para Rádio")

if st.button(" **GERAR SPOT DE 60 SEGUNDOS**", type="primary", width='stretch'):
    
    if not jingle_abertura or not jingle_encerramento:
        st.error("️  obrigatório incluir jingles de abertura E encerramento!")
        st.stop()
    
    progress_bar = st.progress(0.0)
    status_text = st.empty()
    
    audio_segments = []
    failed = False
    
    for i, item in enumerate(roteiro):
        if failed:
            break
            
        status_text.text(f" Gerando: {item['descricao']}...")
        progress_bar.progress((i / len(roteiro)) * 0.85)
        
        audio = generate_audio_stable(item['texto'], item['voz'], item['nome'])
        
        if audio and len(audio) > 1000:
            audio_segments.append(audio)
            st.success(f" {item['descricao']}")
        else:
            st.error(f" Falha: {item['descricao']}")
            failed = True
            break
        
        time.sleep(0.5)
    
    if not failed and len(audio_segments) == len(roteiro):
        status_text.text(" Finalizando spot...")
        progress_bar.progress(0.95)
        
        jingle_abertura.seek(0)
        jingle_encerramento.seek(0)
        
        final_spot = combine_audios_with_jingles(
            audio_segments,
            jingle_start=jingle_abertura,
            jingle_end=jingle_encerramento
        )
        
        if final_spot:
            progress_bar.progress(1.0)
            status_text.text(" Spot pronto!")
            
            st.markdown("---")
            st.markdown("##  SPOT COMERCIAL PRONTO")
            
            st.warning("️ **OUA O SPOT COMPLETO BAIXANDO O ARQUIVO!**")
            
            # Download destacado
            st.download_button(
                label=" BAIXAR SPOT PARA RÁDIO (.mp3)",
                data=final_spot,
                file_name="SPOT_ALFA_BUREAU_REFORMA_2026_60s.mp3",
                mime="audio/mp3",
                width='stretch',
                type="primary"
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Formato", "MP3 192kbps")
            with col2:
                st.metric("Tamanho", f"{len(final_spot) / 1024:.0f} KB")
            with col3:
                st.metric("Duração", "~60s")
            
            # Player para conferência
            with st.expander(" Preview (confira antes de veicular)"):
                st.audio(final_spot, format="audio/mp3")
            
            st.success(" SPOT COMERCIAL PRONTO PARA VEICULAO!")
            
            st.info("""
            ** CHECKLIST ANTES DE VEICULAR:**
            - [ ] Ouça o spot completo
            - [ ] Verifique se está entre 55-60 segundos
            - [ ] Confirme que o áudio está claro
            - [ ] Valide se a mensagem está correta
            - [ ] Envie para a rádio no formato correto
            """)
            
            st.balloons()

st.markdown("---")
st.info(" **Spot Comercial Profissional** | 55-60s | Pronto para rádio | Alta qualidade")


