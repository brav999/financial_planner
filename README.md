# Sistema de Planejamento Financeiro

API para previsão de receitas e custos com machine learning, construída com FastAPI e PostgreSQL.

## 🚀 Funcionalidades

- **Upload de dados históricos** via CSV
- **Previsões automáticas** para 30 e 60 dias
- **Modelos de machine learning** (Regressão Linear)
- **Atualização mensal** de dados
- **API REST** completa com documentação automática
- **Banco de dados PostgreSQL** (Supabase)

## 📋 Pré-requisitos

- Python 3.13+
- PostgreSQL (ou Supabase)
- pip

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd financial_planner
```

### 2. Crie um ambiente virtual
```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:
```env
DATABASE_URL=postgresql://postgres:sua_senha@seu_host:5432/seu_banco
```

### 6. Execute a aplicação
```bash
python -m uvicorn app.main:app --reload
```

A API estará disponível em: http://localhost:8000

## 📖 Documentação da API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📊 Endpoints Principais

### Upload de Dados Históricos
```bash
POST /api/historical-data
```
Upload inicial dos dados financeiros em formato CSV.

### Atualização Mensal
```bash
POST /api/monthly-update
```
Atualização mensal com novos dados e re-treinamento dos modelos.

### Obter Previsões
```bash
GET /api/predictions
```
Retorna previsões para 30 e 60 dias.

### Health Check
```bash
GET /api/health
```
Verificação de saúde do sistema.

### Estatísticas do Modelo
```bash
GET /api/model-stats
```
Estatísticas dos modelos treinados.

## 📁 Formato do CSV

O arquivo CSV deve conter as seguintes colunas:

```csv
competencia,tipo,categoria,valor,descricao
2024-01,receita,vendas,50000.00,Vendas produtos
2024-01,custo,pessoal,15000.00,Salários
2024-01,custo,operacional,8000.00,Aluguel e utilities
```

**Campos:**
- `competencia`: Data no formato YYYY-MM
- `tipo`: "receita" ou "custo"
- `categoria`: Categoria do item
- `valor`: Valor numérico
- `descricao`: Descrição opcional

## 🏗️ Estrutura do Projeto

```
financial_planner/
├── app/
│   ├── api/
│   │   └── routes.py          # Endpoints da API
│   ├── models/
│   │   ├── database.py        # Modelos do banco
│   │   └── schemas.py         # Schemas Pydantic
│   ├── services/
│   │   ├── csv_processor.py   # Processamento de CSV
│   │   ├── data_service.py    # Lógica de negócio
│   │   └── predictor.py       # Modelos de ML
│   └── main.py               # Aplicação FastAPI
├── docs/
│   └── csv-example.csv       # Exemplo de CSV
├── requirements.txt          # Dependências Python
├── .gitignore               # Arquivos ignorados
└── README.md               # Este arquivo
```

## 🔧 Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados principal
- **Scikit-learn**: Machine learning
- **Pandas**: Manipulação de dados
- **NumPy**: Computação numérica
- **Pydantic**: Validação de dados

## Métricas de Avaliação do Modelo

### R² (R-quadrado / Coeficiente de Determinação)
- Mede o quanto a variação dos dados é explicada pelo modelo.
- Valor entre 0 e 1 (quanto mais próximo de 1, melhor).
- Exemplo: `R² = 0.8` → 80% da variação dos valores reais é explicada pelo modelo.

### MAPE (Mean Absolute Percentage Error / Erro Percentual Absoluto Médio)
- Mede o erro médio das previsões em percentual.
- Quanto menor, melhor a precisão.
- Exemplo: `MAPE = 5%` → em média, a previsão está 5% distante do valor real.

**Resumo rápido:**
- **R²** → qualidade do ajuste do modelo aos dados.  
- **MAPE** → precisão das previsões em termos percentuais.

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.
