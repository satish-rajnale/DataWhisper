"""FastAPI dependency injection."""
from fastapi import Depends
from typing import Annotated

from app.database import db
from app.services.schema_loader import schema_loader
from app.services.llm_service import llm_service
from app.services.sql_validator import sql_validator
from app.services.query_executor import query_executor


def get_database():
    """Dependency for database connection."""
    return db


def get_schema_loader():
    """Dependency for schema loader."""
    return schema_loader


def get_llm_service():
    """Dependency for LLM service."""
    return llm_service


def get_sql_validator():
    """Dependency for SQL validator."""
    return sql_validator


def get_query_executor():
    """Dependency for query executor."""
    return query_executor

