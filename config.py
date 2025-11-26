from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Perplexity API
    perplexity_api_key: Optional[str] = None
    perplexity_model: str = "llama-3.1-sonar-small-128k-online"

    # Gemini API
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    
    # Database
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_db_name: str = "agentx"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Vector Store
    chroma_persist_directory: str = "./data/chroma"
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    max_web_searches_per_query: int = 5
    
    # Document Processing
    chunk_size: int = 512
    chunk_overlap: int = 128
    top_k_results: int = 4
    similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
