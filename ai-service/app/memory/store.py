"""
SQLite-based farmer memory store.
Phase 1 persistence — no JSON files, no in-memory-only storage.
Stores crop history, pest history, scheme matches, market analyses, and conversation summaries.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import aiosqlite
import sqlite3

logger = logging.getLogger(__name__)


class FarmerMemoryStore(ABC):
    """Abstract base for farmer memory persistence."""

    @abstractmethod
    async def retrieve(self, user_id: str) -> dict:
        """Retrieve all memory context for a user."""
        ...

    @abstractmethod
    async def persist(self, user_id: str, session_data: dict) -> None:
        """Persist session results to memory."""
        ...

    @abstractmethod
    async def get_history(self, user_id: str, category: str, limit: int = 10) -> list:
        """Retrieve history for a specific category."""
        ...


class SQLiteMemoryStore(FarmerMemoryStore):
    """
    Production memory store using SQLite + aiosqlite.
    Tables created synchronously at init for immediate availability.
    """

    def __init__(self, db_path: str = "ai_memory.db"):
        self.db_path = db_path
        self._init_tables_sync()

    def _init_tables_sync(self) -> None:
        """Create tables synchronously (called once at startup)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS farmer_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    data TEXT NOT NULL,
                    session_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_fm_user
                    ON farmer_memory(user_id);
                CREATE INDEX IF NOT EXISTS idx_fm_cat
                    ON farmer_memory(user_id, category);
                CREATE INDEX IF NOT EXISTS idx_fm_time
                    ON farmer_memory(user_id, created_at DESC);
            """)
        logger.info("💾 SQLiteMemoryStore initialized at %s", self.db_path)

    async def retrieve(self, user_id: str) -> dict:
        """Retrieve all memory context for a user, grouped by category."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT category, data FROM farmer_memory "
                "WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
                (user_id,),
            )
            rows = await cursor.fetchall()

        context: dict[str, list] = {
            "past_crops": [],
            "pest_history": [],
            "scheme_history": [],
            "market_history": [],
            "conversation_summaries": [],
            "recommendation_history": [],
        }

        for row in rows:
            cat = row["category"]
            if cat in context:
                try:
                    context[cat].append(json.loads(row["data"]))
                except json.JSONDecodeError:
                    logger.warning("Malformed memory entry for user=%s, cat=%s", user_id, cat)

        return context

    async def persist(self, user_id: str, session_data: dict) -> None:
        """Persist current session results to memory."""
        entries: list[tuple[str, Any]] = []

        mapping = {
            "crop_recommendations": "past_crops",
            "pest_detection_result": "pest_history",
            "scheme_recommendations": "scheme_history",
            "market_analysis": "market_history",
        }

        for key, cat in mapping.items():
            if session_data.get(key):
                entries.append((cat, session_data[key]))

        if session_data.get("final_summary"):
            entries.append(("conversation_summaries", {
                "summary": session_data["final_summary"],
                "query": session_data.get("user_query", ""),
            }))

        if not entries:
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany(
                "INSERT INTO farmer_memory (user_id, category, data) VALUES (?, ?, ?)",
                [(user_id, cat, json.dumps(data, default=str)) for cat, data in entries],
            )
            await db.commit()

        logger.info("💾 Persisted %d memory entries for user %s", len(entries), user_id)

    async def get_history(self, user_id: str, category: str, limit: int = 10) -> list:
        """Retrieve history entries for a specific category."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT data FROM farmer_memory "
                "WHERE user_id = ? AND category = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, category, limit),
            )
            rows = await cursor.fetchall()

        results = []
        for r in rows:
            try:
                results.append(json.loads(r[0]))
            except json.JSONDecodeError:
                continue
        return results
