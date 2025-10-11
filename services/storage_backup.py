# services/storage_backup.py
"""
Sistema de backup automático para dados persistentes.
Cria backups regulares e permite restauração em caso de falha.
"""
import os
import shutil
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class StorageBackup:
    """Gerencia backups automáticos dos dados"""
    
    def __init__(self, storage_dir: str = "data", backup_dir: str = "backups"):
        self.storage_dir = Path(storage_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurações
        self.max_backups = 10  # Mantém últimos 10 backups
        self.backup_retention_days = 30  # Remove backups com mais de 30 dias
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Cria backup de todos os arquivos de dados.
        
        Args:
            backup_name: Nome customizado (usa timestamp se None)
        
        Returns:
            Caminho do backup criado
        """
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            # Cria diretório do backup
            backup_path.mkdir(exist_ok=True)
            
            # Copia todos os arquivos .pkl e .json
            files_backed_up = []
            
            if self.storage_dir.exists():
                for file in self.storage_dir.glob("*"):
                    if file.suffix in ['.pkl', '.json']:
                        dest = backup_path / file.name
                        shutil.copy2(file, dest)
                        files_backed_up.append(file.name)
            
            # Cria manifesto do backup
            manifest = {
                'timestamp': datetime.now().isoformat(),
                'files': files_backed_up,
                'backup_name': backup_name
            }
            
            with open(backup_path / 'manifest.json', 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Backup criado: {backup_name} ({len(files_backed_up)} arquivos)")
            
            # Remove backups antigos
            self._cleanup_old_backups()
            
            return str(backup_path)
        
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            raise
    
    def restore_backup(self, backup_name: str, confirm: bool = False) -> bool:
        """
        Restaura dados de um backup.
        
        Args:
            backup_name: Nome do backup a restaurar
            confirm: Deve ser True para confirmar restauração
        
        Returns:
            True se restaurado com sucesso
        """
        if not confirm:
            logger.warning("Restauração requer confirmação explícita (confirm=True)")
            return False
        
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup não encontrado: {backup_name}")
        
        try:
            # Cria backup de segurança antes de restaurar
            safety_backup = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.create_backup(safety_backup)
            logger.info(f"Backup de segurança criado: {safety_backup}")
            
            # Restaura arquivos
            files_restored = []
            for file in backup_path.glob("*"):
                if file.suffix in ['.pkl', '.json'] and file.name != 'manifest.json':
                    dest = self.storage_dir / file.name
                    shutil.copy2(file, dest)
                    files_restored.append(file.name)
            
            logger.info(f"Backup restaurado: {backup_name} ({len(files_restored)} arquivos)")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            raise
    
    def list_backups(self) -> List[Dict]:
        """
        Lista todos os backups disponíveis.
        
        Returns:
            Lista de dicionários com informações dos backups
        """
        backups = []
        
        for backup_dir in sorted(self.backup_dir.iterdir(), reverse=True):
            if backup_dir.is_dir():
                manifest_file = backup_dir / 'manifest.json'
                
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest = json.load(f)
                        
                        backups.append({
                            'name': backup_dir.name,
                            'timestamp': manifest.get('timestamp'),
                            'files': manifest.get('files', []),
                            'size_mb': self._get_dir_size(backup_dir) / (1024 * 1024)
                        })
                    except:
                        # Backup sem manifesto válido
                        backups.append({
                            'name': backup_dir.name,
                            'timestamp': 'unknown',
                            'files': [],
                            'size_mb': self._get_dir_size(backup_dir) / (1024 * 1024)
                        })
        
        return backups
    
    def delete_backup(self, backup_name: str) -> bool:
        """Remove um backup específico"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            return False
        
        try:
            shutil.rmtree(backup_path)
            logger.info(f"Backup removido: {backup_name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover backup: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Remove backups antigos baseado nas políticas"""
        backups = self.list_backups()
        
        # Remove backups excedentes (mantém apenas max_backups)
        if len(backups) > self.max_backups:
            for backup in backups[self.max_backups:]:
                self.delete_backup(backup['name'])
                logger.info(f"Backup antigo removido: {backup['name']}")
        
        # Remove backups muito antigos
        cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
        
        for backup in backups:
            try:
                if backup['timestamp'] != 'unknown':
                    backup_date = datetime.fromisoformat(backup['timestamp'])
                    if backup_date < cutoff_date:
                        self.delete_backup(backup['name'])
                        logger.info(f"Backup expirado removido: {backup['name']}")
            except:
                pass
    
    def _get_dir_size(self, path: Path) -> int:
        """Calcula tamanho total de um diretório em bytes"""
        total = 0
        for file in path.rglob('*'):
            if file.is_file():
                total += file.stat().st_size
        return total
    
    def create_scheduled_backup(self) -> str:
        """
        Cria backup com nome baseado em schedule (diário).
        Sobrescreve backup do mesmo dia se já existir.
        """
        today = datetime.now().strftime("%Y%m%d")
        backup_name = f"daily_{today}"
        
        # Remove backup do mesmo dia se existir
        backup_path = self.backup_dir / backup_name
        if backup_path.exists():
            shutil.rmtree(backup_path)
        
        return self.create_backup(backup_name)
    
    def export_backup_to_zip(self, backup_name: str, output_path: Optional[str] = None) -> str:
        """
        Exporta backup como arquivo ZIP.
        
        Args:
            backup_name: Nome do backup
            output_path: Caminho do ZIP (usa nome padrão se None)
        
        Returns:
            Caminho do arquivo ZIP criado
        """
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup não encontrado: {backup_name}")
        
        if output_path is None:
            output_path = self.backup_dir / f"{backup_name}.zip"
        
        try:
            shutil.make_archive(
                str(output_path).replace('.zip', ''),
                'zip',
                backup_path
            )
            logger.info(f"Backup exportado para: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Erro ao exportar backup: {e}")
            raise


# Função helper para integração fácil
def auto_backup_on_save(func):
    """
    Decorator que cria backup automático antes de salvar dados.
    
    Example:
        @auto_backup_on_save
        def save_analysis(self, analysis):
            # ... código de salvamento
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Cria backup antes de salvar
            backup_manager = StorageBackup()
            backup_manager.create_scheduled_backup()
        except Exception as e:
            logger.warning(f"Falha no backup automático: {e}")
        
        # Executa função original
        return func(*args, **kwargs)
    
    return wrapper