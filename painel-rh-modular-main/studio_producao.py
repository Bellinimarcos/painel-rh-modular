"""
ESTDIO DE PRODUO DE ÁUDIO PROFISSIONAL
Alfa Bureau & IPSI - Consultoria em Saúde Organizacional

Produção de:
- Vinhetas (5-30s)
- Spots comerciais (30s, 45s, 60s)
- Jingles
- Campanhas temáticas

VOZES DISPONÍVEIS:
- Brian (masculino grave)
- Carla (feminino institucional)
- Marcos (masculino novo)
"""

import streamlit as st
import time
import subprocess
import tempfile
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

st.set_page_config(
    page_title="Estúdio de Produção - Alfa Bureau & IPSI",
    page_icon="️",
    layout="wide"
)

st.title("️ Estúdio de Produção de Áudio Profissional")
st.markdown("**Alfa Bureau & IPSI - Vinhetas, Spots e Jingles**")

# ==================== VOZES DISPONÍVEIS ====================
VOZES = {
    "Brian": "nPczCjzI2devNBz1zQrb",
    "Nova Voz Feminina": "7iqXtOF3wl3pomwXFY7G",
    "Marcos": "o75NIGuHI95TephWNapV",
    "Carla": "m151rjrbWXbBqyq56tly"
}

# ==================== SELEO DE EMPRESA ====================
st.markdown("---")
st.subheader(" Selecione a Empresa")

empresa = st.radio(
    "Para qual empresa deseja criar o conteúdo?",
    options=["Alfa Bureau", "IPSI - Consultoria em Saúde Organizacional"],
    horizontal=True
)

# ==================== SELEO DE VOZES ====================
st.markdown("---")
st.subheader(" Configurar Vozes")

col1, col2 = st.columns(2)

with col1:
    voz_masculina = st.selectbox(
        "Voz Masculina Principal:",
        options=list(VOZES.keys()),
        index=0,  # Brian por padrão
        help="Escolha a voz masculina para apresentador/locutor principal"
    )

with col2:
    voz_feminina = st.selectbox(
        "Voz Feminina:",
        options=list(VOZES.keys()),
        index=1,  # Nova Voz Feminina por padrão
        help="Escolha a voz feminina para locutora/especialista"
    )

st.info(f" Configuração: **{voz_masculina}** (masculino) + **{voz_feminina}** (feminino)")

# ==================== BIBLIOTECA DE CONTEDOS ====================

