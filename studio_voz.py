import streamlit as st
import requests
import base64
import io
import wave
from pathlib import Path
import time

# Configuração da página
st.set_page_config(
    page_title="Estúdio de Voz Profissional",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Estúdio de Voz Profissional - Alfa Bureau")
st.markdown("**Comercial Reforma Tributária 2026**")

# Roteiro do comercial
roteiro = [
    {"texto": "Atenção empreendedores! A Reforma Tributária de 2026 está chegando e vai revolucionar a rotina da sua empresa.", "voz": "Puck"},
    {"texto": "Os impostos atuais ISS ICMS PIS e Cofins serão substituídos por apenas dois novos tributos o IBS e o CBS.", "voz": "Kore"},
    {"texto": "Isso significa mudanças profundas no cálculo de preços no pagamento de impostos e no controle financeiro.", "voz": "Puck"},
    {"texto": "Será fundamental revisar contratos atualizar sistemas e gerenciar créditos tributários com precisão.", "voz": "Kore"},
    {"texto": "Sua empresa está preparada para esta virada?", "voz": "Puck"},
    {"texto": "A Alfa Bureau está ao seu lado para decifrar mudanças planejar estratégias e adaptar seu negócio.", "voz": "Kore"},
    {"texto": "Alfa Bureau transformando complexidade em simplicidade garantindo competitividade.", "voz": "Puck"}
]

# Verificar chave API
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success("✅ Chave API carregada com sucesso!")
except Exception as e:
    st.error("❌ Erro ao carregar chave API do secrets.toml")
    st.stop()

# Função para converter PCM para WAV
def pcm_to_wav(pcm_data, sample_rate=24000):
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    wav_buffer.seek(0)
    return wav_buffer.read()

# Função para gerar áudio - VERSÃO CORRIGIDA
def generate_audio(texto, voz, api_key, max_retries=3):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
    
    # CORREÇÃO: Enviando apenas o texto sem instruções de estilo
    # O Gemini TTS deve receber apenas o texto a ser narrado
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": texto  # Apenas o texto, sem instruções de estilo
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voz
                    }
                }
            }
        }
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=120)
            
            if response.status_code == 429:
                st.error("⏳ Limite de API excedido. Aguarde 1 hora.")
                return None
            elif response.status_code == 403:
                st.error("🔐 Chave API inválida ou sem permissão para TTS.")
                return None
            elif response.status_code == 500:
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ Erro 500 (servidor Google). Tentativa {attempt + 2}/{max_retries} em 5s...")
                    time.sleep(5)
                    continue
                else:
                    st.error("❌ Servidor do Google instável. Aguarde 10 minutos e tente novamente.")
                    return None
            
            response.raise_for_status()
            result = response.json()
            
            # Verificar se o áudio foi gerado
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "inlineData" in parts[0]:
                        audio_data = parts[0]["inlineData"]["data"]
                        
                        pcm_data = base64.b64decode(audio_data)
                        wav_data = pcm_to_wav(pcm_data)
                        return wav_data
                    else:
                        st.error("❌ Resposta da API não contém dados de áudio")
                        return None
            else:
                st.error("❌ Resposta vazia da API")
                return None
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏰ Timeout. Tentando novamente ({attempt + 2}/{max_retries})...")
                time.sleep(5)
            else:
                st.error("❌ Timeout após múltiplas tentativas.")
                return None
                
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ Erro: {str(e)[:100]}. Tentando novamente...")
                time.sleep(5)
            else:
                st.error(f"❌ Erro após {max_retries} tentativas: {str(e)[:100]}")
                return None
    
    return None

# Função para combinar áudios com silêncio entre eles
def combine_audios(audio_segments):
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        combined = AudioSegment.empty()
        silence = AudioSegment.silent(duration=500)  # 500ms de silêncio entre trechos
        
        for i, segment in enumerate(audio_segments):
            audio = AudioSegment.from_wav(io.BytesIO(segment))
            combined += audio
            
            # Adicionar silêncio entre os trechos (exceto após o último)
            if i < len(audio_segments) - 1:
                combined += silence
        
        # Normalizar volume
        combined = combined.normalize()
        
        output = io.BytesIO()
        combined.export(output, format="wav")
        output.seek(0)
        return output.read()
    except ImportError:
        st.warning("⚠️ PyDub não disponível. Instale com: pip install pydub")
        st.info("Retornando apenas o primeiro segmento. Instale PyDub para combinar todos.")
        return audio_segments[0] if audio_segments else None

# Interface para testar voz individual
st.markdown("---")
st.subheader("🔧 Teste de Voz Individual")

col1, col2 = st.columns(2)
with col1:
    test_voice = st.selectbox("Escolha a voz:", ["Puck", "Kore"])
with col2:
    test_text = st.text_input("Texto de teste:", "Olá, este é um teste de voz.")

if st.button("🎤 Testar Voz"):
    with st.spinner("Gerando áudio de teste..."):
        test_audio = generate_audio(test_text, test_voice, api_key)
        if test_audio:
            st.audio(test_audio, format="audio/wav")
            st.success("✅ Áudio de teste gerado!")
        else:
            st.error("❌ Erro ao gerar áudio de teste")

