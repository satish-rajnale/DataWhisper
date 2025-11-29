# Natural Language SQL Chat Application

A full-stack application that converts natural language questions into validated SQL queries, executes them safely, and returns conversational answers.

## Architecture

- **Frontend**: React + TypeScript with Vite
- **Backend**: FastAPI (Python 3.11+) with async Postgres support
- **SQL Validation**: pglast AST parsing for security
- **LLM**: OpenAI API for query generation and summarization

## Features

- Natural language to SQL conversion using LLM
- AST-based SQL validation (SELECT-only, whitelisted tables)
- Safe query execution with parameter binding
- Conversational result summarization
- Modern chat UI with message history
- Automatic LIMIT enforcement (max 100 rows)
- Statement timeout protection

## Prerequisites

- Python 3.11+
- Node.js 18+ (20+ recommended)
- PostgreSQL 14+
- OpenAI API key

## Setup

### Initialize Sample Database

Before running the application, you can populate the database with sample data:

```bash
# If using Docker Compose, connect to the postgres container
docker-compose exec postgres psql -U postgres -d validquery -f /path/to/init_sample_data.sql

# Or copy the file into the container and run it
docker-compose cp backend/init_sample_data.sql valid-query-postgres:/tmp/
docker-compose exec postgres psql -U postgres -d validquery -f /tmp/init_sample_data.sql

# Or if running locally with psql
psql -U postgres -d validquery -f backend/init_sample_data.sql
```

The sample data includes:
- **users** table: 10 sample users with names, emails, ages, cities
- **products** table: 10 sample products across different categories
- **orders** table: 12 sample orders with various statuses
- **order_items** table: Order line items
- **reviews** table: Product reviews with ratings

### Docker Compose (Recommended)

1. Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

2. **REQUIRED:** Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

   Get your API key from: https://platform.openai.com/api-keys

   All other variables have sensible defaults and can be left as-is for initial setup.

3. Build and start all services:
```bash
docker-compose up --build
```

   For detailed environment variable documentation, see [ENV_SETUP.md](ENV_SETUP.md)

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 3000

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

To stop all services:
```bash
docker-compose down
```

To stop and remove volumes (database data):
```bash
docker-compose down -v
```

### Manual Setup

### Backend

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` directory:
```bash
cp .env.example .env
```

5. Edit `.env` with your configuration:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
STATEMENT_TIMEOUT=30
MAX_QUERY_LIMIT=100
```

6. Start the backend server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Create a `.env` file to configure the API URL:
```env
VITE_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. Start both backend and frontend servers
2. Open the frontend in your browser
3. Ask questions about your database in natural language, for example:
   - "How many users do we have?"
   - "Show me the top 10 products by sales"
   - "What are the most recent orders?"

The system will:
1. Analyze your question
2. Generate a safe SQL query
3. Validate it against the schema
4. Execute it with proper limits
5. Return a conversational summary with the data

## API Endpoints

### POST `/chat`

Send a natural language query and receive SQL results.

**Request:**
```json
{
  "query": "How many users are there?"
}
```

**Response:**
```json
{
  "summary": "There are 1,234 users in the database.",
  "rows": [
    {"count": 1234}
  ],
  "explanation": "Counts all users in the users table",
  "sql": "SELECT COUNT(*) AS count FROM users LIMIT 100"
}
```

### GET `/health`

Health check endpoint.

## Security Features

- **SQL Injection Prevention**: All queries use parameter binding
- **AST Validation**: Only SELECT queries are allowed
- **Table Whitelisting**: Only tables in the schema can be queried
- **LIMIT Enforcement**: Automatic LIMIT clause (max 100 rows)
- **Statement Timeout**: Queries are automatically cancelled after timeout
- **No Mutations**: INSERT, UPDATE, DELETE, and DDL are blocked

## Project Structure

```
valid-query-generator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # DB connection pool
│   │   ├── models.py            # Pydantic models
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── routes/
│   │   │   └── chat.py          # Chat endpoint
│   │   └── services/
│   │       ├── llm_service.py   # OpenAI client
│   │       ├── schema_loader.py # Schema metadata
│   │       ├── sql_validator.py # AST validation
│   │       └── query_executor.py # Query execution
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API client
│   │   └── types.ts             # TypeScript types
│   └── package.json
└── README.md
```

## Development

### Backend Development

- The backend uses FastAPI with automatic API documentation at `/docs`
- Schema is loaded and cached on startup
- All services use dependency injection for testability

### Frontend Development

- Built with Vite for fast development
- TypeScript for type safety
- Modern React with hooks

## Troubleshooting

### Backend won't start

- Check that PostgreSQL is running and accessible
- Verify `.env` file has correct `DATABASE_URL`
- Ensure OpenAI API key is set correctly

### Schema not loading

- Verify database connection string is correct
- Check that tables exist in the database
- Review backend logs for error messages

### Frontend can't connect to backend

- Verify backend is running on port 8000
- Check CORS settings in `backend/app/config.py`
- Update `VITE_API_URL` in frontend `.env` if needed

## License

MIT

