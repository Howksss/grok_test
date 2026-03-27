from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str
    database_url: str
    xai_api_key: str
    xai_base_url: str = "https://api.x.ai/v1"
    xai_model: str = "grok-4-1-fast-non-reasoning"
    moderation_model: str = "grok-3-mini"
    history_limit: int = 20
    rate_limit_per_minute: int = 10
    system_prompt: str = (
        "Ты — AI-ассистент Grok в Telegram. Отвечай полезно и кратко. "
        "Используй HTML-разметку для форматирования: <b>жирный</b>, <i>курсив</i>, <code>код</code>. "
        "Никогда не используй Markdown-синтаксис вроде **жирный** или *курсив*."
    )

    max_image_bytes: int = 10 * 1024 * 1024   # 10мб софт-лимит, у xAI хард 20мб
    video_timeout: int = 120
    video_poll_interval: int = 7


settings = Settings()
