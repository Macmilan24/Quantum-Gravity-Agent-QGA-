# src/llm.py
from typing import Literal, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr as LCSecretStr
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("LLM_ORCHESTRATOR")

class LLMOrchestrator:
    @staticmethod
    def get_model(
        role: Literal["architect", "researcher", "coder", "critic"] = "architect",
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = None
    ):
        target_provider = provider or settings.DEFAULT_PROVIDER
        
        # Default Logic
        if not model_name:
            if role == "coder":
                target_model = settings.MODEL_CODING
                default_temp = 0.1
            else:
                target_model = settings.MODEL_REASONING
                default_temp = 0.7
        else:
            target_model = model_name
            default_temp = 0.5

        final_temp = temperature if temperature is not None else default_temp

        logger.info(f"Loading Model: {target_provider} -> {target_model} (Temp: {final_temp})")

        if target_provider == "google":
            return ChatGoogleGenerativeAI(
                model=target_model,
                temperature=final_temp,
                # Extract string from SecretStr for Google
                google_api_key=settings.GOOGLE_API_KEY, 
                max_output_tokens=8192
            )

        elif target_provider == "openrouter":
            if not settings.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY not found in environment.")
            
            return ChatOpenAI(
                base_url="https://openrouter.ai/api/v1",
                # LangChain OpenAI expects a SecretStr usually, or we pass string
                api_key=settings.OPENROUTER_API_KEY, 
                model=target_model,
                temperature=final_temp,
                max_tokens=8192
            )
        
        else:
            raise ValueError(f"Unknown provider: {target_provider}")

# This is the function your agents are looking for!
def get_llm(role: str = "architect"):
    return LLMOrchestrator.get_model(role=role)