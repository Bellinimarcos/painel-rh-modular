# services/api_client.py
# Responsabilidade: Centralizar toda a comunicação com a API externa (Gemini).

import streamlit as st
import requests
import time
import logging
from typing import Optional

# Importa a classe de configuração que definimos
from config.settings import AppConfig

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

class APIClient:
    """Cliente para interagir com a API da Gemini."""
    def __init__(self):
        self.config = AppConfig()

    def call_gemini(self, prompt: str) -> Optional[str]:
        """
        Faz uma chamada para a API Gemini com tratamento de erros melhorado para
        exibir mensagens de erro específicas da API.
        """
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("Chave da API Gemini não encontrada nos secrets.")
            return None

        if not prompt or not prompt.strip():
            logger.error("Tentativa de chamada à API com um prompt vazio.")
            return None

        url = f"{self.config.GEMINI_FLASH_URL}?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        headers = {'Content-Type': 'application/json'}

        for attempt in range(self.config.API_MAX_RETRIES):
            try:
                response = requests.post(
                    url, json=payload, headers=headers, timeout=self.config.API_TIMEOUT
                )
                response.raise_for_status()
                result = response.json()
                
                # Verifica se a resposta foi bloqueada por segurança, mesmo com status 200
                if not result.get('candidates'):
                    finish_reason = result.get('promptFeedback', {}).get('blockReason')
                    if finish_reason:
                        error_msg = f"A API bloqueou a resposta por segurança (Motivo: {finish_reason})."
                        logger.warning(error_msg)
                        st.error(error_msg)
                        return None
                
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                return text_response

            except requests.exceptions.RequestException as e:
                error_details = ""
                # --- LÓGICA DE DIAGNÓSTICO MELHORADA ---
                # Tenta extrair a mensagem de erro específica da resposta da API
                if e.response is not None:
                    try:
                        error_data = e.response.json()
                        error_details = error_data.get("error", {}).get("message", e.response.text)
                        logger.error(f"API Request falhou com status {e.response.status_code}: {error_details}")
                    except ValueError:
                        error_details = e.response.text
                        logger.error(f"API Request falhou com status {e.response.status_code} e resposta não-JSON.")
                else:
                    logger.warning(f"Erro de comunicação na tentativa {attempt + 1}: {e}")
                    error_details = "Verifique a sua conexão de internet."

                # Mostra o erro detalhado na interface
                if attempt == self.config.API_MAX_RETRIES - 1:
                    st.error(f"Erro da API: {error_details}")
                    st.info("Verifique se a sua chave de API é válida e se a 'Generative Language API' está ativada no seu projeto Google Cloud.")
                
                time.sleep(2 ** attempt)

        logger.error("Todas as tentativas de comunicação com a API falharam.")
        st.error("Não foi possível comunicar com o Assistente IA após várias tentativas.")
        return None

