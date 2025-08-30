import pandas as pd
from typing import List
from app.models.schemas import FinancialDataCreate
import io

class CSVProcessor:
    
    @staticmethod
    def validate_csv_structure(df: pd.DataFrame) -> List[str]:
        """Valida estrutura do CSV"""
        errors = []
        required_columns = ['competencia', 'tipo', 'categoria', 'valor']
        
        # Verificar colunas obrigatórias
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Colunas obrigatórias ausentes: {missing_columns}")
        
        # Verificar se há dados
        if df.empty:
            errors.append("CSV está vazio")
        
        return errors
    
    @staticmethod
    def process_csv(file_content: bytes) -> List[FinancialDataCreate]:
        """Processa CSV e retorna lista de dados validados"""
        try:
            # Ler CSV
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
            
            # Validar estrutura
            errors = CSVProcessor.validate_csv_structure(df)
            if errors:
                raise ValueError(f"Erros na estrutura do CSV: {', '.join(errors)}")
            
            # Limpar dados
            df = df.dropna(subset=['competencia', 'tipo', 'categoria', 'valor'])
            df['descricao'] = df.get('descricao', '').fillna('')
            
            # Converter para schema
            financial_data = []
            for _, row in df.iterrows():
                try:
                    data = FinancialDataCreate(
                        competencia=str(row['competencia']).strip(),
                        tipo=str(row['tipo']).strip(),
                        categoria=str(row['categoria']).strip(),
                        valor=float(row['valor']),
                        descricao=str(row.get('descricao', '')).strip()
                    )
                    financial_data.append(data)
                except Exception as e:
                    raise ValueError(f"Erro na linha {row.name + 2}: {str(e)}")
            
            return financial_data
            
        except Exception as e:
            raise ValueError(f"Erro ao processar CSV: {str(e)}")