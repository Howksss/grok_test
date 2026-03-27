import os

# env-переменные до импорта bot.*, иначе pydantic-settings упадёт при валидации
os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("XAI_API_KEY", "xai-test-key")
os.environ.setdefault("XAI_BASE_URL", "https://api.x.ai/v1")
os.environ.setdefault("XAI_MODEL", "grok-4-1-fast-non-reasoning")
