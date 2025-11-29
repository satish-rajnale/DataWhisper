# Backend - Natural Language SQL Chat API

FastAPI backend for converting natural language questions to SQL queries.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (see `.env.example`):
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4)
- `STATEMENT_TIMEOUT`: Query timeout in seconds (default: 30)
- `MAX_QUERY_LIMIT`: Maximum rows per query (default: 100)
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Architecture

- **config.py**: Configuration management with Pydantic Settings
- **database.py**: Async Postgres connection pool
- **schema_loader.py**: Loads and caches database schema on startup
- **llm_service.py**: OpenAI client for SQL generation and summarization
- **sql_validator.py**: AST-based SQL validation using pglast
- **query_executor.py**: Safe query execution with parameter binding
- **routes/chat.py**: Main chat endpoint

## Security

- SQL injection prevention via parameter binding
- AST validation ensures only SELECT queries
- Table whitelisting from schema
- Automatic LIMIT enforcement
- Statement timeout protection

