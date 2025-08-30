from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, Index, text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Configuração do PostgreSQL/Supabase
DATABASE_URL = os.getenv("DATABASE_URL")

# PostgreSQL/Supabase
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FinancialData(Base):
    __tablename__ = "financial_data"
    
    id = Column(Integer, primary_key=True, index=True)
    competencia = Column(String(7), index=True, nullable=False)  # YYYY-MM
    tipo = Column(String(10), nullable=False)  # receita | custo
    categoria = Column(String(100), nullable=False)
    valor = Column(Float, nullable=False)
    descricao = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices compostos para otimização
    __table_args__ = (
        Index('idx_competencia_tipo', 'competencia', 'tipo'),
        Index('idx_tipo_categoria', 'tipo', 'categoria'),
    )

class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    competencia_base = Column(String(7), nullable=False)  # Mês base da previsão
    tipo = Column(String(10), nullable=False)  # receita | custo
    periodo = Column(Integer, nullable=False)  # 30 ou 60 dias
    valor_previsto = Column(Float, nullable=False)
    intervalo_min = Column(Float, nullable=False)
    intervalo_max = Column(Float, nullable=False)
    modelo_usado = Column(String(50), nullable=False)
    
    # Novos campos de acurácia
    acuracia_absoluta = Column(Float)  # Ex: 0.35
    acuracia_relativa = Column(Float)  # Ex: 35% em relação ao valor real
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices para consultas otimizadas e constraint único
    __table_args__ = (
        Index('idx_competencia_tipo_periodo', 'competencia_base', 'tipo', 'periodo'),
        UniqueConstraint('competencia_base', 'tipo', 'periodo', name='uq_prediction_unique'),
    )

# Criar tabelas (com tratamento de erro para produção)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Aviso: Erro ao criar tabelas (podem já existir): {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para testar conexão
def test_database_connection():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Erro de conexão com o banco: {e}")
        return False