# Exibir roteiro
st.markdown("---")
st.subheader("📝 Roteiro do Comercial")
for i, item in enumerate(roteiro, 1):
    with st.expander(f"**Trecho {i} - Voz: {item['voz']}**"):
        st.write(item['texto'])
        if st.button(f"▶️ Preview", key=f"preview_{i}"):
            with st.spinner(f"Gerando preview do trecho {i}..."):
                preview_audio = generate_audio(item['texto'], item['voz'], api_key)
                if preview_audio:
                    st.audio(preview_audio, format="audio/wav")

# Botão de geração
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎙️ **GERAR COMERCIAL COMPLETO**", type="primary", use_container_width=True):
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        audio_segments = []
        
        for i, item in enumerate(roteiro):
            status_text.text(f"🎤 Gerando trecho {i+1}/{len(roteiro)}: {item['voz']}...")
            progress_bar.progress((i / len(roteiro)) * 0.7)
            
            # Log para debug
            with st.expander(f"Debug - Trecho {i+1}"):
                st.write(f"Texto: {item['texto']}")
                st.write(f"Voz: {item['voz']}")
            
            audio = generate_audio(item['texto'], item['voz'], api_key)
            
            if audio:
                audio_segments.append(audio)
                st.success(f"✅ Trecho {i+1} gerado com sucesso! ({item['voz']})")
            else:
                st.error(f"❌ Falha no trecho {i+1}")
                break
            
            # Delay para evitar limite da API
            if i < len(roteiro) - 1:
                time.sleep(3)  # 3 segundos entre requisições
        
        if len(audio_segments) == len(roteiro):
            status_text.text("🔗 Combinando áudios...")
            progress_bar.progress(0.85)
            
            combined_audio = combine_audios(audio_segments)
            
            if combined_audio:
                progress_bar.progress(1.0)
                status_text.text("✅ Comercial pronto!")
                
                st.markdown("---")
                st.subheader("🎧 Comercial Completo")
                st.audio(combined_audio, format="audio/wav")
                
                # Botão de download
                st.download_button(
                    label="📥 Download do Comercial (.wav)",
                    data=combined_audio,
                    file_name="comercial_alfa_bureau.wav",
                    mime="audio/wav",
                    use_container_width=True
                )
                
                # Salvar trechos individuais também
                with st.expander("💾 Download dos Trechos Individuais"):
                    for i, (segment, item) in enumerate(zip(audio_segments, roteiro), 1):
                        st.download_button(
                            label=f"Trecho {i} - {item['voz']}",
                            data=segment,
                            file_name=f"trecho_{i}_{item['voz']}.wav",
                            mime="audio/wav",
                            key=f"download_{i}"
                        )
                
                st.success("🎉 Comercial gerado com sucesso!")
                st.balloons()
            else:
                st.error("❌ Erro ao combinar áudios")
        else:
            st.error("❌ Não foi possível gerar todos os trechos")
            if len(audio_segments) > 0:
                st.info(f"💡 {len(audio_segments)} trechos foram gerados com sucesso. Tente novamente para completar.")
                
                # Permitir download dos trechos que foram gerados
                with st.expander("💾 Download dos Trechos Gerados"):
                    for i, segment in enumerate(audio_segments, 1):
                        st.download_button(
                            label=f"Trecho {i}",
                            data=segment,
                            file_name=f"trecho_{i}_parcial.wav",
                            mime="audio/wav",
                            key=f"partial_download_{i}"
                        )

# Rodapé
st.markdown("---")
st.info("""
💡 **Dicas Importantes:**
- Use o teste de voz individual primeiro para verificar se a API está funcionando
- Teste cada trecho individualmente antes de gerar o comercial completo
- O processo completo leva aproximadamente 50 segundos
- Sistema com retry automático para maior confiabilidade
""")

# Informações adicionais
with st.expander("ℹ️ Informações Técnicas e Solução de Problemas"):
    st.markdown("""
    **✅ Correções implementadas:**
    - Removido instruções de estilo que causavam geração de música
    - API recebe apenas o texto puro para narração
    - Adicionado silêncio de 500ms entre trechos
    - Normalização de volume no áudio final
    - Preview individual de cada trecho
    - Download de trechos individuais
    
    **🔍 Diagnóstico de Problemas:**
    
    **Se ouvir apenas música:**
    - A API está interpretando incorretamente o prompt
    - Use o teste de voz individual para verificar
    
    **Possíveis erros:**
    - **Erro 429:** Limite de API excedido - aguarde 1 hora
    - **Erro 403:** Verifique se a API Key tem permissão para TTS
    - **Erro 500:** Servidor Google instável - aguarde 10 minutos
    - **Timeout:** Conexão lenta - tente novamente
    
    **Vozes disponíveis no Gemini TTS:**
    - Puck: Voz masculina jovem e energética
    - Kore: Voz feminina profissional
    """)

# Debug da configuração
with st.expander("🐛 Debug - Configuração Atual"):
    st.write("**Configuração da API:**")
    st.code(f"API Key: {'✅ Configurada' if api_key else '❌ Não configurada'}")
    st.code(f"Modelo: gemini-2.5-flash-preview-tts")
    st.code(f"Sample Rate: 24000 Hz")
    st.code(f"Canais: Mono")
    st.code(f"Bit Depth: 16 bits")