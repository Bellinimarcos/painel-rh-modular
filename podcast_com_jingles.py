"""
Podcast Profissional - Alfa Bureau Cast
Gerador de podcast com upload de jingles personalizados
Versão 2.0 - Corrigida e Expandida
"""

import streamlit as st
import time
import subprocess
import tempfile
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(
    page_title="Podcast Profissional - Alfa Bureau",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Podcast Profissional - Alfa Bureau Cast")
st.markdown("**Reforma Tributária 2026 - Versão Expandida (3-4 minutos)**")

# ==================== UPLOAD DE JINGLES ====================
st.markdown("---")
st.subheader("🎵 Faça Upload dos seus Jingles")

col1, col2 = st.columns(2)

with col1:
    st.info("**🎵 Jingle de Abertura**")
    jingle_abertura = st.file_uploader(
        "Escolha o arquivo de áudio",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'mp2', 'wma'],
        key="abertura",
        help="Formatos aceitos: MP3, WAV, M4A, OGG, FLAC, AAC, MP2, WMA"
    )
    if jingle_abertura:
        st.success(f"✅ {jingle_abertura.name}")
        st.audio(jingle_abertura, format=f"audio/{jingle_abertura.name.split('.')[-1]}")

with col2:
    st.warning("**🎵 Jingle de Encerramento**")
    jingle_encerramento = st.file_uploader(
        "Escolha o arquivo de áudio",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'mp2', 'wma'],
        key="encerramento",
        help="Formatos aceitos: MP3, WAV, M4A, OGG, FLAC, AAC, MP2, WMA"
    )
    if jingle_encerramento:
        st.success(f"✅ {jingle_encerramento.name}")
        st.audio(jingle_encerramento, format=f"audio/{jingle_encerramento.name.split('.')[-1]}")

# ==================== ROTEIRO EXPANDIDO ====================
roteiro = [
    # ABERTURA
    {
        "texto": "E aí, tudo bem com vocês? Sejam muito bem-vindos a mais um episódio do Alfa Bureau Cast, o podcast que simplifica a gestão empresarial para você! Eu sou o Brian, e hoje vamos falar sobre um tema que tá tirando o sono de muitos empresários: a Reforma Tributária de 2026. E pra nos ajudar a entender tudo isso, trouxe aqui a nossa especialista em tributos. E aí, como você está?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": "👨 Brian - Abertura Completa"
    },
    {
        "texto": "Oi Brian! Tudo ótimo, obrigada! Olha, esse assunto é realmente sério, viu? A Reforma Tributária vai mexer profundamente com todas as empresas brasileiras. Não é exagero dizer que será uma das maiores mudanças das últimas décadas no nosso sistema tributário.",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "👩 Matilda - Resposta Inicial"
    },
    
    # DESENVOLVIMENTO
    {
        "texto": "Nossa, pesado isso! Mas vamos lá, explica pra gente: o que exatamente vai mudar? Porque eu sei que tem muita gente ainda meio perdida nesse assunto, sem entender direito o que vem pela frente.",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": "👨 Brian - Pergunta 1"
    },
    {
        "texto": "Ótima pergunta! Então, vamos simplificar: hoje, a gente tem um sistema super complexo, com cinco impostos diferentes sobre consumo. Tem o ICMS estadual, o ISS municipal, o PIS, a Cofins e o IPI federal. É uma bagunça, né? Com a reforma, tudo isso vai virar apenas dois impostos: o IBS, que é o Imposto sobre Bens e Serviços, e o CBS, a Contribuição sobre Bens e Serviços. Parece simples, mas o impacto dessa mudança vai ser gigante!",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "👩 Matilda - Explicação Detalhada"
    },
    {
        "texto": "Entendi. E quando isso vai acontecer de fato? Tem algum cronograma?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": "👨 Brian - Pergunta 2"
    },
    {
        "texto": "Sim! A transição vai ser gradual. Começa em 2026 com uma fase de testes, e a implementação completa está prevista para acontecer até 2033. Então são sete anos de transição. Mas atenção: as empresas precisam começar a se preparar agora, em 2025, porque as mudanças nos sistemas e processos levam tempo!",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "👩 Matilda - Cronograma"
    },
    {
        "texto": "Puts, então não dá pra deixar pra última hora mesmo! E as empresas, o que elas precisam fazer pra se preparar? Quais são os principais pontos de atenção?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": "👨 Brian - Pergunta 3"
    },
    {
        "texto": "Olha, existem três pilares fundamentais de preparação. Primeiro: revisar todos os contratos comerciais, porque as alíquotas vão mudar e isso impacta preços e margens. Segundo: atualizar os sistemas de gestão, ERP, faturamento, tudo! Os sistemas atuais não estão preparados pra esse novo modelo. E terceiro, o mais crítico: fazer um planejamento tributário bem estruturado. A Alfa Bureau tem ajudado dezenas de empresas exatamente nisso, fazendo diagnósticos completos e planos de ação personalizados.",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "👩 Matilda - Solução Completa"
    },
    {
        "texto": "Excelente! E me diz uma coisa: tem setores que vão ser mais impactados que outros?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": "👨 Brian - Pergunta 4"
    },
    {
        "texto": "Com certeza! O varejo, serviços, construção civil e indústria vão sentir mudanças significativas. Cada setor tem suas particularidades. Por exemplo, alguns terão benefícios fiscais, outros vão enfrentar aumento de carga tributária. Por isso é tão importante ter um diagnóstico específico do seu negócio.",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "👩 Matilda - Setores Impactados"
    },
    
    # ENCERRAMENTO
    {
        "texto": "Perfeito! Acho que conseguimos esclarecer bastante coisa aqui, né? Muito obrigado pela participação, foi esclarecedor demais!",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": "👨 Brian - Agradecimento"
    },
    {
        "texto": "Imagina, Brian! Foi um prazer enorme estar aqui. E galera, só um recado importante: não deixem pra última hora, tá? A Reforma Tributária tá chegando e quem se preparar antes vai ter uma vantagem competitiva gigante!",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "👩 Matilda - Alerta Final"
    },
    {
        "texto": "Exatamente! E pra quem quer um diagnóstico completo e personalizado da situação da sua empresa, a Alfa Bureau está de portas abertas. Nossa equipe de especialistas pode fazer uma análise detalhada e criar um plano de ação sob medida pro seu negócio. É só entrar em contato!",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": "👨 Brian - CTA"
    },
    {
        "texto": "Isso mesmo! E não percam o próximo episódio do Alfa Bureau Cast, onde vamos falar sobre estratégias práticas de implementação. Vai ser imperdível!",
        "voz": "XrExE9yKIg1WjnnlVkGX",
        "nome": "Matilda",
        "descricao": "👩 Matilda - Convite"
    },
    {
        "texto": "Fiquem ligados! Um super abraço a todos e até o próximo episódio!",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": "👨 Brian - Despedida"
    }
]

