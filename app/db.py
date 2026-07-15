"""SQLite demo database with a small product catalogue.

This stands in for whatever real datastore an agent would query. It is created
and seeded on first use so the app runs with zero manual setup.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SEED = [
    ("SKU-100", "Wireless Mouse", 42),
    ("SKU-101", "Mechanical Keyboard", 17),
    ("SKU-102", "USB-C Hub", 0),
    ("SKU-103", "1080p Webcam", 8),
]


def _connect(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str) -> None:
    """Create and seed the products table if it does not exist."""
    with _connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                sku   TEXT PRIMARY KEY,
                name  TEXT NOT NULL,
                stock INTEGER NOT NULL
            )
            """
        )
        if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO products (sku, name, stock) VALUES (?, ?, ?)", _SEED
            )
        conn.commit()


def get_stock(path: str, sku: str) -> dict | None:
    """Return {sku, name, stock} for a SKU, or None if not found."""
    with _connect(path) as conn:
        row = conn.execute(
            "SELECT sku, name, stock FROM products WHERE sku = ?", (sku,)
        ).fetchone()
    return dict(row) if row else None
