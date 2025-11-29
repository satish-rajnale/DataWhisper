"""Async Postgres database connection pool."""
import asyncpg
from typing import Optional
from contextlib import asynccontextmanager

from app.config import settings


class Database:
    """Database connection pool manager."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool."""
        self._pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=1,
            max_size=10,
            command_timeout=settings.statement_timeout + 5,
        )
    
    async def disconnect(self):
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    @property
    def pool(self) -> asyncpg.Pool:
        """Get connection pool."""
        if self._pool is None:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        return self._pool
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool."""
        async with self.pool.acquire() as connection:
            # Set statement timeout for this connection
            await connection.execute(
                f"SET statement_timeout = '{settings.statement_timeout}s'"
            )
            yield connection


# Global database instance
db = Database()

