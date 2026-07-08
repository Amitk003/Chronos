from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    signing_secret: str = "dev-secret-change-in-production"

    model_config = {"env_prefix": "CHRONOS_"}


settings = Settings()
