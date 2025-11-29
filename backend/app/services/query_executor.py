"""Safe SQL query execution with parameter binding."""
from typing import List, Dict, Any, Optional
import asyncpg
import json

from app.database import db
from app.config import settings


class QueryExecutionError(Exception):
    """Raised when query execution fails."""
    pass


class QueryExecutor:
    """Executes validated SQL queries safely."""
    
    async def execute(
        self,
        sql: str,
        params: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query with parameter binding.
        
        Args:
            sql: Validated SQL query string
            params: Optional list of parameter values
            
        Returns:
            List of dictionaries representing rows
            
        Raises:
            QueryExecutionError: If execution fails
        """
        if params is None:
            params = []
        
        try:
            async with db.acquire() as conn:
                # Execute query with parameters
                rows = await conn.fetch(sql, *params)
                
                # Convert asyncpg.Record objects to dictionaries
                result = []
                for row in rows:
                    row_dict = {}
                    for key, value in row.items():
                        # Convert types that aren't JSON serializable
                        if value is None:
                            row_dict[key] = None
                        elif isinstance(value, (bytes, bytearray)):
                            row_dict[key] = value.hex()
                        elif hasattr(value, 'isoformat'):  # datetime, date, time
                            row_dict[key] = value.isoformat()
                        elif hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool)):
                            # Convert UUID and other types to string
                            try:
                                row_dict[key] = str(value)
                            except Exception:
                                row_dict[key] = value
                        else:
                            row_dict[key] = value
                    result.append(row_dict)
                
                return result
                
        except asyncpg.PostgresError as e:
            raise QueryExecutionError(f"Database error: {str(e)}")
        except Exception as e:
            raise QueryExecutionError(f"Query execution failed: {str(e)}")


# Global query executor instance
query_executor = QueryExecutor()

