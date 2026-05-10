from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    print(model_config)
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    ANTHROPIC_API_KEY: str
    GROQ_API_KEY: str
    HUGGINGFACEHUB_API_TOKEN: str


settings = Settings()
