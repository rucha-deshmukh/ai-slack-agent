"""Tests for the tool registry."""

import pytest

from app.tools import registry


def test_definitions_include_registered_tools():
    names = {d["name"] for d in registry.definitions()}
    assert {"get_stock", "get_weather"} <= names


def test_definitions_have_input_schema():
    for d in registry.definitions():
        assert "input_schema" in d
        assert d["input_schema"]["type"] == "object"


def test_call_unknown_tool_raises():
    with pytest.raises(KeyError):
        registry.call("does_not_exist", {})


def test_get_stock_tool_returns_error_for_unknown_sku(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "t.db"))
    from app.config import get_settings

    get_settings.cache_clear()
    result = registry.call("get_stock", {"sku": "SKU-000"})
    assert "error" in result
