from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # System Info
    APP_NAME: str = "INSA Identity System"
    ENV: str = "development"
    DEBUG: bool = True
    
    # Database
    # DATABASE_URL: str = "postgresql://user:password@localhost:5432/insa_db"
    DATABASE_URL: str = "sqlite:///./insa_identity.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str = "CHANGE_THIS_TO_A_VALID_AES_KEY_32_BYTES_LONG"
    
    # Vector Search
    VECTOR_DIMENSION: int = 512
    INDEX_TYPE: str = "IVF4096,Flat"  # FAISS index type
    
    # Service Thresholds
    MATCH_THRESHOLD: float = 0.40  # Cosine similarity threshold
    LIVENESS_THRESHOLD: float = 0.90

    # OCR / Document Scanning
    GEMINI_API_KEY: Optional[str] = None  # Leave empty for offline regex mode
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
