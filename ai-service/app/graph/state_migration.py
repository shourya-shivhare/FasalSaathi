"""
State schema migration — handles checkpoint evolution across versions.
Called when resuming from a checkpoint with an older schema version.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 1


def migrate_state(state: dict) -> dict:
    """
    Migrate checkpoint state to current schema version.
    Called before processing a resumed graph invocation.
    """
    version = state.get("state_schema_version", 1)

    if version < CURRENT_SCHEMA_VERSION:
        logger.info(
            "Migrating state from v%d to v%d", version, CURRENT_SCHEMA_VERSION
        )
        # ── Future migration steps go here ────────────
        # if version < 2:
        #     state.setdefault("new_field", default_value)
        #     ...

    state["state_schema_version"] = CURRENT_SCHEMA_VERSION
    return state