# ALFA BUREAU - Conteúdos
alfa_bureau_biblioteca = {
    "Vinhetas 50 segundos (2 vozes)": [
        {
            "nome": "Reforma Tributária 2026 - Marketing Otimizado",
            "duracao": "43s + vinhetas (total ~50s)",
            "roteiro": [
                {
                    "texto": "Atenção! Em 2026 começa a maior mudança tributária das últimas décadas. CBS substitui PIS e Cofins com regras diferentes!",
                    "tipo": "feminino"
                },
                {
                    "texto": "Créditos ampliados: máquinas, serviços, energia, tudo gerando abatimento! Mas cuidado: quem não se preparar pode perder dinheiro e ter problemas!",
                    "tipo": "masculino"
                },
                {
                    "texto": "Preços vão mudar, seu caixa será impactado. O imposto muda para destino. São mudanças complexas!",
                    "tipo": "feminino"
                },
                {
                "texto": "Alfa Bureau: estratégia personalizada para 2026. Fale conosco e transforme complexidade em simplicidade!",
                    "tipo": "masculino"
                }
            ]
        },
        {
            "nome": "Reforma Tributária 2026",
            "duracao": "50s",
            "roteiro": [
                {
                    "texto": "Atenção empresário! A Reforma Tributária de 2026 está chegando e vai mudar completamente a forma como sua empresa paga impostos.",
                    "tipo": "masculino"
                },
                {
                    "texto": "Cinco impostos atuais serão substituídos por apenas dois. O sistema de créditos muda totalmente. Quem não se preparar pode ter sérios problemas!",
                    "tipo": "feminino"
                },
                {
                    "texto": "A Alfa Bureau está ajudando empresas a se prepararem com diagnóstico completo e plano de ação personalizado.",
                    "tipo": "masculino"
                },
                {
                    "texto": "Entre em contato com a Alfa Bureau. Transformando complexidade em simplicidade!",
                    "tipo": "feminino"
                }
            ]
        },
        {
            "nome": "Gestão Empresarial Inteligente",
            "duracao": "50s",
            "roteiro": [
                {
                    "texto": "Você sabe quanto tempo perde todo mês com burocracia tributária? Impostos, obrigações acessórias, fiscalização.",
                    "tipo": "masculino"
                },
                {
                    "texto": "E se você pudesse ter uma equipe de especialistas cuidando de tudo isso para você? Assessoria completa, planejamento estratégico, economia garantida.",
                    "tipo": "feminino"
                },
                {
                    "texto": "Alfa Bureau: mais de 20 anos simplificando a gestão de empresas brasileiras.",
                    "tipo": "masculino"
                },
                {
                    "texto": "Fale conosco e descubra como transformar impostos em estratégia. Alfa Bureau!",
                    "tipo": "feminino"
                }
            ]
        },
        {
            "nome": "Planejamento Tributário",
            "duracao": "50s",
            "roteiro": [
                {
                    "texto": "Sua empresa está pagando impostos demais? Muitos empresários descobrem tarde demais que poderiam economizar milhares de reais todo mês.",
                    "tipo": "feminino"
                },
                {
                    "texto": "Com planejamento tributário inteligente, você identifica oportunidades legais de redução de carga tributária e aumenta sua competitividade.",
                    "tipo": "masculino"
                },
                {
                    "texto": "A Alfa Bureau tem especialistas prontos para analisar sua empresa e encontrar as melhores soluções.",
                    "tipo": "feminino"
                },
                {
                    "texto": "Não pague mais do que o necessário! Alfa Bureau: especialistas em transformar impostos em estratégia!",
                    "tipo": "masculino"
                }
            ]
        }
    ],
    
    "Vinhetas Curtas (5-10s)": [
        {
            "nome": "Vinheta Institucional 1",
            "duracao": "5s",
            "roteiro": [
                {
                    "texto": "Alfa Bureau: transformando complexidade em simplicidade, garantindo sua competitividade!",
                    "tipo": "feminino"
                }
            ]
        },
        {
            "nome": "Vinheta Institucional 2",
            "duracao": "7s",
            "roteiro": [
                {
                    "texto": "Alfa Bureau. Gestão empresarial inteligente. Resultados que você pode contar!",
                    "tipo": "masculino"
                }
            ]
        },
        {
            "nome": "Vinheta Call to Action",
            "duracao": "8s",
            "roteiro": [
                {
                    "texto": "Precisa de assessoria contábil e tributária de excelência? Alfa Bureau. Fale conosco!",
                    "tipo": "feminino"
                }
            ]
        }
    ],
    
    "Spots 30 segundos": [
        {
            "nome": "Reforma Tributária - Urgência",
            "duracao": "30s",
            "roteiro": [
                {
                    "texto": "2026 está chegando e com ele a maior Reforma Tributária da história. Sua empresa está preparada?",
                    "tipo": "masculino"
                },
                {
                    "texto": "Novos impostos, novas regras, novas obrigações. A Alfa Bureau oferece diagnóstico completo e plano de ação personalizado.",
                    "tipo": "feminino"
                },
                {
                    "texto": "Não deixe para última hora! Entre em contato com a Alfa Bureau e prepare seu negócio para o futuro.",
                    "tipo": "masculino"
                }
            ]
        },
        {
            "nome": "Planejamento Tributário",
            "duracao": "30s",
            "roteiro": [
                {
                    "texto": "Sua empresa está pagando impostos demais?  hora de fazer um planejamento tributário inteligente!",
                    "tipo": "feminino"
                },
                {
                    "texto": "A Alfa Bureau identifica oportunidades de economia legal, reduz sua carga tributária e aumenta sua competitividade.",
                    "tipo": "masculino"
                },
                {
                    "texto": "Alfa Bureau: especialistas em transformar impostos em estratégia. Agende sua consultoria!",
                    "tipo": "feminino"
                }
            ]
        }
    ],
    
    "Spots 60 segundos": [
        {
            "nome": "Institucional Completo",
            "duracao": "60s",
            "roteiro": [
                {
                    "texto": "Todo empresário sabe: gestão tributária é complexa, burocrática e consome tempo precioso do seu negócio.",
                    "tipo": "masculino"
                },
                {
                    "texto": "Mas e se você pudesse ter uma equipe de especialistas cuidando disso para você?  exatamente isso que a Alfa Bureau oferece!",
                    "tipo": "feminino"
                },
                {
                    "texto": "Assessoria contábil completa, planejamento tributário estratégico, gestão de obrigações acessórias e muito mais.",
                    "tipo": "masculino"
                },
                {
                    "texto": "Com a Alfa Bureau, você transforma complexidade em simplicidade e foca no que realmente importa: fazer seu negócio crescer!",
                    "tipo": "feminino"
                },
                {
                    "texto": "Alfa Bureau: mais de 20 anos simplificando a gestão de empresas brasileiras. Entre em contato e descubra como podemos ajudar você!",
                    "tipo": "masculino"
                }
            ]
        }
    ]
}

