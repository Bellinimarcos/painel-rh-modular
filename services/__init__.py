"""
Módulo de serviços (API, armazenamento, etc)
"""
from .api_client import APIClient
from .storage import PersistentStorage, get_persistent_storage

__all__ = [
    'APIClient',
    'PersistentStorage',
    'get_persistent_storage'
]