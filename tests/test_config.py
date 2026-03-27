from bot.config import Settings, settings


def test_required_fields():
    fields = Settings.model_fields
    for name in ("bot_token", "database_url", "xai_api_key", "xai_base_url", "xai_model"):
        assert name in fields


def test_defaults():
    assert settings.xai_base_url == "https://api.x.ai/v1"
    assert settings.history_limit == 20
    assert settings.rate_limit_per_minute == 10


def test_loads_from_env():
    s = Settings()
    assert s.bot_token == "test:token"
    assert s.xai_api_key == "xai-test-key"
    assert "asyncpg" in s.database_url