# ==================== VERIFICAR API ====================
try:
    api_key = st.secrets["ELEVENLABS_API_KEY"]
    client = ElevenLabs(api_key=api_key)
    st.success("✅ ElevenLabs API carregada com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar API: {str(e)}")
    st.info("💡 Configure sua API Key em `.streamlit/secrets.toml`")
    st.stop()

# ==================== CONFIGURAR FFMPEG ====================
project_root = Path(__file__).parent
ffmpeg_path = project_root / "ffmpeg.exe"
if not ffmpeg_path.exists():
    ffmpeg_path = "ffmpeg"

# ==================== FUNÇÕES ====================

def generate_audio_stable(texto, voice_id):
    """Gera áudio usando ElevenLabs com configurações otimizadas - CORRIGIDO"""
    try:
        # Configurações mais estáveis para evitar chiados
        if voice_id == "nPczCjzI2devNBz1zQrb":  # Brian
            settings = VoiceSettings(
                stability=0.75,  # AUMENTADO para mais estabilidade
                similarity_boost=0.80,  # AUMENTADO para melhor qualidade
                style=0.30,  # REDUZIDO para evitar distorções
                use_speaker_boost=True
            )
        else:  # Matilda
            settings = VoiceSettings(
                stability=0.65,  # AUMENTADO
                similarity_boost=0.75,  # AUMENTADO
                style=0.35,  # REDUZIDO
                use_speaker_boost=True
            )
        
        # Gerar áudio
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=texto,
            voice_settings=settings,
            output_format="mp3_44100_128"  # FORMATO ESPECÍFICO para melhor qualidade
        )
        
        # Coletar bytes
        audio_bytes = b"".join(audio_generator)
        
        # Verificar se o áudio foi gerado corretamente
        if len(audio_bytes) < 1000:  # Áudio muito pequeno = problema
            raise Exception("Áudio gerado é muito pequeno")
            
        return audio_bytes
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar áudio: {str(e)}")
        return None


