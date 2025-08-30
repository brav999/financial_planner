import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:xgA3jlEfCuTGziOe@db.zwfuttqzujnxaeliwxod.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("Conexão OK:", result.fetchone())
except Exception as e:
    print("Erro:", e)