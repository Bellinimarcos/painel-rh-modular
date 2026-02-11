# utils/backup_manager.py
# Responsabilidade: Sistema de backup e exportação de análises

import json
import pickle
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List
import pandas as pd
import streamlit as st
from models.analysis import AnalysisResult
class BackupManager:
    """Gerencia backup e exportação de análises."""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def export_to_json(self, analyses: List[AnalysisResult], filename: str = None) -> str:
        """Exporta análises para JSON (sem DataFrames)."""
        if not filename:
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.backup_dir / filename
        
        # Serializa análises
        data = []
        for analysis in analyses:
            # Remove DataFrames dos dados
            clean_data = {
                k: v for k, v in analysis.data.items() 
                if not isinstance(v, pd.DataFrame)
            }
            
            analysis_dict = {
                'id': analysis.id,
                'type': analysis.type.value,
                'name': analysis.name,
                'timestamp': analysis.timestamp.isoformat(),
                'data': clean_data,
                'metadata': analysis.metadata,
                'risk_level': analysis.risk_level.label if analysis.risk_level else None,
                'quality': analysis.quality.label if analysis.quality else None,
                'insights': analysis.insights,
                'recommendations': analysis.recommendations
            }
            data.append(analysis_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def export_to_excel(self, analyses: List[AnalysisResult], filename: str = None) -> str:
        """Exporta análises para Excel com múltiplas abas."""
        if not filename:
            filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = self.backup_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Aba 1: Resumo geral
            summary_data = []
            for analysis in analyses:
                summary_data.append({
                    'ID': analysis.id,
                    'Nome': analysis.name,
                    'Tipo': analysis.type.value,
                    'Data': analysis.timestamp.strftime('%d/%m/%Y %H:%M'),
                    'Risco': analysis.risk_level.label if analysis.risk_level else 'N/A',
                    'Qualidade': analysis.quality.label if analysis.quality else 'N/A'
                })
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Aba 2: Métricas detalhadas
            metrics_data = []
            for analysis in analyses:
                for key, value in analysis.data.items():
                    if isinstance(value, (int, float)):
                        metrics_data.append({
                            'Análise': analysis.name,
                            'Tipo': analysis.type.value,
                            'Métrica': key,
                            'Valor': value,
                            'Data': analysis.timestamp.strftime('%d/%m/%Y')
                        })
            
            if metrics_data:
                df_metrics = pd.DataFrame(metrics_data)
                df_metrics.to_excel(writer, sheet_name='Métricas', index=False)
            
            # Aba 3: Insights da IA
            ai_data = []
            for analysis in analyses:
                if analysis.metadata and 'ai_detailed_analysis' in analysis.metadata:
                    ai_data.append({
                        'Análise': analysis.name,
                        'Tipo': analysis.type.value,
                        'Data': analysis.timestamp.strftime('%d/%m/%Y'),
                        'Insights IA': analysis.metadata['ai_detailed_analysis']
                    })
            
            if ai_data:
                df_ai = pd.DataFrame(ai_data)
                df_ai.to_excel(writer, sheet_name='Insights IA', index=False)
        
        return str(filepath)
    
    def create_full_backup(self, data_dir: str = "data") -> str:
        """Cria backup completo incluindo arquivos pickle."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"backup_completo_{timestamp}.zip"
        zip_path = self.backup_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            data_path = Path(data_dir)
            
            # Adiciona todos os arquivos .pkl
            for pkl_file in data_path.glob('*.pkl'):
                zipf.write(pkl_file, arcname=f"data/{pkl_file.name}")
        
        return str(zip_path)
    
    def restore_from_backup(self, zip_path: str, target_dir: str = "data"):
        """Restaura backup de um arquivo zip."""
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(Path(target_dir).parent)
    
    def list_backups(self) -> List[dict]:
        """Lista todos os backups disponíveis."""
        backups = []
        
        for file in self.backup_dir.glob('*'):
            backups.append({
                'nome': file.name,
                'tamanho': f"{file.stat().st_size / 1024:.2f} KB",
                'data': datetime.fromtimestamp(file.stat().st_mtime).strftime('%d/%m/%Y %H:%M'),
                'caminho': str(file)
            })
        
        return sorted(backups, key=lambda x: x['data'], reverse=True)


def render_backup_interface():
    """Renderiza interface de backup na sidebar."""
    from services.storage import get_persistent_storage
    
    st.sidebar.divider()
    st.sidebar.subheader("💾 Backup & Export")
    
    storage = get_persistent_storage()
    backup_mgr = BackupManager()
    analyses = storage.get_analyses()
    
    if not analyses:
        st.sidebar.info("Nenhuma análise para exportar")
        return
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        # Export para Excel
        if st.button("📊 Excel", use_container_width=True, help="Exportar para Excel"):
            try:
                filepath = backup_mgr.export_to_excel(analyses)
                
                with open(filepath, 'rb') as f:
                    st.sidebar.download_button(
                        label="⬇️ Baixar Excel",
                        data=f.read(),
                        file_name=Path(filepath).name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                st.sidebar.success("Excel gerado!")
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")
    
    with col2:
        # Export para JSON
        if st.button("📄 JSON", use_container_width=True, help="Exportar para JSON"):
            try:
                filepath = backup_mgr.export_to_json(analyses)
                
                with open(filepath, 'rb') as f:
                    st.sidebar.download_button(
                        label="⬇️ Baixar JSON",
                        data=f.read(),
                        file_name=Path(filepath).name,
                        mime="application/json",
                        use_container_width=True
                    )
                st.sidebar.success("JSON gerado!")
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")
    
    # Backup completo (.zip)
    if st.sidebar.button("🗜️ Backup Completo (.zip)", use_container_width=True):
        try:
            zip_path = backup_mgr.create_full_backup()
            
            with open(zip_path, 'rb') as f:
                st.sidebar.download_button(
                    label="⬇️ Baixar Backup ZIP",
                    data=f.read(),
                    file_name=Path(zip_path).name,
                    mime="application/zip",
                    use_container_width=True
                )
            st.sidebar.success("Backup completo criado!")
        except Exception as e:
            st.sidebar.error(f"Erro: {e}")
    
    # Restaurar backup
    with st.sidebar.expander("🔄 Restaurar Backup"):
        uploaded_zip = st.file_uploader(
            "Upload arquivo .zip",
            type=['zip'],
            key="restore_backup"
        )
        
        if uploaded_zip and st.button("Restaurar", type="primary"):
            try:
                # Salva temporariamente
                temp_path = Path("backups") / uploaded_zip.name
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_zip.read())
                
                # Restaura
                backup_mgr.restore_from_backup(str(temp_path))
                st.success("Backup restaurado! Recarregue a página.")
                
                # Remove temporário
                temp_path.unlink()
            except Exception as e:
                st.error(f"Erro ao restaurar: {e}")