"""
Pest Detection Node — runs YOLO inference on uploaded image.
Image loaded by ID from ImageStore (never bytes in state).
Cleanup via try/finally per Patch 2.
"""
from __future__ import annotations

import asyncio
import logging
import time
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def pest_detection_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Run YOLO pest detection on the uploaded image.
    Image bytes loaded via image_store.get(image_id) — never from state.
    Cleanup via try/finally ensures no orphaned temp files.
    """
    start = time.time()
    image_id = state.get("uploaded_image_id")
    runtime = config["configurable"]["runtime"]
    tools = runtime.tool_registry

    if not image_id:
        return {
            "errors": [{"node": "pest_detection", "error": "No uploaded_image_id in state"}],
            "confidence_scores": {"pest": 0.0},
            "graph_path": ["pest_detection"],
            "execution_trace": [{
                "node": "pest_detection", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": "No image ID provided",
                "confidence": 0.0, "timestamp": _now_iso(),
            }],
        }

    try:
        # Load image bytes from disk (NOT from state)
        image_bytes = await tools.image_store.get(image_id)

        # Run YOLO inference in a thread (it's CPU-bound)
        result = await _run_yolo_inference(image_bytes)

        # Enrich with pest map suggestions
        for detection in result.get("detections", []):
            try:
                info = tools.pest_map.get_full_pest_info(
                    detection["class"], detection["confidence"]
                )
                detection["severity"] = info.get("severity", "Unknown")
                detection["suggestions"] = info.get("suggestions", [])
            except Exception:
                detection["suggestions"] = []

        avg_conf = _avg_confidence(result)

        logger.info(
            "🐛 Pest detection: %d detections, avg_conf=%.2f",
            result.get("detection_count", 0), avg_conf,
        )

        return {
            "pest_detection_result": result,
            "confidence_scores": {"pest": avg_conf},
            "reasoning_steps": [{
                "agent": "pest_detection",
                "reasoning": (
                    f"Detected {result['detection_count']} pest(s). "
                    f"Classes: {', '.join(d['class'] for d in result['detections'][:3])}. "
                    f"Avg confidence: {avg_conf:.2f}."
                    if result["detections"] else "No pests detected."
                ),
                "confidence": avg_conf,
            }],
            "graph_path": ["pest_detection"],
            "timestamps": {"pest_completed": _now_iso()},
            "execution_trace": [{
                "node": "pest_detection", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "tools_used": ["yolo_inference", "pest_map"],
                "reasoning": f"{result['detection_count']} pest(s) detected",
                "confidence": avg_conf, "timestamp": _now_iso(),
            }],
        }

    except Exception as e:
        logger.error("Pest detection failed: %s", e)
        return {
            "graph_path": ["pest_detection"],
            "errors": [{"node": "pest_detection", "error": str(e)}],
            "confidence_scores": {"pest": 0.0},
            "execution_trace": [{
                "node": "pest_detection", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Error: {e}", "confidence": 0.0,
                "timestamp": _now_iso(),
            }],
        }
    finally:
        # Patch 2: ALWAYS clean up, even on failure
        try:
            await tools.image_store.delete(image_id)
        except Exception:
            pass


async def _run_yolo_inference(image_bytes: bytes) -> dict:
    """Run YOLO in a thread pool (CPU-bound operation)."""
    loop = asyncio.get_running_loop()

    def _infer():
        # Write bytes to temp file for YOLO
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        try:
            from ai_service.infer import run_inference
            return run_inference(
                image_path=tmp_path,
                conf_threshold=0.35,
                save_annotated=False,
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    return await loop.run_in_executor(None, _infer)


def _avg_confidence(result: dict) -> float:
    """Compute average detection confidence."""
    detections = result.get("detections", [])
    if not detections:
        return 0.0
    return sum(d.get("confidence", 0) for d in detections) / len(detections)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
