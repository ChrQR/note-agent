from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openrouter_api_key: str
    model_name: str = "deepseek/deepseek-v4-flash"
    pocket_api_key: str
    vikunja_api_key: str
    vikunja_bot_name: str


settings = Settings()  # ty: ignore