# IPSI - Conteúdos
ipsi_biblioteca = {
    "Vinhetas 50 segundos (2 vozes)": [
        {
            "nome": "Saúde Mental no Trabalho",
            "duracao": "50s",
            "roteiro": [
                {
                    "texto": "Estresse, ansiedade, burnout. A saúde mental dos seus colaboradores está em risco e isso afeta diretamente a produtividade da sua empresa.",
                    "tipo": "feminino"
                },
                {
                    "texto": "Colaboradores saudáveis emocionalmente são mais engajados, criativos e produtivos. E sua empresa tem papel fundamental nessa prevenção.",
                    "tipo": "masculino"
                },
                {
                    "texto": "A IPSI Consultoria oferece diagnóstico de riscos psicossociais, programas de prevenção e treinamentos especializados.",
                    "tipo": "feminino"
                },
                {
                    "texto": "IPSI: cuidando da saúde de quem faz sua empresa acontecer!",
                    "tipo": "masculino"
                }
            ]
        },
        {
            "nome": "Clima Organizacional",
            "duracao": "50s",
            "roteiro": [
                {
                    "texto": "Alta rotatividade? Conflitos frequentes? Baixa produtividade? Esses são sinais de que o clima organizacional da sua empresa precisa de atenção urgente.",
                    "tipo": "masculino"
                },
                {
                    "texto": "Um ambiente de trabalho saudável não é luxo, é necessidade.  investimento que traz retorno garantido em produtividade e resultados.",
                    "tipo": "feminino"
                },
                {
                    "texto": "A IPSI realiza pesquisas de clima, identifica problemas e propõe soluções práticas e eficazes para transformar sua empresa.",
                    "tipo": "masculino"
                },
                {
                    "texto": "IPSI Consultoria em Saúde Organizacional: porque colaborador feliz é empresa lucrativa!",
                    "tipo": "feminino"
                }
            ]
        },
        {
            "nome": "Qualidade de Vida no Trabalho",
            "duracao": "50s",
            "roteiro": [
                {
                    "texto": "Você investe em tecnologia, em infraestrutura, em marketing. Mas investe na saúde e bem-estar dos seus colaboradores?",
                    "tipo": "feminino"
                },
                {
                    "texto": "Empresas que cuidam das pessoas têm menos absenteísmo, maior retenção de talentos e equipes mais produtivas e motivadas.",
                    "tipo": "masculino"
                },
                {
                    "texto": "A IPSI desenvolve programas completos de qualidade de vida, ginástica laboral, gestão de estresse e promoção da saúde mental.",
                    "tipo": "feminino"
                },
                {
                    "texto": "Invista em quem faz sua empresa crescer. IPSI Consultoria: especialistas em saúde organizacional!",
                    "tipo": "masculino"
                }
            ]
        }
    ],
    
    "Vinhetas Curtas (5-10s)": [
        {
            "nome": "Vinheta Institucional 1",
            "duracao": "6s",
            "roteiro": [
                {
                    "texto": "IPSI Consultoria: cuidando da saúde de quem faz sua empresa acontecer!",
                    "tipo": "feminino"
                }
            ]
        },
        {
            "nome": "Vinheta Institucional 2",
            "duracao": "8s",
            "roteiro": [
                {
                    "texto": "IPSI: especialistas em saúde organizacional. Porque colaborador saudável é empresa produtiva!",
                    "tipo": "masculino"
                }
            ]
        }
    ],
    
    "Spots 30 segundos": [
        {
            "nome": "Saúde Mental no Trabalho",
            "duracao": "30s",
            "roteiro": [
                {
                    "texto": "Estresse, ansiedade, burnout. A saúde mental dos seus colaboradores está em risco?",
                    "tipo": "feminino"
                },
                {
                    "texto": "A IPSI Consultoria oferece diagnóstico completo de riscos psicossociais e programas de prevenção personalizados.",
                    "tipo": "masculino"
                },
                {
                    "texto": "Cuide de quem faz sua empresa crescer. IPSI Consultoria em Saúde Organizacional!",
                    "tipo": "feminino"
                }
            ]
        },
        {
            "nome": "Clima Organizacional",
            "duracao": "30s",
            "roteiro": [
                {
                    "texto": "Alta rotatividade? Baixa produtividade? Conflitos frequentes? O clima da sua empresa precisa de atenção!",
                    "tipo": "masculino"
                },
                {
                    "texto": "A IPSI realiza pesquisas de clima organizacional, identifica problemas e propõe soluções práticas e eficazes.",
                    "tipo": "feminino"
                },
                {
                    "texto": "Transforme o ambiente da sua empresa. IPSI Consultoria: especialistas em saúde organizacional!",
                    "tipo": "masculino"
                }
            ]
        }
    ],
    
    "Spots 60 segundos": [
        {
            "nome": "Campanha Setembro Amarelo",
            "duracao": "60s",
            "roteiro": [
                {
                    "texto": "Setembro Amarelo: mês de prevenção ao suicídio e valorização da vida. Mas saúde mental não deve ser pauta apenas em setembro.",
                    "tipo": "feminino"
                },
                {
                    "texto": "No ambiente de trabalho, o estresse, a pressão e o desgaste emocional são realidade. E sua empresa tem papel fundamental na prevenção.",
                    "tipo": "masculino"
                },
                {
                    "texto": "A IPSI Consultoria oferece programas de promoção da saúde mental, treinamentos para lideranças e diagnóstico de riscos psicossociais.",
                    "tipo": "feminino"
                },
                {
                    "texto": "Colaboradores saudáveis emocionalmente são mais produtivos, engajados e felizes. E isso reflete diretamente nos resultados da empresa!",
                    "tipo": "masculino"
                },
                {
                    "texto": "IPSI Consultoria em Saúde Organizacional: porque cuidar das pessoas é cuidar do negócio. Entre em contato!",
                    "tipo": "feminino"
                }
            ]
        }
    ]
}

