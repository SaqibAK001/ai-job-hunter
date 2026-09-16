from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str
    database_name: str = "ai_job_hunter"

    jwt_secret: str
    gemini_api_key: str

    resend_api_key: str
    email_from: str
    email_to: str

    cron_secret: str
    job_search_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()