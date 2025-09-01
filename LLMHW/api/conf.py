
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str


    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHROMA_DB_DIR: str = "vector_db"
    CHAT_MODEL: str = "gpt-4o-mini"
    LANGUAGE_FILTER_ENABLED: bool = True
    TTS_ENABLED: bool = True
    STT_ENABLED: bool = False


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
