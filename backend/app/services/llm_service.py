"""LLM service for SQL generation and result summarization."""
import json
from typing import Dict, List, Optional
from openai import AsyncOpenAI

from app.config import settings
from app.services.schema_loader import schema_loader


class LLMService:
    """OpenAI client wrapper for SQL generation and summarization."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_sql(
        self,
        user_query: str,
        schema_context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate SQL query from natural language question.
        
        Args:
            user_query: User's natural language question
            schema_context: Formatted schema context string
            
        Returns:
            Dict with keys: sql, params (JSON string), explanation
        """
        if schema_context is None:
            schema_context = schema_loader.get_schema_context()
        
        system_prompt = """You are a SQL expert. Given a database schema and a user's question, 
generate a safe, valid PostgreSQL SELECT query.

Rules:
1. Only generate SELECT queries (or WITH ... SELECT)
2. Use parameterized queries for any user input (use $1, $2, etc. for parameters)
3. Always include a LIMIT clause (max 100 rows)
4. Return your response as JSON with these keys:
   - "sql": The SQL query string
   - "params": JSON array of parameter values (empty array if no parameters)
   - "explanation": Brief explanation of what the query does

Example response:
{
  "sql": "SELECT name, email FROM users WHERE age > $1 LIMIT 50",
  "params": [18],
  "explanation": "Finds users older than 18, returning name and email"
}"""

        user_prompt = f"""Database Schema:
{schema_context}

User Question: {user_query}

Generate a SQL query to answer this question. Remember to use parameterized queries and include a LIMIT clause."""

        # Only use response_format for models that support it (gpt-4-turbo-preview, gpt-4-1106-preview, etc.)
        # Regular gpt-4 and gpt-3.5-turbo don't support json_object response_format
        supports_json_format = any(model_name in self.model.lower() for model_name in [
            'gpt-4-turbo', 'gpt-4-1106', 'gpt-4-0125', 'gpt-3.5-turbo-1106', 'o1'
        ])
        
        create_kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1
        }
        
        if supports_json_format:
            create_kwargs["response_format"] = {"type": "json_object"}
        
        response = await self.client.chat.completions.create(**create_kwargs)
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from LLM")
        
        # Try to parse JSON, handling cases where response might be wrapped in markdown code blocks
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove closing ```
        content = content.strip()
        
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {content}")
        
        # Validate required keys
        if "sql" not in result:
            raise ValueError("LLM response missing 'sql' key")
        if "params" not in result:
            result["params"] = []
        if "explanation" not in result:
            result["explanation"] = "Generated SQL query"
        
        return result
    
    async def summarize_results(
        self,
        user_query: str,
        rows: List[Dict],
        sql: str
    ) -> str:
        """
        Generate conversational summary of query results.
        
        Args:
            user_query: Original user question
            rows: Query result rows
            sql: SQL query that was executed
            
        Returns:
            Conversational summary string
        """
        # Limit rows for summarization to avoid token limits
        rows_for_summary = rows[:20] if len(rows) > 20 else rows
        
        system_prompt = """You are a helpful assistant that explains database query results 
in a clear, conversational way. Summarize the results naturally, highlighting key findings."""

        user_prompt = f"""User asked: {user_query}

Query executed: {sql}

Results ({len(rows)} row{'s' if len(rows) != 1 else ''}):
{json.dumps(rows_for_summary, indent=2)}

Provide a clear, conversational summary of these results. If there are more than 20 rows, 
mention that only a sample is shown."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        if not content:
            return f"Query returned {len(rows)} row(s)."
        
        return content


# Global LLM service instance
llm_service = LLMService()

