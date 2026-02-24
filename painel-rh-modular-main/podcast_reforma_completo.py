"""
Podcast Profissional - Alfa Bureau Cast
REFORMA TRIBUTÁRIA 2026 - Versão Completa para Pequenas Empresas
5-7 minutos de conteúdo aprofundado
"""

import streamlit as st
import time
import subprocess
import tempfile
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# ==================== CONFIGURAO ====================
st.set_page_config(
    page_title="Podcast Reforma Tributária Completo",
    page_icon="️",
    layout="wide"
)

st.title("️ Alfa Bureau Cast - Reforma Tributária 2026")
st.markdown("**Guia Completo para Pequenas Empresas (5-7 minutos)**")

# ==================== UPLOAD DE JINGLES ====================
st.markdown("---")
st.subheader(" Faça Upload dos seus Jingles")

col1, col2 = st.columns(2)

with col1:
    st.info("** Jingle de Abertura**")
    jingle_abertura = st.file_uploader(
        "Escolha o arquivo de áudio",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'mp2', 'wma'],
        key="abertura"
    )
    if jingle_abertura:
        st.success(f" {jingle_abertura.name}")

with col2:
    st.warning("** Jingle de Encerramento**")
    jingle_encerramento = st.file_uploader(
        "Escolha o arquivo de áudio",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'mp2', 'wma'],
        key="encerramento"
    )
    if jingle_encerramento:
        st.success(f" {jingle_encerramento.name}")

