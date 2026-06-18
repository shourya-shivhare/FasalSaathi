"""
Image Upload Node — asks the farmer to upload an image for pest detection.

Bug Fix (was: Command(resume=...)):
  The previous version returned Command(resume={...}), which is the API a
  *caller* uses to RESUME a paused graph — not how a node triggers an interrupt.
  It silently never paused; the graph continued straight to pest_detection
  without an image.

New design (state-machine / non-interrupt):
  1. Set pending_action = "waiting_for_image" and final_response = prompt.
  2. Return normally → graph flows to memory_persist → observability → END.
  3. The checkpointed state carries pending_action = "waiting_for_image".
  4. Next invocation (same session_id, image attached):
       - uploaded_image_id is in the new initial_state (overrides checkpoint).
       - intent_router detects (uploaded_image_id + pending_action) and
         routes directly into the pest workflow.

This makes the pause/resume flow robust across independent API calls,
which is how the chat router actually works (each message is a fresh ainvoke).
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from ai_service.app.graph.state import FasalSaathiState
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
    Ask the farmer to upload an image for pest detection.

    Returns a final_response with the image-request prompt and sets
    pending_action = "waiting_for_image" so the intent_router can detect
    the image on the next invocation and resume the pest workflow.
    """
    start = time.time()

    logger.info("📸 Image upload node — sending image request to farmer")

    return {
        "final_response": IMAGE_REQUEST_PROMPT,
        "pending_action": "waiting_for_image",
        "graph_path": ["image_upload"],
        "timestamps": {"image_requested": _now_iso()},
        "execution_trace": [{
            "node": "image_upload", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": "Image request sent to farmer; waiting for upload in next turn",
            "confidence": 1.0, "timestamp": _now_iso(),
        }],
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
