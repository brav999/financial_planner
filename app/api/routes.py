from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import *
from app.services.csv_processor import CSVProcessor
from app.services.data_service import DataService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["financial"])
data_service = DataService()

@router.post("/historical-data", response_model=dict)
async def upload_historical_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload dos dados históricos iniciais"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um CSV")
    
    try:
        # Processar CSV
        content = await file.read()
        financial_data = CSVProcessor.process_csv(content)
        
        # Salvar no banco
        saved_count = data_service.save_financial_data(db, financial_data)
        
        # Treinar modelos
        accuracy_scores = data_service.train_models(db)
        
        return {
            "message": "Dados históricos carregados com sucesso",
            "registros_processados": len(financial_data),
            "registros_salvos": saved_count,
            "modelos_treinados": True,
            "acuracia": accuracy_scores
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar dados históricos: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/monthly-update", response_model=dict)
async def monthly_update(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Atualização mensal com novos dados"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um CSV")
    
    try:
        # Processar CSV
        content = await file.read()
        financial_data = CSVProcessor.process_csv(content)
        
        # Salvar no banco
        saved_count = data_service.save_financial_data(db, financial_data)
        
        # Re-treinar modelos
        accuracy_scores = data_service.train_models(db)
        
        # Obter competência mais recente para base das previsões
        latest_competencia = max([data.competencia for data in financial_data])
        
        # Gerar previsões
        predictions = data_service.generate_predictions(db, latest_competencia)
        
        return {
    "message": "Atualização mensal realizada com sucesso",
    "registros_processados": len(financial_data),
    "registros_salvos": saved_count,
    "modelos_atualizados": True,
    "acuracia_absoluta": {k: v.get("r2") for k, v in accuracy_scores.items()},
    "acuracia_relativa": {k: v.get("mape") for k, v in accuracy_scores.items()},
    "previsoes_geradas": True,
    "previsoes": predictions
    }
        
    except Exception as e:
        logger.error(f"Erro na atualização mensal: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/predictions", response_model=PredictionsResponse)
async def get_predictions(db: Session = Depends(get_db)):
    """Obter previsões atuais"""
    try:
        # Obter competência mais recente
        all_data = data_service.get_all_financial_data(db)
        if not all_data:
            raise HTTPException(status_code=400, detail="Não há dados disponíveis")
        
        latest_competencia = max([data['competencia'] for data in all_data])
        
        # Gerar previsões (o método já treina o modelo se necessário)
        predictions = data_service.generate_predictions(db, latest_competencia)
        
        return PredictionsResponse(**predictions)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter previsões: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Verificação de saúde do sistema"""
    try:
        stats = data_service.get_database_stats(db)
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            database_status="connected",
            total_records=stats['total_records'],
            last_update=stats['last_update']
        )
        
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return HealthResponse(
            status="error",
            timestamp=datetime.utcnow(),
            database_status="error",
            total_records=0,
            last_update=None
        )

@router.get("/model-stats", response_model=ModelStatsResponse)
async def get_model_stats(db: Session = Depends(get_db)):
    """Estatísticas dos modelos"""
    try:
        stats = data_service.get_database_stats(db)
        
        # Calcular acurácia média
        accuracy_scores = data_service.predictor.accuracy_scores
        avg_accuracy = sum(accuracy_scores.values()) / len(accuracy_scores) if accuracy_scores else 0.0
        
        # Contar previsões no histórico
        from app.models.database import PredictionHistory
        total_predictions = db.query(PredictionHistory).count()
        
        return ModelStatsResponse(
            modelo_ativo="linear_regression",
            total_previsoes=total_predictions,
            acuracia_media=avg_accuracy,
            ultima_atualizacao=data_service.predictor.last_training_date or datetime.utcnow(),
            registros_treinamento=stats['total_records']
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))