# ==================== ROTEIRO EXPANDIDO - 5-7 MINUTOS ====================
roteiro = [
    # ABERTURA
    {
        "texto": "Olá empresários! Sejam muito bem-vindos a mais um episódio do Alfa Bureau Cast. Hoje vamos falar sobre um tema que está movimentando o mundo dos negócios: a Reforma Tributária de 2026. E para nos ajudar a descomplicar esse assunto, temos aqui a Carla, nossa especialista em tributos. Carla, vamos começar pelo básico: o que é essa tal Reforma Tributária?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Abertura"
    },
    {
        "texto": "Olá Brian! Com prazer! Olha, a Reforma Tributária é a maior mudança no sistema de impostos brasileiro das últimas décadas. O objetivo é simplificar toda aquela burocracia que temos hoje. Vários impostos que conhecemos vão ser substituídos por apenas dois novos impostos principais.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Explicação Inicial"
    },
    {
        "texto": "Interessante! E quais impostos vão acabar?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Pergunta 1"
    },
    {
        "texto": "Vão acabar o PIS, Cofins, IPI, que são federais, além do ICMS estadual e o ISS municipal. No lugar deles, teremos a CBS, que é a Contribuição sobre Bens e Serviços, e o IBS, que é o Imposto sobre Bens e Serviços.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Impostos"
    },
    
    # FOCO EM 2026
    {
        "texto": "E o que muda especificamente em 2026?  quando tudo começa?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Foco 2026"
    },
    {
        "texto": "Exatamente! 2026 é o ano que marca o início dessa transição. A primeira grande mudança é a chegada da CBS, que vai começar a substituir o PIS e a Cofins. Será um ano de testes, então as alíquotas começam bem pequenas. Mas é fundamental que as empresas já estejam preparadas!",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - 2026"
    },
    {
        "texto": "E como funciona essa CBS?  muito diferente do que temos hoje?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - CBS"
    },
    {
        "texto": "Sim, é bem diferente! A CBS funciona como um IVA, que significa Imposto sobre Valor Agregado. O grande diferencial é o sistema de créditos. Toda vez que sua empresa compra algo relacionado ao negócio, você gera um crédito que pode ser usado para abater o imposto que você vai pagar nas suas vendas.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Sistema CBS"
    },
    
    # CRDITOS
    {
        "texto": "Esse sistema de créditos parece interessante. Pode explicar melhor como funciona na prática?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Créditos"
    },
    {
        "texto": "Claro! Imagine que você compre matéria-prima, pague energia, aluguel, ou até serviços de marketing. Com o novo sistema, quase todas essas despesas vão gerar crédito tributário.  como se você ganhasse um vale que depois vai usar para pagar menos imposto quando vender seus produtos ou serviços. E aqui vem uma ótima notícia: se você comprar máquinas, equipamentos ou veículos para o negócio, poderá usar o crédito de uma vez só, sem ter que esperar anos como acontece hoje!",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Explicação Créditos"
    },
    {
        "texto": "Isso pode melhorar o fluxo de caixa das empresas então?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Caixa"
    },
    {
        "texto": "Com certeza! Como você terá mais créditos nas suas compras, é possível que seu caixa fique melhor porque você pagará menos imposto direto. Mas atenção: isso exige um controle rigoroso para usar os créditos corretamente e não perder dinheiro.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Gestão Créditos"
    },
    
    # SIMPLES NACIONAL
    {
        "texto": "E as empresas do Simples Nacional? Como ficam nessa história toda?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Simples"
    },
    {
        "texto": "As empresas do Simples Nacional não precisam migrar para o novo sistema imediatamente. Vocês continuarão pagando o imposto unificado como hoje. Mas tem uma novidade boa: se uma empresa do Simples vender para uma empresa maior, essa empresa maior poderá usar o crédito do imposto que a do Simples pagou. Isso pode abrir mais oportunidades de negócio!",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Simples"
    },
    
    # IMPACTO EM PREOS
    {
        "texto": "Uma dúvida que deve estar na cabeça de muita gente: os preços vão mudar?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Preços"
    },
    {
        "texto": " bem provável que sim. Para alguns produtos e serviços, o imposto pode ficar mais barato, para outros, mais caro. A boa notícia é que com o fim da cobrança em cascata, onde um imposto é cobrado em cima do outro, a tendência é que a carga tributária final sobre o consumo possa ser reduzida em vários setores. Mas cada empresa precisará recalcular seus custos e repensar sua precificação.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Precificação"
    },
    
    # RISCOS
    {
        "texto": "E quais são os principais riscos se uma empresa não se preparar adequadamente?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Riscos"
    },
    {
        "texto": "Os riscos são sérios! Erros na emissão de notas fiscais podem gerar multas pesadas. Tem também a perda de dinheiro por não aproveitar os créditos corretamente, dificuldade em calcular preços de venda, e claro, problemas com a fiscalização. Por isso é tão importante começar a se preparar agora, em 2025!",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Riscos Detalhados"
    },
    
    # AES PRÁTICAS
    {
        "texto": "Então Carla, quais são os primeiros passos que um empresário deve tomar já agora para se preparar?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Ações"
    },
    {
        "texto": "Primeiro: converse urgentemente com seu contador. Ele é seu principal aliado nesse processo. Segundo: mapeie todos os impostos que você paga hoje e entenda seus benefícios fiscais. Terceiro: analise seus produtos e serviços pensando em como os novos impostos vão afetar seus custos. Quarto: comece a preparar seus sistemas de emissão de notas, porque virá um novo documento fiscal eletrônico nacional que vai unificar tudo. E quinto: fique de olho nas notícias e atualizações, porque ainda virão muitas regulamentações detalhando a reforma.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Passo a Passo"
    },
    
    # BENEFÍCIOS
    {
        "texto": "Para finalizar, quais são os principais benefícios que essa reforma pode trazer para as pequenas empresas?",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Benefícios"
    },
    {
        "texto": "Olha, os benefícios são grandes! Teremos simplificação radical, com menos impostos para entender e menos burocracia. O sistema de crédito amplo permite que mais compras gerem crédito, reduzindo o imposto a pagar. Acaba a guerra fiscal entre estados, o que significa mais competitividade para todos. E por fim, teremos mais segurança jurídica, com um sistema mais claro que reduz a insegurança sobre como os impostos são aplicados.",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Benefícios"
    },
    
    # ENCERRAMENTO
    {
        "texto": "Perfeito Carla! Acho que conseguimos trazer muita clareza sobre esse tema tão importante. Muito obrigado pela participação!",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Agradecimento"
    },
    {
        "texto": "Imagina Brian! E galera, lembrem-se: 2026 está logo ali! Não deixem para a última hora. Quem se preparar antes terá uma enorme vantagem competitiva!",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Alerta"
    },
    {
        "texto": "Exatamente! E para quem quer fazer um diagnóstico completo e personalizado da situação da sua empresa, a Alfa Bureau está pronta para ajudar. Nossa equipe de especialistas pode fazer uma análise detalhada, mapear todos os impactos da reforma no seu negócio, e criar um plano de ação sob medida. Entre em contato conosco e garanta que sua empresa esteja preparada para essa transformação!",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - CTA Completo"
    },
    {
        "texto": "E não percam os próximos episódios do Alfa Bureau Cast! Vamos continuar trazendo conteúdo prático e relevante para você, empresário, navegar com segurança por essas mudanças. Até a próxima!",
        "voz": "m151rjrbWXbBqyq56tly",
        "nome": "Carla",
        "descricao": " Carla - Convite Final"
    },
    {
        "texto": "Um abraço a todos e fiquem ligados!",
        "voz": "nPczCjzI2devNBz1zQrb",
        "nome": "Brian",
        "descricao": " Brian - Despedida"
    }
]

# ==================== VERIFICAR API ====================
try:
    api_key = st.secrets["ELEVENLABS_API_KEY"]
    client = ElevenLabs(api_key=api_key)
    st.success(" ElevenLabs API carregada!")
except Exception as e:
    st.error(f" Erro: {str(e)}")
    st.stop()

# FFmpeg
project_root = Path(__file__).parent
ffmpeg_path = project_root / "ffmpeg.exe"
if not ffmpeg_path.exists():
    ffmpeg_path = "ffmpeg"

# ==================== FUNES ====================

