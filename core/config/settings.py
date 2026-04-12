# core/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from ..exceptions.agent_errors import SystemConfigError

class Settings(BaseSettings):
    # --- 1. Competition Server Config ---
    COMPETITION_API_KEY: str = Field(..., description="API Key for the competition system")
    BASE_URL: str = Field(..., description="URL of the DataProvider API")
    
    # --- 2. OpenAI Config ---
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key")
    GPT_MODEL_NAME: str = Field(default="gpt-4o-2024-08-06", description="Most standard 4o model version currently")
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # --- 3. Temperature Config for each Agent ---
    TEMP_ROUTER: float = Field(default=0.0, description="Router requires absolute logic")
    TEMP_EXTRACTOR: float = Field(default=0.1, description="Extractor needs to adhere strictly to text, less hallucination")
    TEMP_SYNTHESIZER: float = Field(default=0.3, description="Synthesizer needs some flexibility for smooth writing")

    # --- 4. System Config ---
    MAX_RETRIES: int = Field(default=3, description="Maximum retries when API fails")
    MAX_TOKENS_PER_CHUNK: int = Field(default=4000, description="Token limit for each data chunk")

    # Load from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

try:
    # Initialize a single instance (Singleton pattern) for project-wide use
    settings = Settings()
except Exception as e:
    raise SystemConfigError(f"Environment configuration error: Are you missing a variable in the .env file? Details: {e}")