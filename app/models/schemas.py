from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
import re

class FinancialDataCreate(BaseModel):
    competencia: str
    tipo: str
    categoria: str
    valor: float
    descricao: Optional[str] = None
    
    @field_validator('competencia')
    @classmethod
    def validate_competencia(cls, v):
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('Competência deve estar no formato YYYY-MM')
        return v
    
    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        if v.lower() not in ['receita', 'custo']:
            raise ValueError('Tipo deve ser "receita" ou "custo"')
        return v.lower()
    
    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser positivo')
        return v

class FinancialDataResponse(BaseModel):
    id: int
    competencia: str
    tipo: str
    categoria: str
    valor: float
    descricao: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    valor_previsto: float
    intervalo_confianca: List[float]
    acuracia_historica: float
    modelo_usado: str

class PredictionsResponse(BaseModel):
    receita_30d: PredictionResponse
    custos_30d: PredictionResponse
    receita_60d: PredictionResponse
    custos_60d: PredictionResponse
    data_base: str
    total_registros: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_status: str
    total_records: int
    last_update: Optional[str]

class ModelStatsResponse(BaseModel):
    modelo_ativo: str
    total_previsoes: int
    acuracia_media: float
    ultima_atualizacao: datetime
    registros_treinamento: int
