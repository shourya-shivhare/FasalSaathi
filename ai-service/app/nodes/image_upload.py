"""
Image Upload Node — interrupts graph to request image upload via chat.
Uses Command (not bare interrupt) per Patch 3 for atomic state+interrupt.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from langgraph.types import Command
from app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

IMAGE_REQUEST_PROMPT = (
    "I can help identify the issue affecting your crop.\n\n"
    "Please upload a clear image of:\n"
    "• affected leaves or stems\n"
    "• insects, spots, or visible damage\n"
    "• close-up photos if possible\n"
    "• good lighting without blur\n\n"
    "After upload I can provide:\n"
    "🌱 pest identification\n"
    "🐛 severity assessment\n"
    "💊 treatment suggestions\n"
    "🌾 impact on crop planning"
)


async def image_upload_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Interrupt graph to request image upload inside chat.
    Uses Command for atomic state update + interrupt (Patch 3).
    Graph resumes when user sends next message with image attached.
    """
    start = time.time()

    logger.info("📸 Image upload interrupt — pausing graph for image")

    # Patch 3: Use Command to bundle state update + interrupt atomically
    return Command(
        update={
            "pending_action": "waiting_for_image",
            "graph_path": ["image_upload"],
            "timestamps": {"image_requested": _now_iso()},
            "execution_trace": [{
                "node": "image_upload", "status": "interrupted",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": "Waiting for user image upload",
                "confidence": 1.0, "timestamp": _now_iso(),
            }],
        },
        resume={
            "type": "image_request",
            "message": IMAGE_REQUEST_PROMPT,
        },
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
