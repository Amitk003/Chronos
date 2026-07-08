from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    signing_secret: str = "dev-secret-change-in-production"
    jobs_db_url: str = "sqlite:///chronos_jobs.sqlite"

    model_config = {"env_prefix": "CHRONOS_"}


settings = Settings()