# ==================== SELEO DE CONTEDO ====================

biblioteca = alfa_bureau_biblioteca if empresa == "Alfa Bureau" else ipsi_biblioteca

st.markdown("---")
st.subheader(" Biblioteca de Conteúdos")

categoria = st.selectbox(
    "Escolha a categoria:",
    options=list(biblioteca.keys())
)

conteudo_selecionado = st.selectbox(
    "Escolha o conteúdo:",
    options=biblioteca[categoria],
    format_func=lambda x: f"{x['nome']} ({x['duracao']})"
)

# Mostrar roteiro
st.markdown("---")
st.subheader(" Roteiro Selecionado")

with st.expander("Ver Roteiro Completo", expanded=True):
    for i, fala in enumerate(conteudo_selecionado['roteiro'], 1):
        voz_usada = voz_masculina if fala['tipo'] == 'masculino' else voz_feminina
        st.write(f"**{i}. {voz_usada}:**")
        st.write(f"_{fala['texto']}_")
        st.divider()

# ==================== UPLOAD JINGLES ====================
st.markdown("---")
st.subheader(" Jingles Musicais (Opcional)")

col1, col2 = st.columns(2)

with col1:
    usar_jingle_abertura = st.checkbox("Adicionar jingle de abertura?")
    if usar_jingle_abertura:
        jingle_abertura = st.file_uploader(
            "Upload jingle abertura",
            type=['mp3', 'wav', 'flac'],
            key="ab"
        )
    else:
        jingle_abertura = None

with col2:
    usar_jingle_fim = st.checkbox("Adicionar assinatura final?")
    if usar_jingle_fim:
        jingle_encerramento = st.file_uploader(
            "Upload assinatura",
            type=['mp3', 'wav', 'flac'],
            key="enc"
        )
    else:
        jingle_encerramento = None

# ==================== API ====================
try:
    api_key = st.secrets["ELEVENLABS_API_KEY"]
    client = ElevenLabs(api_key=api_key)
    st.success(" API conectada")
except:
    st.error(" Erro na API")
    st.stop()

project_root = Path(__file__).parent
ffmpeg_path = project_root / "ffmpeg.exe"
if not ffmpeg_path.exists():
    ffmpeg_path = "ffmpeg"

# ==================== FUNES ====================

def generate_audio(texto, voice_id):
    try:
        settings = VoiceSettings(
            stability=0.90,
            similarity_boost=0.85,
            style=0.15,
            use_speaker_boost=True
        )
        
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_turbo_v2_5",
            text=texto,
            voice_settings=settings,
            output_format="mp3_44100_192"
        )
        
        return b"".join(audio)
    except Exception as e:
        st.error(f" {str(e)}")
        return None

