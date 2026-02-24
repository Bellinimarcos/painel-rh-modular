# logic/absenteeism_processor.py
# Responsabilidade: Processar e analisar dados de absentismo, incluindo o Fator de Bradford.

import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, date
from typing import Dict, List, Tuple
import logging

from models.analysis import AnalysisResult, ValidationResult
from models.enums import AnalysisType, RiskLevel, DataQuality
from config.settings import AppConfig

logger = logging.getLogger(__name__)



# BENCHMARK DE ABSENTISMO
BENCHMARK_ABSENTISMO = {
    'Indústria': 4.5,
    'Comércio': 3.8,
    'Serviços': 3.2,
    'Saúde': 5.5,
    'Educação': 4.0,
    'TI': 2.5,
    'Outros': 3.5
}

class AbsenteeismProcessor:
    """
    Processa dados de absentismo e calcula mÃ©tricas chave:
    - Taxa de absentismo
    - Fator de Bradford
    - AnÃ¡lise por colaborador
    """
    
    def __init__(self):
        self.config = AppConfig()
    
    def validate(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> ValidationResult:
        """
        Valida os dados de entrada antes do processamento.
        
        Args:
            df: DataFrame com os dados de ausÃªncias
            column_mapping: Mapeamento das colunas do arquivo
        
        Returns:
            ValidationResult com status da validaÃ§Ã£o
        """
        errors = []
        warnings = []
        suggestions = []
        
        # Verifica se as colunas mapeadas existem no DataFrame
        required_fields = ['id_colaborador', 'data_inicio', 'data_fim']
        missing_fields = []
        
        for field in required_fields:
            if field not in column_mapping.values():
                missing_fields.append(field)
        
        if missing_fields:
            errors.append(f"Campos obrigatÃ³rios nÃ£o mapeados: {', '.join(missing_fields)}")
        
        # Verifica se o DataFrame nÃ£o estÃ¡ vazio
        if df.empty:
            errors.append("O arquivo estÃ¡ vazio ou nÃ£o contÃ©m dados vÃ¡lidos")
        
        # Verifica percentual de dados nulos
        if not df.empty:
            null_percentage = (df.isnull().sum().sum() / df.size) * 100
            if null_percentage > 30:
                warnings.append(f"Alto percentual de dados ausentes: {null_percentage:.1f}%")
            elif null_percentage > 15:
                suggestions.append(f"Percentual moderado de dados ausentes: {null_percentage:.1f}%")
        
        # Calcula score de qualidade
        quality_score = 100
        if errors:
            quality_score = 0
        else:
            if df.empty:
                quality_score = 0
            else:
                null_pct = (df.isnull().sum().sum() / df.size) * 100
                quality_score = max(0, 100 - null_pct)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            quality_score=quality_score
        )
    
    def _parse_dates_robust(self, df: pd.DataFrame, date_column: str) -> pd.Series:
        """
        Converte uma coluna para datas de forma robusta, tentando mÃºltiplos formatos.
        
        Args:
            df: DataFrame contendo a coluna
            date_column: Nome da coluna a converter
        
        Returns:
            Series com as datas convertidas
        """
        try:
            # Tenta conversÃ£o padrÃ£o do pandas (suporta mÃºltiplos formatos)
            dates = pd.to_datetime(df[date_column], dayfirst=True, errors='coerce')
            
            # Converte para date (remove timezone se existir)
            if dates.dt.tz is not None:
                dates = dates.dt.tz_localize(None)
            
            dates = dates.dt.date
            
            # Log de datas invÃ¡lidas
            invalid_count = dates.isna().sum()
            if invalid_count > 0:
                logger.warning(f"Coluna '{date_column}': {invalid_count} datas invÃ¡lidas encontradas")
            
            return dates
            
        except Exception as e:
            logger.error(f"Erro ao converter coluna '{date_column}': {e}")
            return pd.Series([None] * len(df))
    
    def _calculate_business_days(self, start_date: date, end_date: date) -> int:
        """
        Calcula o nÃºmero de dias Ãºteis entre duas datas.
        
        Args:
            start_date: Data de inÃ­cio
            end_date: Data de fim
        
        Returns:
            NÃºmero de dias Ãºteis (excluindo fins de semana)
        """
        try:
            if pd.isna(start_date) or pd.isna(end_date):
                return 0
            
            if end_date < start_date:
                return 0
            
            # Converte para numpy datetime64 para usar busday_count
            start_np = np.datetime64(start_date)
            end_np = np.datetime64(end_date)
            
            # Calcula dias Ãºteis (inclusive o Ãºltimo dia)
            business_days = np.busday_count(start_np, end_np + np.timedelta64(1, 'D'))
            
            return max(0, int(business_days))
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias Ãºteis entre {start_date} e {end_date}: {e}")
            return 1  # Fallback: considera pelo menos 1 dia
    
    def _calculate_bradford_factor(self, absences_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula o Fator de Bradford para cada colaborador.
        FÃ³rmula: B = SÂ² Ã— D
        Onde S = nÃºmero de perÃ­odos de ausÃªncia, D = total de dias ausentes
        
        Args:
            absences_df: DataFrame com ausÃªncias jÃ¡ processadas
        
        Returns:
            DataFrame com o Fator de Bradford por colaborador
        """
        if absences_df.empty:
            return pd.DataFrame(columns=['id_colaborador', 'S', 'D', 'fator_bradford'])
        
        bradford_df = absences_df.groupby('id_colaborador').agg(
            S=('data_inicio', 'count'),  # NÃºmero de perÃ­odos
            D=('dias_ausencia', 'sum')   # Total de dias
        ).reset_index()
        
        # Calcula o fator: SÂ² Ã— D
        bradford_df['fator_bradford'] = (bradford_df['S'] ** 2) * bradford_df['D']
        
        return bradford_df
    
    def process(
        self,
        df: pd.DataFrame,
        name: str,
        period_start: date,
        period_end: date,
        total_employees: int,
        setor: str,
        column_mapping: Dict[str, str]
    ) -> AnalysisResult:
        """
        Processa os dados de absentismo e calcula todas as mÃ©tricas.
        
        Args:
            df: DataFrame com os dados brutos
            name: Nome da anÃ¡lise
            period_start: Data de inÃ­cio do perÃ­odo
            period_end: Data de fim do perÃ­odo
            total_employees: Total de colaboradores na organizaÃ§Ã£o
            setor: Setor da empresa (para benchmark)
            column_mapping: Mapeamento das colunas
        
        Returns:
            AnalysisResult com os resultados da anÃ¡lise
        """
        # Valida os dados
        validation = self.validate(df, column_mapping)
        if not validation.is_valid:
            raise ValueError(f"Dados invÃ¡lidos: {'; '.join(validation.errors)}")
        
        # Renomeia as colunas de acordo com o mapeamento
        df_processed = df.rename(columns=column_mapping).copy()
        
        # Converte datas de forma robusta
        df_processed['data_inicio'] = self._parse_dates_robust(df_processed, 'data_inicio')
        df_processed['data_fim'] = self._parse_dates_robust(df_processed, 'data_fim')
        
        # Remove linhas com datas invÃ¡lidas
        initial_rows = len(df_processed)
        df_processed.dropna(subset=['data_inicio', 'data_fim'], inplace=True)
        removed_rows = initial_rows - len(df_processed)
        
        if removed_rows > 0:
            logger.warning(f"{removed_rows} linhas removidas por datas invÃ¡lidas")
        
        # Remove registros onde data_fim < data_inicio
        invalid_ranges = df_processed['data_fim'] < df_processed['data_inicio']
        if invalid_ranges.any():
            logger.warning(f"{invalid_ranges.sum()} registros com intervalo de datas invÃ¡lido removidos")
            df_processed = df_processed[~invalid_ranges]
        
        # Filtra apenas ausÃªncias que se sobrepÃµem ao perÃ­odo analisado
        df_filtered = df_processed[
            (df_processed['data_inicio'] <= period_end) & 
            (df_processed['data_fim'] >= period_start)
        ].copy()
        
        # Calcula dias de ausÃªncia para cada registro
        dias_ausencia = []
        for _, row in df_filtered.iterrows():
            # Ajusta as datas para o perÃ­odo analisado
            start = max(row['data_inicio'], period_start)
            end = min(row['data_fim'], period_end)
            
            days = self._calculate_business_days(start, end)
            dias_ausencia.append(days)
        
        df_filtered['dias_ausencia'] = dias_ausencia
        
        # Remove ausÃªncias com 0 dias (podem ser fins de semana ou feriados)
        df_filtered = df_filtered[df_filtered['dias_ausencia'] > 0]
        
        # Calcula mÃ©tricas principais
        total_dias_uteis = self._calculate_business_days(period_start, period_end)
        total_dias_possiveis = total_employees * total_dias_uteis
        total_dias_ausencia = int(df_filtered['dias_ausencia'].sum()) if not df_filtered.empty else 0
        
        # Taxa de absentismo (percentual)
        taxa_absentismo = (total_dias_ausencia / total_dias_possiveis * 100) if total_dias_possiveis > 0 else 0
        
        # Calcula Fator de Bradford
        bradford_df = self._calculate_bradford_factor(df_filtered)
        fator_bradford_medio = bradford_df['fator_bradford'].mean() if not bradford_df.empty else 0
        
        # Determina nÃ­vel de risco
        benchmark = BENCHMARK_ABSENTISMO.get(setor, 3.5)
        risk_level = self._calculate_risk_level(taxa_absentismo, benchmark)
        
        # Gera insights automÃ¡ticos
        insights = self._generate_insights(
            taxa_absentismo, 
            benchmark, 
            fator_bradford_medio,
            bradford_df
        )
        
        return AnalysisResult(
            id=hashlib.md5(f"absent_{datetime.now()}".encode()).hexdigest()[:8],
            type=AnalysisType.ABSENTEEISM,
            name=name,
            timestamp=datetime.now(),
            data={
                'taxa_absentismo': round(taxa_absentismo, 2),
                'fator_bradford_medio': round(fator_bradford_medio, 2),
                'df_bradford': bradford_df,
                'total_dias_ausencia': total_dias_ausencia
            },
            metadata={
                'periodo_inicio': period_start,
                'periodo_fim': period_end,
                'total_colaboradores': total_employees,
                'benchmark_setor': benchmark,
                'setor': setor,
                'registros_processados': len(df_filtered),
                'total_dias_uteis_periodo': total_dias_uteis,
                'registros_removidos': removed_rows
            },
            quality=validation.quality,
            risk_level=risk_level,
            insights=insights
        )
    
    def _calculate_risk_level(self, taxa: float, benchmark: float) -> RiskLevel:
        """Determina o nÃ­vel de risco baseado na comparaÃ§Ã£o com o benchmark."""
        if taxa > benchmark * 1.5:
            return RiskLevel.HIGH
        elif taxa > benchmark * 1.2:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _generate_insights(
        self,
        taxa: float,
        benchmark: float,
        bradford_medio: float,
        bradford_df: pd.DataFrame
    ) -> List[str]:
        """Gera insights automÃ¡ticos baseados nos dados."""
        insights = []
        
        # Insight sobre a taxa
        diff = taxa - benchmark
        if diff > 0:
            insights.append(
                f"Taxa de absentismo {diff:.1f}% acima do benchmark do setor ({benchmark:.1f}%)"
            )
        else:
            insights.append(
                f"Taxa de absentismo dentro dos parÃ¢metros esperados para o setor"
            )
        
        # Insight sobre Bradford
        if bradford_medio > 100:
            insights.append(
                f"Fator Bradford mÃ©dio elevado ({bradford_medio:.1f}) indica padrÃ£o preocupante de ausÃªncias frequentes"
            )
        elif bradford_medio > 50:
            insights.append(
                f"Fator Bradford mÃ©dio moderado ({bradford_medio:.1f}) - monitorar colaboradores com scores altos"
            )
        
        # Insight sobre colaboradores crÃ­ticos
        if not bradford_df.empty:
            critical_employees = bradford_df[bradford_df['fator_bradford'] > 200]
            if len(critical_employees) > 0:
                insights.append(
                    f"{len(critical_employees)} colaborador(es) com Fator Bradford crÃ­tico (>200) - requer atenÃ§Ã£o imediata"
                )
        
        return insights
