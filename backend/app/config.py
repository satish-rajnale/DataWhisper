"""Configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database configuration
    database_url: str
    
    # OpenAI configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # Query execution limits
    statement_timeout: int = 30  # seconds
    max_query_limit: int = 100
    
    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS origins - comma-separated string
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Global settings instance
settings = Settings()