def combine_audios(segments, jingle_start=None, jingle_end=None):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            files = []
            
            if jingle_start:
                jp = temp_path / "js.mp3"
                jt = temp_path / f"jso.{jingle_start.name.split('.')[-1]}"
                with open(jt, 'wb') as f:
                    f.write(jingle_start.read())
                subprocess.run([str(ffmpeg_path), '-i', str(jt), '-acodec', 'libmp3lame', '-ar', '44100', '-b:a', '128k', str(jp), '-y'], capture_output=True)
                if jp.exists():
                    files.append(jp)
            
            for i, seg in enumerate(segments):
                sp = temp_path / f"s_{i:02d}.mp3"
                with open(sp, 'wb') as f:
                    f.write(seg)
                files.append(sp)
            
            if jingle_end:
                je = temp_path / "je.mp3"
                jte = temp_path / f"jeo.{jingle_end.name.split('.')[-1]}"
                with open(jte, 'wb') as f:
                    f.write(jingle_end.read())
                subprocess.run([str(ffmpeg_path), '-i', str(jte), '-acodec', 'libmp3lame', '-ar', '44100', '-b:a', '128k', str(je), '-y'], capture_output=True)
                if je.exists():
                    files.append(je)
            
            lf = temp_path / "list.txt"
            with open(lf, 'w', encoding='utf-8') as f:
                for fp in files:
                    f.write(f"file '{str(fp).replace(chr(92), '/')}'\n")
            
            output_file = temp_path / "final.mp3"
            
            # Otimizado para WhatsApp
            cmd = [
                str(ffmpeg_path),
                '-f', 'concat',
                '-safe', '0',
                '-i', str(lf),
                '-acodec', 'libmp3lame',
                '-b:a', '128k',
                '-ar', '44100',
                '-ac', '2',
                '-write_xing', '0',
                str(output_file),
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error(f"Erro FFmpeg: {result.stderr}")
                return None
            
            with open(output_file, 'rb') as f:
                return f.read()
    except Exception as e:
        st.error(f" {str(e)}")
        return None

# ==================== GERAO ====================

st.markdown("---")

if st.button(f"️ **PRODUZIR ÁUDIO - {empresa}**", type="primary", width='stretch'):
    progress = st.progress(0.0)
    status = st.empty()
    
    segments = []
    roteiro = conteudo_selecionado['roteiro']
    
    for i, fala in enumerate(roteiro):
        # Determinar qual voz usar
        voice_id = VOZES[voz_masculina] if fala['tipo'] == 'masculino' else VOZES[voz_feminina]
        voz_nome = voz_masculina if fala['tipo'] == 'masculino' else voz_feminina
        
        status.text(f" Gravando: {voz_nome}...")
        progress.progress((i / len(roteiro)) * 0.85)
        
        audio = generate_audio(fala['texto'], voice_id)
        
        if audio:
            segments.append(audio)
            st.success(f" {voz_nome}")
        else:
            st.error(f" Erro: {voz_nome}")
            break
        
        time.sleep(0.5)
    
    if len(segments) == len(roteiro):
        status.text(" Finalizando...")
        progress.progress(0.95)
        
        if jingle_abertura:
            jingle_abertura.seek(0)
        if jingle_encerramento:
            jingle_encerramento.seek(0)
        
        final = combine_audios(segments, jingle_abertura, jingle_encerramento)
        
        if final:
            progress.progress(1.0)
            status.text(" Pronto!")
            
            st.markdown("---")
            st.markdown(f"##  {conteudo_selecionado['nome']}")
            
            st.success(f" **Áudio com {voz_masculina} + {voz_feminina} - Otimizado para WhatsApp!**")
            
            nome_empresa = "ALFA_BUREAU" if empresa == "Alfa Bureau" else "IPSI"
            nome_arquivo = f"{nome_empresa}_{conteudo_selecionado['nome'].replace(' ', '_')}.mp3"
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label=f" BAIXAR ÁUDIO (.mp3)",
                    data=final,
                    file_name=nome_arquivo,
                    mime="audio/mp3",
                    width='stretch',
                    type="primary"
                )
            
            with col2:
                st.metric("Formato", "MP3 128kbps")
                st.caption(" WhatsApp, Instagram, Rádio")
            
            st.info("""
            ** Como enviar no WhatsApp:**
            1. Baixe o arquivo
            2. WhatsApp > Anexar > Documento
            3. Selecione o MP3
            4. Envie!
            """)
            
            with st.expander(" Preview"):
                st.audio(final, format="audio/mp3")
            
            st.success(f" Produzido para {empresa}!")
            st.balloons()

st.markdown("---")
st.info(f"️ **Estúdio Profissional** | Vozes: {voz_masculina} + {voz_feminina} | WhatsApp Ready")


