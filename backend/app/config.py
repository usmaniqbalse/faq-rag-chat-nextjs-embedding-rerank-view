from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    API_KEY: str = "change-me"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    CHROMA_PATH: str = "./demo-rag-chroma"
    EMBED_MODEL: str = "nomic-embed-text:latest"
    CHAT_MODEL: str = "llama3.2:3b"
    MAX_UPLOAD_MB: int = 20

     # NEW: logging
    LOG_LEVEL: str = "INFO"      # DEBUG, INFO, WARNING, ERROR
    LOG_JSON: bool = False       # True -> JSON logs

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

settings = Settings()
