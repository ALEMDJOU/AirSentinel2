from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List, Optional
import json

class Settings(BaseSettings):
    # Application
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8501", 
        "https://airsentinel.onrender.com",
        "https://airsentinel-cameroon.vercel.app",
        "https://airsentinel-chi.vercel.app",
        "https://project-uo7uo-7zvnt09fu-fofack-alemdjou-henri-joels-projects.vercel.app"
    ]
    
    # Dataset et ML
    DATASET_PATH: str = "data/processed/dataset_final.parquet"
    ML_MODELS_PATH: str = "models/"

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # Supabase Storage
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SMTP Notifications
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "alerts@airsentinel.cm"
    EMAILS_FROM_NAME: str = "AirSentinel Alerts"
    BREVO_API_KEY: Optional[str] = None
    FRONTEND_URL: str = "https://airsentinel-chi.vercel.app"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
