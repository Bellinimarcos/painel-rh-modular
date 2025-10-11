# services/storage.py
# Responsabilidade: Gerir o armazenamento e recuperação de dados persistentes (análises, etc.).

import os
import pickle
import logging
import streamlit as st
from typing import Optional, Any, Dict, List
from models.analysis import AnalysisResult # Importa o modelo que criámos
from services.storage_backup import auto_backup_on_save, StorageBackup

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

# --- Constantes de Armazenamento ---
STORAGE_DIR = "data"
ANALYSES_FILE = os.path.join(STORAGE_DIR, "analyses.pkl")
PULSE_SURVEYS_FILE = os.path.join(STORAGE_DIR, "pulse_surveys.pkl")

class PersistentStorage:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PersistentStorage, cls).__new__(cls)
            os.makedirs(STORAGE_DIR, exist_ok=True)
            cls._instance._load_all()
        return cls._instance

    def _load_all(self):
        """Carrega todos os dados do armazenamento ao iniciar."""
        self.analyses = self._load_from_pickle(ANALYSES_FILE) or []
        self.pulse_surveys = self._load_from_pickle(PULSE_SURVEYS_FILE) or {}

    def _load_from_pickle(self, file_path: str) -> Optional[Any]:
        """Carrega dados de um ficheiro pickle com tratamento de erro robusto."""
        try:
            with open(file_path, 'rb') as f:
                logger.info(f"A carregar dados de {file_path}")
                return pickle.load(f)
        except FileNotFoundError:
            logger.warning(f"Ficheiro de armazenamento {file_path} não encontrado. A iniciar com dados vazios.")
            return None
        except (pickle.UnpicklingError, EOFError, AttributeError, ImportError) as e:
            logger.error(f"Erro ao ler o ficheiro pickle {file_path}: {e}. A ignorar dados.")
            return None

    def _save_to_pickle(self, data: Any, file_path: str):
        """Salva dados num ficheiro pickle."""
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
                logger.info(f"Dados salvos em {file_path}")
        except Exception as e:
            logger.error(f"Falha ao salvar dados em {file_path}: {e}")

    def get_analyses(self) -> List[AnalysisResult]:
        """Retorna a lista de análises salvas."""
        return self.analyses

    @auto_backup_on_save
    def save_analysis(self, analysis_result: AnalysisResult):
        """Salva ou atualiza uma análise na lista."""
        self.analyses = [a for a in self.analyses if a.id != analysis_result.id]
        self.analyses.append(analysis_result)
        self._save_to_pickle(self.analyses, ANALYSES_FILE)

    def clear_all(self):
        """Limpa todos os dados armazenados."""
        self.analyses = []
        self.pulse_surveys = {}
        for file_path in [ANALYSES_FILE, PULSE_SURVEYS_FILE]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Ficheiro de armazenamento {file_path} removido.")
                except OSError as e:
                    logger.error(f"Erro ao remover {file_path}: {e}")

# Usa o cache do Streamlit para garantir que temos apenas uma instância do storage.
@st.cache_resource
def get_persistent_storage() -> PersistentStorage:
    """Função de acesso global ao singleton de armazenamento."""
    return PersistentStorage()