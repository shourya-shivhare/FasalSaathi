"""
SQLite-backed checkpoint saver for LangGraph.
Replaces in-memory MemorySaver — checkpoints survive restarts.
"""
from __future__ import annotations

import logging
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

logger = logging.getLogger(__name__)


def get_checkpointer(db_path: str = "graph_checkpoints.db") -> SqliteSaver:
    """Create SQLite checkpoint saver for the LangGraph pipeline."""
    logger.info("📁 Initializing SqliteSaver at %s", db_path)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return SqliteSaver(conn)
