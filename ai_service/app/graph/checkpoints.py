"""
SQLite-backed checkpoint saver for LangGraph.
Replaces in-memory MemorySaver — checkpoints survive restarts.
Supports both synchronous (SqliteSaver) and asynchronous (AsyncSqliteSaver) savers.
"""
from __future__ import annotations

import logging
import asyncio
import aiosqlite

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

logger = logging.getLogger(__name__)

_async_conn: aiosqlite.Connection | None = None
_async_saver: AsyncSqliteSaver | None = None
_loop: asyncio.AbstractEventLoop | None = None


def get_checkpointer(db_path: str = "graph_checkpoints.db") -> SqliteSaver:
    """Create SQLite checkpoint saver for the LangGraph pipeline (synchronous)."""
    logger.info("📁 Initializing SqliteSaver at %s", db_path)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return SqliteSaver(conn)


async def get_async_checkpointer(db_path: str = "graph_checkpoints.db") -> AsyncSqliteSaver:
    """Create or return a singleton AsyncSqliteSaver with a shared connection."""
    global _async_conn, _async_saver, _loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _async_saver is None or _loop != current_loop:
        if _async_conn is not None:
            try:
                # Close old connection associated with previous event loop
                await _async_conn.close()
            except Exception:
                pass
            _async_conn = None
            _async_saver = None

        logger.info("📁 Initializing AsyncSqliteSaver at %s for loop %s", db_path, current_loop)
        _async_conn = await aiosqlite.connect(db_path, check_same_thread=False)
        _async_saver = AsyncSqliteSaver(_async_conn)
        await _async_saver.setup()
        _loop = current_loop

    return _async_saver


async def close_async_checkpointer() -> None:
    """Close the active async checkpointer connection on shutdown."""
    global _async_conn, _async_saver, _loop
    if _async_conn is not None:
        logger.info("📁 Closing AsyncSqliteSaver database connection")
        await _async_conn.close()
        _async_conn = None
        _async_saver = None
        _loop = None


