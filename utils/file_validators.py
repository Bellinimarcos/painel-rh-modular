# utils/file_validators.py
# Responsabilidade: Fornecer funções robustas para leitura e validação de arquivos.

import pandas as pd
import io
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class FileValidator:
    """
    Classe utilitária para leitura e validação robusta de arquivos CSV e Excel.
    Tenta múltiplos encodings e separadores automaticamente.
    """
    
    # Encodings comuns para tentar, em ordem de prioridade
    ENCODINGS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    # Separadores comuns para CSV
    SEPARATORS = [',', ';', '\t', '|']
    
    @staticmethod
    def read_file_robust(uploaded_file) -> Tuple[Optional[pd.DataFrame], List[str], List[str]]:
        """
        Lê um arquivo CSV ou Excel de forma robusta, tentando múltiplos formatos.
        
        Args:
            uploaded_file: Objeto de arquivo do Streamlit (UploadedFile)
        
        Returns:
            Tupla contendo:
            - DataFrame se bem-sucedido, None caso contrário
            - Lista de avisos
            - Lista de erros
        """
        warnings = []
        errors = []
        
        if uploaded_file is None:
            errors.append("Nenhum arquivo foi carregado")
            return None, warnings, errors
        
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Tenta ler Excel primeiro se for a extensão
        if file_extension in ['xlsx', 'xls']:
            try:
                uploaded_file.seek(0)
                df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else None)
                logger.info(f"Arquivo Excel '{uploaded_file.name}' lido com sucesso")
                return df, warnings, errors
            except Exception as e:
                logger.error(f"Erro ao ler Excel: {e}")
                errors.append(f"Erro ao ler arquivo Excel: {str(e)}")
                # Tenta como CSV se falhar
        
        # Tenta ler como CSV
        uploaded_file.seek(0)
        file_content = uploaded_file.getvalue()
        
        # Tenta diferentes combinações de encoding e separador
        for encoding in FileValidator.ENCODINGS:
            for separator in FileValidator.SEPARATORS:
                try:
                    uploaded_file.seek(0)
                    text_content = file_content.decode(encoding)
                    df = pd.read_csv(
                        io.StringIO(text_content),
                        sep=separator,
                        low_memory=False,
                        encoding=encoding
                    )
                    
                    # Verifica se a leitura foi bem-sucedida (mais de 1 coluna)
                    if df.shape[1] > 1:
                        if encoding != 'utf-8':
                            warnings.append(f"Arquivo lido com encoding '{encoding}'")
                        if separator != ',':
                            warnings.append(f"Separador '{separator}' detectado")
                        
                        logger.info(f"CSV lido com encoding='{encoding}', sep='{separator}'")
                        return df, warnings, errors
                
                except (UnicodeDecodeError, pd.errors.ParserError) as e:
                    continue  # Tenta próxima combinação
                except Exception as e:
                    logger.error(f"Erro inesperado ao ler CSV: {e}")
                    continue
        
        # Se chegou aqui, nenhuma combinação funcionou
        errors.append(
            "Não foi possível ler o arquivo. Verifique se é um CSV ou Excel válido."
        )
        return None, warnings, errors
    
    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame,
        min_rows: int = 1,
        min_columns: int = 1,
        required_columns: Optional[List[str]] = None
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Valida um DataFrame após a leitura.
        
        Args:
            df: DataFrame a validar
            min_rows: Número mínimo de linhas esperado
            min_columns: Número mínimo de colunas esperado
            required_columns: Lista de colunas obrigatórias
        
        Returns:
            Tupla contendo:
            - bool: True se válido
            - Lista de avisos
            - Lista de erros
        """
        warnings = []
        errors = []
        
        if df is None:
            errors.append("DataFrame é None")
            return False, warnings, errors
        
        # Verifica se está vazio
        if df.empty:
            errors.append("O arquivo está vazio")
            return False, warnings, errors
        
        # Verifica número de linhas
        if len(df) < min_rows:
            errors.append(f"Arquivo contém apenas {len(df)} linha(s). Mínimo esperado: {min_rows}")
        
        # Verifica número de colunas
        if df.shape[1] < min_columns:
            errors.append(f"Arquivo contém apenas {df.shape[1]} coluna(s). Mínimo esperado: {min_columns}")
        
        # Verifica colunas obrigatórias
        if required_columns:
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
        
        # Avisos sobre qualidade dos dados
        null_percentage = (df.isnull().sum().sum() / df.size) * 100 if df.size > 0 else 0
        if null_percentage > 20:
            warnings.append(f"Alto percentual de dados ausentes: {null_percentage:.1f}%")
        elif null_percentage > 10:
            warnings.append(f"Percentual moderado de dados ausentes: {null_percentage:.1f}%")
        
        # Verifica duplicatas
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            warnings.append(f"{duplicate_rows} linha(s) duplicada(s) encontrada(s)")
        
        is_valid = len(errors) == 0
        return is_valid, warnings, errors
    
    @staticmethod
    def preview_dataframe(df: pd.DataFrame, n_rows: int = 5) -> str:
        """
        Cria um preview formatado do DataFrame para mostrar ao utilizador.
        
        Args:
            df: DataFrame para preview
            n_rows: Número de linhas a mostrar
        
        Returns:
            String formatada com informações do DataFrame
        """
        if df is None or df.empty:
            return "DataFrame vazio"
        
        preview = []
        preview.append(f"📊 **Dimensões**: {len(df)} linhas × {df.shape[1]} colunas")
        preview.append(f"📋 **Colunas**: {', '.join(df.columns[:10].tolist())}")
        if df.shape[1] > 10:
            preview.append(f"   ... e mais {df.shape[1] - 10} colunas")
        
        # Tipos de dados
        dtypes_summary = df.dtypes.value_counts().to_dict()
        preview.append(f"🔢 **Tipos de dados**: {dtypes_summary}")
        
        # Dados ausentes
        null_count = df.isnull().sum().sum()
        if null_count > 0:
            preview.append(f"⚠️ **Dados ausentes**: {null_count} células vazias")
        
        return "\n".join(preview)


class ColumnMapper:
    """
    Classe auxiliar para facilitar o mapeamento de colunas de arquivos
    para os nomes esperados pela aplicação.
    """
    
    @staticmethod
    def auto_detect_column(
        df: pd.DataFrame,
        target_name: str,
        keywords: List[str]
    ) -> Optional[str]:
        """
        Tenta detectar automaticamente uma coluna baseado em palavras-chave.
        
        Args:
            df: DataFrame com as colunas
            target_name: Nome do campo que estamos procurando (para logs)
            keywords: Lista de palavras-chave a procurar (case-insensitive)
        
        Returns:
            Nome da coluna encontrada ou None
        """
        columns_lower = {col.lower(): col for col in df.columns}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for col_lower, col_original in columns_lower.items():
                if keyword_lower in col_lower:
                    logger.info(f"Auto-detectado '{target_name}': {col_original}")
                    return col_original
        
        return None
    
    @staticmethod
    def suggest_mappings(df: pd.DataFrame) -> dict:
        """
        Sugere mapeamentos automáticos para campos comuns.
        
        Args:
            df: DataFrame com os dados
        
        Returns:
            Dicionário com sugestões de mapeamento
        """
        suggestions = {}
        
        # Mapeamentos comuns para absentismo
        mappings_config = {
            'id_colaborador': ['matricula', 'matrícula', 'id', 'colaborador', 'funcionario', 'funcionário', 'empregado'],
            'data_inicio': ['inicio', 'início', 'saida', 'saída', 'start', 'begin'],
            'data_fim': ['fim', 'fim', 'retorno', 'end', 'finish', 'ultimo', 'último'],
            'motivo': ['motivo', 'razao', 'razão', 'causa', 'tipo', 'categoria']
        }
        
        for target, keywords in mappings_config.items():
            detected = ColumnMapper.auto_detect_column(df, target, keywords)
            if detected:
                suggestions[target] = detected
        
        return suggestions