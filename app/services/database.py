"""
WeatherGPT — Database Service (SQLite via aiosqlite)

Single SQLite file for all relational data:
  - subscriptions: push notification subscriptions
  - alert_log: historical alert records

Deliberate deviation from the pitch deck's Firebase + PostgreSQL split —
two databases is unnecessary complexity for a demo.
"""

import sqlite3
import aiosqlite
import uuid
from datetime import datetime
from typing import Optional

from app.core.config import settings

# Extract the file path from the connection URL
# "sqlite+aiosqlite:///./weathergpt.db" → "./weathergpt.db"
_DB_PATH = settings.database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")


async def init_db():
    """Create tables if they don't exist."""
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                contact TEXT NOT NULL,
                channel TEXT NOT NULL DEFAULT 'whatsapp',
                location TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'citizen',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alert_log (
                id TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                alert_level TEXT NOT NULL,
                headline TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.commit()


async def add_subscription(
    contact: str,
    channel: str,
    location: str,
    role: str,
) -> dict:
    """Add a new subscription. Returns the created record."""
    sub_id = str(uuid.uuid4())[:8]
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.execute(
            "INSERT INTO subscriptions (id, contact, channel, location, role) VALUES (?, ?, ?, ?, ?)",
            (sub_id, contact, channel, location, role),
        )
        await db.commit()
    return {"id": sub_id, "status": "subscribed"}


async def get_subscriptions(location: Optional[str] = None) -> list[dict]:
    """Get all subscriptions, optionally filtered by location."""
    async with aiosqlite.connect(_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if location:
            cursor = await db.execute(
                "SELECT * FROM subscriptions WHERE LOWER(location) LIKE ?",
                (f"%{location.lower()}%",),
            )
        else:
            cursor = await db.execute("SELECT * FROM subscriptions")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def log_alert(location: str, alert_level: str, headline: Optional[str] = None):
    """Log an alert for historical tracking."""
    alert_id = str(uuid.uuid4())[:8]
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.execute(
            "INSERT INTO alert_log (id, location, alert_level, headline) VALUES (?, ?, ?, ?)",
            (alert_id, location, alert_level, headline),
        )
        await db.commit()


async def get_recent_alerts(location: Optional[str] = None, limit: int = 10) -> list[dict]:
    """Get recent alerts, optionally filtered by location."""
    async with aiosqlite.connect(_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if location:
            cursor = await db.execute(
                "SELECT * FROM alert_log WHERE LOWER(location) LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{location.lower()}%", limit),
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM alert_log ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
