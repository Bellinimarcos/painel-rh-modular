# config/settings.py
"""
ConfiguraÃ§Ãµes centralizadas do Painel RH Modular.
Carrega variÃ¡veis de ambiente do arquivo .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Carrega variÃ¡veis do arquivo .env
load_dotenv()


class AppConfig:
    """ConfiguraÃ§Ãµes da aplicaÃ§Ã£o"""
    
    # InformaÃ§Ãµes bÃ¡sicas
    APP_NAME = os.getenv("APP_NAME", "Painel RH Modular")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    
    # API Keys (CRÃTICO) - Tenta Streamlit Secrets primeiro, depois .env
    GEMINI_API_KEY = None
    try:
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
    except (AttributeError, FileNotFoundError, KeyError):
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # URLs da API Gemini (MODELOS ATUALIZADOS - SEM "-latest"!)
    GEMINI_FLASH_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    GEMINI_PRO_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    # ConfiguraÃ§Ãµes da API
    API_TIMEOUT = 60
    API_MAX_RETRIES = 3
    
    # DiretÃ³rios
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
    REPORTS_DIR = BASE_DIR / os.getenv("REPORTS_DIR", "reports")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / os.getenv("LOG_FILE", "app.log")
    
    # ConfiguraÃ§Ãµes adicionais
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "pt-BR")
    
    # Benchmarks (para anÃ¡lises)
    BENCHMARK_ABSENTISMO = {
        'IndÃºstria': 4.5,
        'ComÃ©rcio': 3.8,
        'ServiÃ§os': 3.2,
        'SaÃºde': 5.5,
        'EducaÃ§Ã£o': 4.0,
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
        """Valida se configuraÃ§Ãµes obrigatÃ³rias estÃ£o presentes"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("âŒ GEMINI_API_KEY nÃ£o configurada no arquivo .env ou Streamlit Secrets")
        
        if errors:
            error_msg = "\n".join(errors)
            raise ValueError(f"\n\nðŸš¨ ERRO DE CONFIGURAÃ‡ÃƒO:\n\n{error_msg}\n\n"
                           f"ðŸ“‹ SOLUÃ‡ÃƒO:\n"
                           f"1. Verifique se GEMINI_API_KEY estÃ¡ em .streamlit/secrets.toml\n"
                           f"2. Ou adicione no arquivo .env\n"
                           f"3. Reinicie a aplicaÃ§Ã£o\n")
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Cria diretÃ³rios necessÃ¡rios se nÃ£o existirem"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)
        
        # SubdiretÃ³rios de dados
        (cls.DATA_DIR / "analyses").mkdir(exist_ok=True)
        (cls.DATA_DIR / "knowledge_base").mkdir(exist_ok=True)
        (cls.DATA_DIR / "conversations").mkdir(exist_ok=True)


# InicializaÃ§Ã£o automÃ¡tica ao importar
try:
    AppConfig.validate()
    AppConfig.create_directories()
except ValueError as e:
    print(e)
    # NÃ£o levanta exceÃ§Ã£o aqui para permitir que Streamlit carregue
    # A validaÃ§Ã£o serÃ¡ feita novamente no main.py
