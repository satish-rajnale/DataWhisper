"""SQL query validator using pglast AST parsing."""
from typing import Set, Optional, Any
from pglast import parse_sql

from app.config import settings
from app.services.schema_loader import schema_loader


class ValidationError(Exception):
    """Raised when SQL validation fails."""
    pass


class SQLValidator:
    """Validates SQL queries for safety and correctness."""
    
    def __init__(self):
        self._allowed_tables: Optional[Set[str]] = None
    
    def _get_allowed_tables(self) -> Set[str]:
        """Get set of allowed table names from schema."""
        if self._allowed_tables is None:
            schema = schema_loader.get_schema()
            self._allowed_tables = set(schema.keys())
        return self._allowed_tables
    
    def validate(self, sql: str) -> str:
        """
        Validate SQL query and return sanitized version.
        
        Args:
            sql: SQL query string to validate
            
        Returns:
            Validated SQL query (may be modified, e.g., LIMIT added)
            
        Raises:
            ValidationError: If query is invalid or unsafe
        """
        try:
            # Parse SQL to AST
            ast = parse_sql(sql)
        except Exception as e:
            raise ValidationError(f"Invalid SQL syntax: {str(e)}")
        
        allowed_tables = self._get_allowed_tables()
        
        # Validate each statement
        for stmt in ast:
            self._validate_statement(stmt, allowed_tables)
        
        # Ensure LIMIT is present and within bounds
        sql = self._ensure_limit(sql, ast)
        
        return sql
    
    def _validate_statement(self, stmt: Any, allowed_tables: Set[str]):
        """Validate a single SQL statement node."""
        if not hasattr(stmt, 'node_tag'):
            return
        
        stmt_type = stmt.node_tag
        
        # Only allow SELECT statements
        if stmt_type == "SelectStmt":
            self._validate_select(stmt, allowed_tables)
        elif stmt_type == "RawStmt":
            # Recursively validate the inner statement
            if hasattr(stmt, 'stmt'):
                inner_stmt = stmt.stmt
                self._validate_statement(inner_stmt, allowed_tables)
        else:
            raise ValidationError(
                f"Only SELECT queries are allowed. Found: {stmt_type}"
            )
    
    def _validate_select(self, select_stmt: Any, allowed_tables: Set[str]):
        """Validate a SELECT statement."""
        # Check for CTEs (WITH clauses)
        if hasattr(select_stmt, 'withClause') and select_stmt.withClause:
            if hasattr(select_stmt.withClause, 'ctes'):
                for cte in select_stmt.withClause.ctes:
                    if hasattr(cte, 'ctequery'):
                        self._validate_select(cte.ctequery, allowed_tables)
        
        # Extract table references
        self._extract_and_validate_tables(select_stmt, allowed_tables)
    
    def _extract_and_validate_tables(
        self,
        node: Any,
        allowed_tables: Set[str]
    ):
        """Recursively extract and validate table references."""
        if node is None:
            return
        
        if not hasattr(node, 'node_tag'):
            return
        
        node_tag = node.node_tag
        
        # Check for RangeVar (table references)
        if node_tag == "RangeVar":
            table_name = None
            if hasattr(node, 'schemaname') and node.schemaname:
                if hasattr(node, 'relname'):
                    table_name = f"{node.schemaname}.{node.relname}"
            elif hasattr(node, 'relname'):
                table_name = node.relname
            
            if table_name and table_name not in allowed_tables:
                raise ValidationError(
                    f"Table '{table_name}' is not in the allowed schema. "
                    f"Allowed tables: {sorted(allowed_tables)}"
                )
        
        # Recursively check child nodes
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            try:
                attr_value = getattr(node, attr_name)
                if hasattr(attr_value, 'node_tag'):
                    self._extract_and_validate_tables(attr_value, allowed_tables)
                elif isinstance(attr_value, list):
                    for item in attr_value:
                        if hasattr(item, 'node_tag'):
                            self._extract_and_validate_tables(item, allowed_tables)
            except (AttributeError, TypeError):
                pass
    
    def _ensure_limit(self, sql: str, ast: list) -> str:
        """
        Ensure LIMIT clause exists and is within bounds.
        If missing, adds LIMIT. If present, validates and adjusts if needed.
        """
        max_limit = settings.max_query_limit
        
        # Check if LIMIT exists in any SELECT statement
        has_limit = False
        limit_value = None
        
        def check_limit(node: Any):
            nonlocal has_limit, limit_value
            if hasattr(node, 'node_tag'):
                if node.node_tag == "SelectStmt":
                    if hasattr(node, 'limitCount') and node.limitCount:
                        has_limit = True
                        # Extract limit value
                        if hasattr(node.limitCount, 'val'):
                            try:
                                limit_value = int(node.limitCount.val)
                            except (ValueError, AttributeError):
                                pass
                # Recursively check
                for attr_name in dir(node):
                    if not attr_name.startswith('_'):
                        try:
                            attr_value = getattr(node, attr_name)
                            if hasattr(attr_value, 'node_tag'):
                                check_limit(attr_value)
                            elif isinstance(attr_value, list):
                                for item in attr_value:
                                    if hasattr(item, 'node_tag'):
                                        check_limit(item)
                        except (AttributeError, TypeError):
                            pass
        
        for stmt in ast:
            check_limit(stmt)
        
        # If no LIMIT, add one
        if not has_limit:
            # Simple approach: append LIMIT if not present
            sql_upper = sql.upper().strip()
            if "LIMIT" not in sql_upper:
                # Find the end of the query (before any semicolon)
                sql = sql.rstrip().rstrip(';')
                sql = f"{sql} LIMIT {max_limit}"
        
        # If LIMIT exists but exceeds max, we need to modify it
        # This is complex with AST, so we'll do a simple string replacement
        # for common cases
        if has_limit and limit_value and limit_value > max_limit:
            import re
            # Replace LIMIT values that exceed max
            pattern = r'\bLIMIT\s+(\d+)\b'
            def replace_limit(match):
                val = int(match.group(1))
                return f"LIMIT {min(val, max_limit)}"
            sql = re.sub(pattern, replace_limit, sql, flags=re.IGNORECASE)
        
        return sql


# Global validator instance
sql_validator = SQLValidator()

