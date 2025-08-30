from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.models.database import Base, engine, test_database_connection
import logging
import os
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar diretórios necessários para uploads
os.makedirs("data", exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)

# Testar conexão com banco
if not test_database_connection():
    logger.error("Falha na conexão com o banco de dados")
else:
    logger.info("Conexão com banco de dados estabelecida com sucesso")

# Criar tabelas
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas/verificadas com sucesso")
except Exception as e:
    logger.error(f"Erro ao criar/verificar tabelas: {e}")

app = FastAPI(
    title="Sistema de Planejamento Financeiro",
    description="API para previsão de receitas e custos com Supabase",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Sistema de Planejamento Financeiro API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)