# utils/gdrive_backup.py
# Responsabilidade: Backup automático para Google Drive

from datetime import datetime
from pathlib import Path
import json
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GDriveBackup:
    """Gerencia backups automáticos no Google Drive."""
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.folder_id = None
    
    def authenticate(self):
        """Autentica com Google Drive."""
        token_path = 'token.pickle'
        
        # Carrega credenciais salvas
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # Se não há credenciais válidas, faz login
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Requer arquivo credentials.json do Google Cloud Console
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Salva credenciais
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('drive', 'v3', credentials=self.creds)
        return True
    
    def create_backup_folder(self, folder_name="Backups_Painel_RH"):
        """Cria ou localiza pasta de backups no Drive."""
        if not self.service:
            self.authenticate()
        
        # Busca pasta existente
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            self.folder_id = folders[0]['id']
            return self.folder_id
        
        # Cria nova pasta
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        self.folder_id = folder.get('id')
        return self.folder_id
    
    def upload_file(self, file_path: str, drive_filename: str = None):
        """Faz upload de arquivo para Google Drive."""
        if not self.service:
            self.authenticate()
        
        if not self.folder_id:
            self.create_backup_folder()
        
        if not drive_filename:
            drive_filename = Path(file_path).name
        
        file_metadata = {
            'name': drive_filename,
            'parents': [self.folder_id]
        }
        
        media = MediaFileUpload(
            file_path,
            resumable=True
        )
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    
    def auto_backup(self, backup_manager):
        """Executa backup automático completo."""
        from services.storage import get_persistent_storage
        
        storage = get_persistent_storage()
        analyses = storage.get_analyses()
        
        if not analyses:
            return None, "Nenhuma análise para backup"
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Cria Excel
            excel_path = backup_manager.export_to_excel(
                analyses, 
                f"backup_auto_{timestamp}.xlsx"
            )
            
            # Upload para Drive
            link = self.upload_file(excel_path)
            
            # Remove arquivo local
            Path(excel_path).unlink()
            
            return link, f"Backup automático realizado: {timestamp}"
        
        except Exception as e:
            return None, f"Erro no backup: {str(e)}"


def render_gdrive_backup_config():
    """Interface para configurar backup automático no Google Drive."""
    st.subheader("️ Backup Automático - Google Drive")
    
    st.info("""
    **Como configurar:**
    1. Habilite a API do Google Drive no Google Cloud Console
    2. Baixe `credentials.json` e coloque na raiz do projeto
    3. Execute a autenticação abaixo (só uma vez)
    4. Configure frequência dos backups
    """)
    
    with st.expander(" Instruções Detalhadas"):
        st.markdown("""
        ### Passo 1: Google Cloud Console
        1. Acesse [Google Cloud Console](https://console.cloud.google.com)
        2. Crie novo projeto: "Painel RH Backups"
        3. Ative a **Google Drive API**
        4. Vá em **Credenciais**  **Criar Credenciais**  **ID do cliente OAuth**
        5. Tipo: "Aplicativo para computador"
        6. Baixe o arquivo JSON
        7. Renomeie para `credentials.json`
        8. Coloque na pasta raiz do projeto
        
        ### Passo 2: Autenticação (primeira vez)
        Execute localmente uma vez para autorizar o acesso.
        
        ### Passo 3: Deploy
        No Streamlit Cloud, adicione nos Secrets:
        ```toml
        [gdrive]
        enabled = true
        ```
        """)
    
    gdrive = GDriveBackup()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Autenticar Google Drive", width='stretch'):
            try:
                gdrive.authenticate()
                st.success(" Autenticação bem-sucedida!")
            except FileNotFoundError:
                st.error(" Arquivo credentials.json não encontrado")
            except Exception as e:
                st.error(f" Erro: {e}")
    
    with col2:
        if st.button("️ Criar Pasta Backups", width='stretch'):
            try:
                folder_id = gdrive.create_backup_folder()
                st.success(f" Pasta criada: {folder_id}")
            except Exception as e:
                st.error(f" Erro: {e}")
    
    st.divider()
    
    # Backup manual
    if st.button("️ Fazer Backup Agora", type="primary", width='stretch'):
        from utils.backup_manager import BackupManager
        
        backup_mgr = BackupManager()
        
        with st.spinner("Fazendo backup..."):
            link, msg = gdrive.auto_backup(backup_mgr)
            
            if link:
                st.success(msg)
                st.markdown(f"[ Ver no Google Drive]({link})")
            else:
                st.error(msg)
    
    st.divider()
    
    # Configuração de backup automático
    st.subheader("⏰ Backup Automático")
    
    enable_auto = st.checkbox("Ativar backup automático diário")
    
    if enable_auto:
        backup_time = st.time_input("Horário do backup", value=datetime.now().replace(hour=2, minute=0))
        
        st.info(f"Backup será executado diariamente às {backup_time.strftime('%H:%M')}")
        
        # Salva configuração
        if st.button(" Salvar Configuração"):
            config = {
                'enabled': True,
                'time': backup_time.strftime('%H:%M')
            }
            
            config_path = Path('config/backup_config.json')
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            st.success(" Configuração salva!")


# Script para executar backup agendado (rodar em servidor/cron)
def scheduled_backup():
    """Executa backup agendado (usar com cron ou schedule)."""
    import schedule
    import time
    
    def job():
        from utils.backup_manager import BackupManager
        
        gdrive = GDriveBackup()
        backup_mgr = BackupManager()
        
        link, msg = gdrive.auto_backup(backup_mgr)
        print(f"{datetime.now()}: {msg}")
        
        if link:
            print(f"Link: {link}")
    
    # Lê configuração
    try:
        with open('config/backup_config.json', 'r') as f:
            config = json.load(f)
        
        if config.get('enabled'):
            backup_time = config.get('time', '02:00')
            schedule.every().day.at(backup_time).do(job)
            
            print(f"Backup agendado para {backup_time}")
            
            while True:
                schedule.run_pending()
                time.sleep(60)
    except FileNotFoundError:
        print("Configuração de backup não encontrada")


if __name__ == "__main__":
    # Executar como script standalone para backups agendados
    scheduled_backup()