def combine_audios_with_jingles(audio_segments, jingle_start=None, jingle_end=None):
    """Combina áudios do podcast com jingles usando FFmpeg - MELHORADO"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_list = []
            
            # Adicionar jingle de abertura
            if jingle_start:
                jingle_start_path = temp_path / f"jingle_start.{jingle_start.name.split('.')[-1]}"
                with open(jingle_start_path, 'wb') as f:
                    f.write(jingle_start.read())
                
                # Converter para formato padrão com melhor qualidade
                converted_start = temp_path / "jingle_start_converted.wav"
                result = subprocess.run([
                    str(ffmpeg_path),
                    '-i', str(jingle_start_path),
                    '-ar', '44100',  # Sample rate
                    '-ac', '2',  # Stereo
                    '-b:a', '192k',  # Bitrate
                    str(converted_start),
                    '-y'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    file_list.append(converted_start)
                else:
                    st.warning(f"⚠️ Aviso ao converter jingle de abertura: {result.stderr}")
            
            # Adicionar segmentos do podcast (já em MP3)
            for i, segment in enumerate(audio_segments):
                segment_path = temp_path / f"segment_{i}.mp3"
                with open(segment_path, 'wb') as f:
                    f.write(segment)
                file_list.append(segment_path)
            
            # Adicionar jingle de encerramento
            if jingle_end:
                jingle_end_path = temp_path / f"jingle_end.{jingle_end.name.split('.')[-1]}"
                with open(jingle_end_path, 'wb') as f:
                    f.write(jingle_end.read())
                
                # Converter para formato padrão com melhor qualidade
                converted_end = temp_path / "jingle_end_converted.wav"
                result = subprocess.run([
                    str(ffmpeg_path),
                    '-i', str(jingle_end_path),
                    '-ar', '44100',
                    '-ac', '2',
                    '-b:a', '192k',
                    str(converted_end),
                    '-y'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    file_list.append(converted_end)
                else:
                    st.warning(f"⚠️ Aviso ao converter jingle de encerramento: {result.stderr}")
            
            # Criar arquivo de lista
            list_file = temp_path / "filelist.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for file_path in file_list:
                    f.write(f"file '{file_path.absolute()}'\n")
            
            # Arquivo de saída
            output_file = temp_path / "podcast_final.wav"
            
            # Combinar tudo com melhor qualidade
            cmd = [
                str(ffmpeg_path),
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file),
                '-c:a', 'pcm_s16le',
                '-ar', '44100',
                '-ac', '2',
                str(output_file),
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            # Ler arquivo final
            with open(output_file, 'rb') as f:
                return f.read()
                
    except Exception as e:
        st.error(f"❌ Erro ao combinar áudios: {str(e)}")
        return None

# ==================== INTERFACE ====================

st.markdown("---")
st.subheader("🎭 Apresentadores")

col1, col2 = st.columns(2)
with col1:
    st.info("**👨 Brian**\n\nVoz grave e consistente\nTom profissional estável\nApresentador principal")
with col2:
    st.success("**👩 Matilda**\n\nVoz PT-BR natural\nTom técnico e claro\nEspecialista convidada")

# Estrutura
st.markdown("---")
st.subheader("📻 Estrutura do Podcast")

col1, col2, col3 = st.columns(3)
with col1:
    status_abertura = "✅" if jingle_abertura else "⏳"
    st.info(f"**{status_abertura} Abertura**\n\nJingle musical\n~5-10s")
with col2:
    st.success("**🎙️ Corpo Principal**\n\nDiálogo expandido\n~3-4 minutos")
with col3:
    status_encerramento = "✅" if jingle_encerramento else "⏳"
    st.warning(f"**{status_encerramento} Encerramento**\n\nJingle musical\n~5-10s")

# Duração total
total_dialogos = len(roteiro)
duracao_estimada = f"{total_dialogos * 15} - {total_dialogos * 20} segundos"
st.info(f"📊 **Duração estimada do diálogo:** {duracao_estimada} | **Total de falas:** {total_dialogos}")

# Roteiro
st.markdown("---")
with st.expander("📝 Ver Roteiro Completo (Expandido)"):
    for i, item in enumerate(roteiro, 1):
        st.write(f"**{i}. {item['descricao']}**")
        st.write(f"_{item['nome']}: {item['texto']}_")
        st.divider()

# Info
with st.expander("⚙️ Melhorias desta Versão"):
    st.markdown("""
    **✅ Correções aplicadas:**
    - 🔧 **Qualidade de áudio melhorada:** formato MP3 44.1kHz 128kbps
    - 🔧 **Estabilidade aumentada:** 0.75 para Brian, 0.65 para Matilda
    - 🔧 **Validação de áudio:** verifica se o áudio foi gerado corretamente
    - 📏 **Podcast expandido:** de ~1min para 3-4 minutos
    - 💬 **Mais conteúdo:** 15 falas ao invés de 11
    - 🎯 **Mais profundidade:** explicações detalhadas sobre a reforma
    
    **Estrutura do podcast:**
    1. 🎵 **Jingle de Abertura** (seu arquivo)
    2. 🎙️ **Diálogo expandido** (gerado com ElevenLabs - SEM chiados!)
    3. 🎵 **Jingle de Encerramento** (seu arquivo)
    
    **Resultado:** Podcast profissional de 3-4 minutos em alta qualidade!
    """)

# ==================== BOTÃO GERAR ====================

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Verificar avisos
    mensagem_aviso = ""
    if not jingle_abertura and not jingle_encerramento:
        mensagem_aviso = "⚠️ Gerando sem jingles (somente falas)"
    elif not jingle_abertura:
        mensagem_aviso = "⚠️ Sem jingle de abertura"
    elif not jingle_encerramento:
        mensagem_aviso = "⚠️ Sem jingle de encerramento"
    
    if mensagem_aviso:
        st.warning(mensagem_aviso)
    
    if st.button("🎙️ **GERAR PODCAST EXPANDIDO**", type="primary", use_container_width=True):
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        audio_segments = []
        failed = False
        
        # Gerar falas
        for i, item in enumerate(roteiro):
            if failed:
                break
                
            status_text.text(f"🎤 Gerando: {item['descricao']}...")
            progress_bar.progress((i / len(roteiro)) * 0.85)
            
            audio = generate_audio_stable(item['texto'], item['voz'])
            
            if audio and len(audio) > 1000:  # Verificar se áudio é válido
                audio_segments.append(audio)
                st.success(f"✅ {item['descricao']} - {len(audio)} bytes")
            else:
                st.error(f"❌ Falha ao gerar: {item['descricao']}")
                failed = True
                break
            
            time.sleep(0.5)  # Delay para evitar rate limit
        
        # Combinar tudo
        if not failed and len(audio_segments) == len(roteiro):
            status_text.text("🎬 Combinando áudios com jingles...")
            progress_bar.progress(0.95)
            
            # Resetar file uploaders
            if jingle_abertura:
                jingle_abertura.seek(0)
            if jingle_encerramento:
                jingle_encerramento.seek(0)
            
            final_podcast = combine_audios_with_jingles(
                audio_segments,
                jingle_start=jingle_abertura,
                jingle_end=jingle_encerramento
            )
            
            if final_podcast:
                progress_bar.progress(1.0)
                status_text.text("✅ Podcast pronto!")
                
                st.markdown("---")
                st.subheader("🎧 Alfa Bureau Cast - Versão Expandida Final")
                
                # Mostrar estrutura
                estrutura = []
                if jingle_abertura:
                    estrutura.append("🎵 Jingle Abertura")
                estrutura.append(f"🎙️ Diálogo ({len(roteiro)} falas)")
                if jingle_encerramento:
                    estrutura.append("🎵 Jingle Encerramento")
                
                st.info(f"**Estrutura:** {' + '.join(estrutura)}")
                
                # Estatísticas
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Falas Geradas", len(roteiro))
                with col_stat2:
                    st.metric("Tamanho Final", f"{len(final_podcast) / 1024 / 1024:.1f} MB")
                with col_stat3:
                    st.metric("Duração Estimada", "3-4 min")
                
                # Player de áudio
                st.audio(final_podcast, format="audio/wav")
                
                # Download
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        label="📥 Download Podcast Expandido (.wav)",
                        data=final_podcast,
                        file_name="alfa_bureau_podcast_EXPANDIDO_v2.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
                with col_b:
                    st.metric("Qualidade", "PREMIUM ⭐")
                
                st.success("🎉 Podcast PROFISSIONAL EXPANDIDO gerado com sucesso!")
                st.balloons()
        else:
            st.error("❌ Falha na geração. Verifique sua API Key e conexão.")

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px;'>
    <h3 style='color: white; margin: 0;'>💎 Versão 2.0 - Expandida e Corrigida</h3>
    <p style='color: white; margin: 5px 0 0 0;'>SEM chiados | 3-4 minutos | 15 falas | Alta qualidade</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
with st.expander("🐛 Troubleshooting"):
    st.markdown("""
    **Se ainda tiver chiado:**
    1. Verifique se sua API Key está correta
    2. Teste com textos menores primeiro
    3. Aumente o delay entre as gerações (linha time.sleep)
    4. Verifique sua conexão de internet
    
    **Se o podcast ficou muito longo:**
    - Remova algumas falas do meio do roteiro
    - Ou reduza o texto de cada fala
    
    **Para converter WAV para MP3:**
    ```bash
    ffmpeg -i podcast.wav -b:a 192k podcast.mp3
    ```
    """)