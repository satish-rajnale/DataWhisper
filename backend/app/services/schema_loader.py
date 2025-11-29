"""Postgres schema metadata loader and cache."""
from typing import Dict, List, Optional
import asyncpg

from app.database import db


class SchemaLoader:
    """Loads and caches Postgres schema metadata."""
    
    def __init__(self):
        self._schema_cache: Optional[Dict[str, Dict]] = None
    
    async def load_schema(self) -> Dict[str, Dict]:
        """
        Load schema metadata from Postgres system catalogs.
        
        Returns:
            Dict mapping table names to their metadata:
            {
                "table_name": {
                    "columns": [
                        {"name": "col1", "type": "integer", "nullable": False},
                        ...
                    ],
                    "comments": {
                        "table": "Table comment",
                        "columns": {"col1": "Column comment", ...}
                    },
                    "foreign_keys": [
                        {"column": "col1", "references_table": "other_table", "references_column": "id"},
                        ...
                    ]
                }
            }
        """
        async with db.acquire() as conn:
            # Get all user tables (exclude system schemas)
            tables_query = """
                SELECT 
                    schemaname,
                    tablename
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schemaname, tablename
            """
            
            tables = await conn.fetch(tables_query)
            schema: Dict[str, Dict] = {}
            
            for table in tables:
                schema_name = table['schemaname']
                table_name = table['tablename']
                full_table_name = f"{schema_name}.{table_name}" if schema_name != 'public' else table_name
                
                # Get columns
                columns_query = """
                    SELECT 
                        a.attname AS column_name,
                        pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                        a.attnotnull AS not_null,
                        a.attnum AS column_position
                    FROM pg_catalog.pg_attribute a
                    JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                    JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                    WHERE n.nspname = $1
                      AND c.relname = $2
                      AND a.attnum > 0
                      AND NOT a.attisdropped
                    ORDER BY a.attnum
                """
                
                columns_rows = await conn.fetch(columns_query, schema_name, table_name)
                columns = [
                    {
                        "name": row['column_name'],
                        "type": row['data_type'],
                        "nullable": not row['not_null']
                    }
                    for row in columns_rows
                ]
                
                # Get table comment
                table_comment_query = """
                    SELECT obj_description(c.oid, 'pg_class') AS comment
                    FROM pg_catalog.pg_class c
                    JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                    WHERE n.nspname = $1 AND c.relname = $2
                """
                table_comment_row = await conn.fetchrow(table_comment_query, schema_name, table_name)
                table_comment = table_comment_row['comment'] if table_comment_row and table_comment_row['comment'] else None
                
                # Get column comments
                column_comments_query = """
                    SELECT 
                        a.attname AS column_name,
                        col_description(a.attrelid, a.attnum) AS comment
                    FROM pg_catalog.pg_attribute a
                    JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                    JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                    WHERE n.nspname = $1
                      AND c.relname = $2
                      AND a.attnum > 0
                      AND NOT a.attisdropped
                """
                column_comments_rows = await conn.fetch(column_comments_query, schema_name, table_name)
                column_comments = {
                    row['column_name']: row['comment']
                    for row in column_comments_rows
                    if row['comment']
                }
                
                # Get foreign keys
                fk_query = """
                    SELECT
                        kcu.column_name AS column_name,
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_schema = $1
                      AND tc.table_name = $2
                """
                fk_rows = await conn.fetch(fk_query, schema_name, table_name)
                foreign_keys = [
                    {
                        "column": row['column_name'],
                        "references_table": (
                            f"{row['foreign_table_schema']}.{row['foreign_table_name']}"
                            if row['foreign_table_schema'] != 'public'
                            else row['foreign_table_name']
                        ),
                        "references_column": row['foreign_column_name']
                    }
                    for row in fk_rows
                ]
                
                schema[full_table_name] = {
                    "columns": columns,
                    "comments": {
                        "table": table_comment,
                        "columns": column_comments
                    },
                    "foreign_keys": foreign_keys
                }
            
            self._schema_cache = schema
            return schema
    
    def get_schema(self) -> Dict[str, Dict]:
        """Get cached schema. Raises RuntimeError if not loaded."""
        if self._schema_cache is None:
            raise RuntimeError("Schema not loaded. Call load_schema() first.")
        return self._schema_cache
    
    def get_schema_context(self, max_tables: Optional[int] = None) -> str:
        """
        Format schema for LLM prompt context.
        
        Args:
            max_tables: Optional limit on number of tables to include
            
        Returns:
            Formatted string describing the schema
        """
        schema = self.get_schema()
        tables = list(schema.items())
        
        if max_tables:
            tables = tables[:max_tables]
        
        lines = []
        for table_name, table_info in tables:
            lines.append(f"\n## Table: {table_name}")
            
            if table_info["comments"]["table"]:
                lines.append(f"Description: {table_info['comments']['table']}")
            
            lines.append("Columns:")
            for col in table_info["columns"]:
                nullable = "nullable" if col["nullable"] else "NOT NULL"
                comment = table_info["comments"]["columns"].get(col["name"], "")
                comment_str = f" -- {comment}" if comment else ""
                lines.append(f"  - {col['name']}: {col['type']} ({nullable}){comment_str}")
            
            if table_info["foreign_keys"]:
                lines.append("Foreign Keys:")
                for fk in table_info["foreign_keys"]:
                    lines.append(
                        f"  - {fk['column']} -> {fk['references_table']}.{fk['references_column']}"
                    )
        
        return "\n".join(lines)


# Global schema loader instance
schema_loader = SchemaLoader()

