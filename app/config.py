from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str = "qwen3:8b"

    class Config:
        env_file = ".env"


settings = Settings()