from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

AVAILABLE_MODELS = [
    "grok-4-1-fast-non-reasoning",
    "grok-4-1-fast-reasoning",
    "grok-4.20-0309-non-reasoning",
    "grok-4.20-0309-reasoning",
]

MODEL_CB_PREFIX = "model:"


def build_model_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=m, callback_data=f"model:{m}")]
            for m in AVAILABLE_MODELS
        ]
    )
