from sqlalchemy.orm import Session
from app.models.database import FinancialData, PredictionHistory
from app.models.schemas import FinancialDataCreate
from app.services.predictor import FinancialPredictor
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataService:
    
    def __init__(self):
        self.predictor = FinancialPredictor()
    
    def save_financial_data(self, db: Session, data_list: List[FinancialDataCreate]) -> int:
        """Salva dados financeiros no banco"""
        saved_count = 0
        
        for data in data_list:
            # Verificar se já existe
            existing = db.query(FinancialData).filter(
                FinancialData.competencia == data.competencia,
                FinancialData.tipo == data.tipo,
                FinancialData.categoria == data.categoria,
                FinancialData.descricao == data.descricao
            ).first()
            
            if not existing:
                db_item = FinancialData(**data.dict())
                db.add(db_item)
                saved_count += 1
        
        db.commit()
        return saved_count
    
    def get_all_financial_data(self, db: Session) -> List[Dict]:
        """Recupera todos os dados financeiros"""
        data = db.query(FinancialData).all()
        return [
            {
                'competencia': item.competencia,
                'tipo': item.tipo,
                'categoria': item.categoria,
                'valor': item.valor,
                'descricao': item.descricao
            }
            for item in data
        ]
    
    def train_models(self, db: Session) -> Dict[str, float]:
        """Treina os modelos com todos os dados disponíveis"""
        financial_data = self.get_all_financial_data(db)
        return self.predictor.train(financial_data)
    
    def generate_predictions(self, db: Session, base_competencia: str) -> Dict:
        """Gera previsões para 30 e 60 dias"""
        # Treinar modelo se não estiver treinado
        if not self.predictor.is_trained:
            self.train_models(db)
        
        predictions = self.predictor.predict_future(base_competencia, [30, 60])
        
        # Salvar histórico de previsões
        for key, pred in predictions.items():
            tipo = key.split('_')[0]
            periodo = int(key.split('_')[1].replace('d', ''))
            
            prediction_record = PredictionHistory(
                competencia_base=base_competencia,
                tipo=tipo,
                periodo=periodo,
                valor_previsto=pred['valor_previsto'],
                intervalo_min=pred['intervalo_confianca'][0],
                intervalo_max=pred['intervalo_confianca'][1],
                modelo_usado=pred['modelo_usado'],
                acuracia=pred['acuracia_historica']
            )
            db.add(prediction_record)
        
        db.commit()
        
        return {
            'receita_30d': predictions['receita_30d'],
            'custos_30d': predictions['custo_30d'],
            'receita_60d': predictions['receita_60d'],
            'custos_60d': predictions['custo_60d'],
            'data_base': base_competencia,
            'total_registros': len(self.get_all_financial_data(db))
        }
    
    def get_database_stats(self, db: Session) -> Dict:
        """Estatísticas do banco de dados"""
        total_records = db.query(FinancialData).count()
        last_record = db.query(FinancialData).order_by(FinancialData.created_at.desc()).first()
        
        return {
            'total_records': total_records,
            'last_update': last_record.created_at.isoformat() if last_record else None,
            'model_trained': self.predictor.is_trained,
            'last_training': self.predictor.last_training_date.isoformat() if self.predictor.last_training_date else None
        }
