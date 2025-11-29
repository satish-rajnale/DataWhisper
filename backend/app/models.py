"""Pydantic models for request/response validation."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    summary: str
    rows: List[Dict[str, Any]]
    explanation: str
    sql: str

