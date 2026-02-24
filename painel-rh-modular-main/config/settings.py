# config/settings.py
"""
Configurações centralizadas do Painel RH Modular.
Carrega variáveis de ambiente do arquivo .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Carrega variáveis do arquivo .env
load_dotenv()

class AppConfig:
    """Configurações da aplicação"""
    
    # Informações básicas
    APP_NAME = os.getenv("APP_NAME", "Painel RH Modular")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    
    # API Keys (CRÍTICO) - Tenta Streamlit Secrets primeiro, depois .env
    GEMINI_API_KEY = None
    try:
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
    except (AttributeError, FileNotFoundError, KeyError):
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # URLs da API Gemini (MODELOS ATUALIZADOS - VERSÃO ESTÁVEL 2026)
    # AQUI ESTAVA O ERRO: Removemos o "-exp" para usar a versão oficial
    GEMINI_FLASH_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    GEMINI_PRO_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Configurações da API
    API_TIMEOUT = 60
    API_MAX_RETRIES = 3
    
    # Diretórios
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
    REPORTS_DIR = BASE_DIR / os.getenv("REPORTS_DIR", "reports")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / os.getenv("LOG_FILE", "app.log")
    
    # Configurações adicionais
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "pt-BR")
    
    # Benchmarks (para análises)
    BENCHMARK_ABSENTISMO = {
        'Indústria': 4.5,
        'Comércio': 3.8,
        'Serviços': 3.2,
        'Saúde': 5.5,
        'Educação': 4.0,
        'TI': 2.5,
        'Outros': 3.5
    }
    
    # Benchmark de Turnover
    BENCHMARK_TURNOVER = {
        'Indústria': 3.5,
        'Comércio': 5.0,
        'Serviços': 4.0,
        'Saúde': 3.0,
        'Educação': 2.5,
        'TI': 4.5,
        'Outros': 4.0
    }
    
    @classmethod
    def validate(cls):
        """Valida se configurações obrigatórias estão presentes"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("❌ GEMINI_API_KEY não configurada no arquivo .env ou Streamlit Secrets")
        
        if errors:
            error_msg = "\n".join(errors)
            raise ValueError(f"\n\n🚨 ERRO DE CONFIGURAÇÃO:\n\n{error_msg}\n\n"
                           f"📋 SOLUÇÃO:\n"
                           f"1. Verifique se GEMINI_API_KEY está em .streamlit/secrets.toml\n"
                           f"2. Ou adicione no arquivo .env\n"
                           f"3. Reinicie a aplicação\n")
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Cria diretórios necessários se não existirem"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)
        
        # Subdiretórios de dados
        (cls.DATA_DIR / "analyses").mkdir(exist_ok=True)
        (cls.DATA_DIR / "knowledge_base").mkdir(exist_ok=True)
        (cls.DATA_DIR / "conversations").mkdir(exist_ok=True)

# Inicialização automática ao importar
try:
    AppConfig.validate()
    AppConfig.create_directories()
except ValueError as e:
    print(e)