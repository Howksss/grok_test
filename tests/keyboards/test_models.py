from bot.config import settings
from bot.keyboards.models import AVAILABLE_MODELS, build_model_keyboard


def test_default_model_in_list():
    assert settings.xai_model in AVAILABLE_MODELS


def test_keyboard_has_all_models():
    kb = build_model_keyboard()
    buttons = [btn.text for row in kb.inline_keyboard for btn in row]
    assert set(buttons) == set(AVAILABLE_MODELS)


def test_callback_data_format():
    kb = build_model_keyboard()
    for row in kb.inline_keyboard:
        for btn in row:
            assert btn.callback_data.startswith("model:")
