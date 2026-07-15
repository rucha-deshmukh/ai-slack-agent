"""Tests for the SQLite demo database."""

from app.db import get_stock, init_db


def test_init_and_lookup(tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    result = get_stock(db, "SKU-100")
    assert result is not None
    assert result["sku"] == "SKU-100"
    assert result["stock"] >= 0


def test_unknown_sku_returns_none(tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    assert get_stock(db, "SKU-999") is None


def test_init_is_idempotent(tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    init_db(db)  # should not raise or duplicate rows
    assert get_stock(db, "SKU-101") is not None
