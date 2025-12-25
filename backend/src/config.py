# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from dotenv import load_dotenv

# Force load .env immediately to prevent "Arguments missing" errors
load_dotenv()

class Settings(BaseSettings):
    # We use SecretStr for keys (Best Practice)
    GOOGLE_API_KEY: SecretStr = Field(..., description="Required for Gemini")
    OPENROUTER_API_KEY: SecretStr = Field(None, description="Required for OpenRouter")
    
    # Configuration
    DEFAULT_PROVIDER: str = "openrouter" 
    MODEL_REASONING: str = "google/gemini-2.0-flash-thinking-exp:free" 
    MODEL_CODING: str = "google/gemini-2.0-flash-thinking-exp:free"
    
    # This tells Pydantic to read from .env if variables aren't in memory
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()