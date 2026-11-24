from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///./canario.db"
    dominio_isca: str = "seudominio.dev"
    webhook_segredo: str = ""
    llm_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:5173"]

settings = Settings()