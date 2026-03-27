import importlib

import pytest


@pytest.mark.parametrize("module_path", [
    "bot",
    "bot.database",
    "bot.handlers",
    "bot.services",
    "bot.keyboards",
])
def test_package_importable(module_path):
    mod = importlib.import_module(module_path)
    assert mod is not None
