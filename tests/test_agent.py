"""Tests for the offline agent fallback (no API key required)."""

from app.agent import run_agent


def test_stock_question_routes_to_tool(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "t.db"))
    from app.config import get_settings

    get_settings.cache_clear()
    reply = run_agent("How much stock of SKU-100 do we have?")
    assert "Stock info" in reply


def test_generic_question_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    reply = run_agent("Tell me a joke")
    assert "ANTHROPIC_API_KEY" in reply