def generate_audio_stable(texto, voice_id, nome_voz):
    """Gera áudio usando ElevenLabs - Turbo V2.5"""
    try:
        if voice_id == "nPczCjzI2devNBz1zQrb":  # Brian
            settings = VoiceSettings(
                stability=0.85,
                similarity_boost=0.80,
                style=0.20,
                use_speaker_boost=True
            )
        else:  # Carla
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
        st.error(f" Erro: {str(e)}")
        return None


def combine_audios_with_jingles(audio_segments, jingle_start=None, jingle_end=None):
    """Combina áudios com FFmpeg"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_list = []
            
            # Jingle abertura
            if jingle_start:
                jingle_start_path = temp_path / "jingle_start.mp3"
                jingle_temp = temp_path / f"jingle_orig.{jingle_start.name.split('.')[-1]}"
                with open(jingle_temp, 'wb') as ft:
                    ft.write(jingle_start.read())
                
                subprocess.run([
                    str(ffmpeg_path),
                    '-i', str(jingle_temp),
                    '-acodec', 'libmp3lame',
                    '-ar', '44100',
                    '-b:a', '192k',
                    str(jingle_start_path),
                    '-y'
                ], capture_output=True)
                
                if jingle_start_path.exists():
                    file_list.append(jingle_start_path)
            
            # Segmentos
            for i, segment in enumerate(audio_segments):
                segment_path = temp_path / f"segment_{i:02d}.mp3"
                with open(segment_path, 'wb') as f:
                    f.write(segment)
                file_list.append(segment_path)
            
            # Jingle encerramento
            if jingle_end:
                jingle_end_path = temp_path / "jingle_end.mp3"
                jingle_temp = temp_path / f"jingle_end_orig.{jingle_end.name.split('.')[-1]}"
                with open(jingle_temp, 'wb') as ft:
                    ft.write(jingle_end.read())
                
                subprocess.run([
                    str(ffmpeg_path),
                    '-i', str(jingle_temp),
                    '-acodec', 'libmp3lame',
                    '-ar', '44100',
                    '-b:a', '192k',
                    str(jingle_end_path),
                    '-y'
                ], capture_output=True)
                
                if jingle_end_path.exists():
                    file_list.append(jingle_end_path)
            
            # Lista
            list_file = temp_path / "filelist.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for file_path in file_list:
                    f.write(f"file '{str(file_path).replace(chr(92), '/')}'\n")
            
            output_file = temp_path / "podcast_final.mp3"
            
            # Combinar
            subprocess.run([
                str(ffmpeg_path),
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy',
                str(output_file),
                '-y'
            ], capture_output=True)
            
            with open(output_file, 'rb') as f:
                return f.read()
                
    except Exception as e:
        st.error(f" Erro: {str(e)}")
        return None

# ==================== INTERFACE ====================

st.markdown("---")
st.subheader(" Estrutura do Podcast Completo")

col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"** Abertura**\nJingle\n~{len(roteiro)} falas")
with col2:
    st.success(f"**️ Conteúdo**\nBrian + Carla\n5-7 minutos")
with col3:
    st.warning("** Encerramento**\nJingle\n~24s")

st.info(f" **Total de falas:** {len(roteiro)} | **Duração estimada:** 5-7 minutos")

with st.expander(" Ver Roteiro Completo (25 falas)"):
    for i, item in enumerate(roteiro, 1):
        st.write(f"**{i}. {item['descricao']}**")
        st.caption(f"{item['nome']}: {item['texto'][:100]}...")
        st.divider()

# ==================== GERAR ====================

st.markdown("---")

if st.button("️ **GERAR PODCAST COMPLETO (5-7 MIN)**", type="primary", width='stretch'):
    progress_bar = st.progress(0.0)
    status_text = st.empty()
    
    audio_segments = []
    failed = False
    
    for i, item in enumerate(roteiro):
        if failed:
            break
            
        status_text.text(f" {item['descricao']}...")
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
        status_text.text(" Combinando...")
        progress_bar.progress(0.95)
        
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
            status_text.text(" Pronto!")
            
            st.markdown("---")
            st.subheader(" Reforma Tributária 2026 - Podcast Completo")
            
            st.warning("️ **IMPORTANTE:** Baixe o arquivo para ouvir completo!")
            
            st.markdown("###  DOWNLOAD")
            st.download_button(
                label="️ BAIXAR PODCAST COMPLETO (.mp3)",
                data=final_podcast,
                file_name="reforma_tributaria_2026_completo.mp3",
                mime="audio/mp3",
                width='stretch',
                type="primary"
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Falas", len(roteiro))
            with col2:
                st.metric("Tamanho", f"{len(final_podcast) / 1024 / 1024:.1f} MB")
            with col3:
                st.metric("Duração", "5-7 min")
            
            st.success(" Podcast gerado com sucesso!")
            st.balloons()

st.markdown("---")
st.info(" **Podcast Expandido** | 25 falas | Conteúdo aprofundado | Brian + Carla")


