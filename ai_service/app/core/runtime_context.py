"""
Runtime context — injected via config["configurable"]["runtime"].
Never stored in graph state. Never serialized by checkpoints.

This keeps live objects (DB connections, HTTP clients) out of
the serialization path while making them available to every node.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_service.app.core.tool_registry import ToolRegistry


@dataclass
class GraphRuntimeContext:
    """Injected via config['configurable']['runtime']. Never in graph state."""
    tool_registry: ToolRegistry
