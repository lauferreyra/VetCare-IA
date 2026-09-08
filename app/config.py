from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    llm_model: str
    vetcare_api_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()