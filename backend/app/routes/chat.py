"""Chat endpoint for natural language to SQL queries."""
from fastapi import APIRouter, HTTPException
import logging

from app.models import ChatRequest, ChatResponse
from app.services.llm_service import llm_service
from app.services.schema_loader import schema_loader
from app.services.sql_validator import sql_validator, ValidationError
from app.services.query_executor import query_executor, QueryExecutionError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process natural language query and return SQL results.
    
    Flow:
    1. Get schema context
    2. Generate SQL via LLM
    3. Validate SQL
    4. Execute query
    5. Summarize results
    6. Return response
    """
    try:
        # Get schema context
        schema_context = schema_loader.get_schema_context()
        
        # Generate SQL via LLM
        logger.info(f"Generating SQL for query: {request.query}")
        llm_result = await llm_service.generate_sql(
            user_query=request.query,
            schema_context=schema_context
        )
        
        sql = llm_result["sql"]
        params = llm_result.get("params", [])
        explanation = llm_result.get("explanation", "Generated SQL query")
        
        # Validate SQL
        logger.info(f"Validating SQL: {sql}")
        try:
            validated_sql = sql_validator.validate(sql)
        except ValidationError as e:
            logger.error(f"SQL validation failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Generated SQL is invalid or unsafe: {str(e)}"
            )
        
        # Execute query
        logger.info(f"Executing SQL with params: {params}")
        try:
            rows = await query_executor.execute(validated_sql, params)
        except QueryExecutionError as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Query execution failed: {str(e)}"
            )
        
        # Summarize results
        logger.info(f"Summarizing {len(rows)} rows")
        summary = await llm_service.summarize_results(
            user_query=request.query,
            rows=rows,
            sql=validated_sql
        )
        
        return ChatResponse(
            summary=summary,
            rows=rows,
            explanation=explanation,
            sql=validated_sql
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

