# config/settings.py
"""
Configuraes centralizadas do Painel RH Modular.
Carrega variveis de ambiente do arquivo .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Carrega variveis do arquivo .env
load_dotenv()

class AppConfig:
    """Configuraes da aplicao"""
    
    # Informaes bsicas
    APP_NAME = os.getenv("APP_NAME", "Painel RH Modular")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    
    # API Keys (CRTICO) - Tenta Streamlit Secrets primeiro, depois .env
    GEMINI_API_KEY = None
    try:
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
    except (AttributeError, FileNotFoundError, KeyError):
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # URLs da API Gemini (MODELOS ATUALIZADOS - VERSO ESTVEL 2026)
    # AQUI ESTAVA O ERRO: Removemos o "-exp" para usar a verso oficial
    GEMINI_FLASH_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    GEMINI_PRO_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Configuraes da API
    API_TIMEOUT = 60
    API_MAX_RETRIES = 3
    
    # Diretrios
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
    REPORTS_DIR = BASE_DIR / os.getenv("REPORTS_DIR", "reports")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / os.getenv("LOG_FILE", "app.log")
    
    # Configuraes adicionais
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "pt-BR")
    
    # Benchmarks (para anlises)
    BENCHMARK_ABSENTISMO = {
        'Indstria': 4.5,
        'Comrcio': 3.8,
        'Servios': 3.2,
        'Sade': 5.5,
        'Educao': 4.0,
        'TI': 2.5,
        'Outros': 3.5
    }
    
    # Benchmark de Turnover
    BENCHMARK_TURNOVER = {
        'Indstria': 3.5,
        'Comrcio': 5.0,
        'Servios': 4.0,
        'Sade': 3.0,
        'Educao': 2.5,
        'TI': 4.5,
        'Outros': 4.0
    }
    
    @classmethod
    def validate(cls):
        """Valida se configuraes obrigatrias esto presentes"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append(" GEMINI_API_KEY no configurada no arquivo .env ou Streamlit Secrets")
        
        if errors:
            error_msg = "\n".join(errors)
            raise ValueError(f"\n\n ERRO DE CONFIGURAO:\n\n{error_msg}\n\n"
                           f" SOLUO:\n"
                           f"1. Verifique se GEMINI_API_KEY est em .streamlit/secrets.toml\n"
                           f"2. Ou adicione no arquivo .env\n"
                           f"3. Reinicie a aplicao\n")
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Cria diretrios necessrios se no existirem"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)
        
        # Subdiretrios de dados
        (cls.DATA_DIR / "analyses").mkdir(exist_ok=True)
        (cls.DATA_DIR / "knowledge_base").mkdir(exist_ok=True)
        (cls.DATA_DIR / "conversations").mkdir(exist_ok=True)

# Inicializao automtica ao importar
try:
    AppConfig.validate()
    AppConfig.create_directories()
except ValueError as e:
    print(e)


