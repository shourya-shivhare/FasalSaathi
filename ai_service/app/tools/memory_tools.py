"""
Memory tool wrappers — convenience layer over FarmerMemoryStore.
Accessed via ToolRegistry in graph nodes.
"""
from __future__ import annotations

from ai_service.app.memory.store import FarmerMemoryStore


class MemoryTools:
    """High-level memory access for graph nodes."""

    def __init__(self, store: FarmerMemoryStore):
        self._store = store

    async def get_past_crops(self, user_id: str, limit: int = 5) -> list:
        """Retrieve past crop recommendation history."""
        return await self._store.get_history(user_id, "past_crops", limit)

    async def get_pest_history(self, user_id: str, limit: int = 10) -> list:
        """Retrieve pest detection history."""
        return await self._store.get_history(user_id, "pest_history", limit)

    async def get_scheme_history(self, user_id: str, limit: int = 20) -> list:
        """Retrieve scheme recommendation history."""
        return await self._store.get_history(user_id, "scheme_history", limit)

    async def get_market_history(self, user_id: str, limit: int = 10) -> list:
        """Retrieve market analysis history."""
        return await self._store.get_history(user_id, "market_history", limit)

    async def get_conversation_summaries(self, user_id: str, limit: int = 5) -> list:
        """Retrieve past conversation summaries."""
        return await self._store.get_history(user_id, "conversation_summaries", limit)
