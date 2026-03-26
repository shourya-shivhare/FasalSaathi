"""
detect.py — Pest detection endpoint for FasalSaathi backend.

Route  : POST /api/v1/detect
Accepts: multipart/form-data image upload
Returns: JSON with detected pests, confidence scores, and treatment suggestions.
"""

import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Path plumbing — make ai-service importable from the backend
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
# backend/app/api/v1/endpoints/detect.py → 5 parents up = project root
_AI_SERVICE_DIR = _PROJECT_ROOT / "ai-service"

if str(_AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_SERVICE_DIR))

# ---------------------------------------------------------------------------
# Internal imports (from ai-service)
# ---------------------------------------------------------------------------
try:
    from infer import run_inference, DEFAULT_WEIGHTS              # noqa: E402
    from utils.pest_map import get_full_pest_info                 # noqa: E402
except ImportError as exc:
    # Non-fatal at import time — the endpoint will return 503 at request time
    run_inference = None       # type: ignore[assignment]
    get_full_pest_info = None  # type: ignore[assignment]
    _IMPORT_ERROR = str(exc)
else:
    _IMPORT_ERROR = None

# ---------------------------------------------------------------------------
# Allowed MIME types for image uploads
# ---------------------------------------------------------------------------
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/webp",
}

# Supported image file extensions (extra validation layer)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

router = APIRouter()


# ---------------------------------------------------------------------------
# Helper: validate uploaded file
# ---------------------------------------------------------------------------

def _validate_upload(file: UploadFile) -> None:
    """Raise HTTPException if the file type is not an accepted image format."""
    content_type = (file.content_type or "").lower()
    file_ext = Path(file.filename or "").suffix.lower()

    if content_type not in ALLOWED_CONTENT_TYPES and file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type '{content_type}'. "
                f"Allowed types: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
            ),
        )


# ---------------------------------------------------------------------------
# Helper: build response payload
# ---------------------------------------------------------------------------

def _build_response(
    inference_output: dict[str, Any],
    image_filename: str,
) -> dict[str, Any]:
    """
    Transform raw inference output into the API response shape.

    Response schema:
        {
            "image":       str,              # original filename
            "total":       int,              # total detections
            "pests":       list[str],        # detected class names
            "confidence":  list[float],      # per-detection confidence
            "bboxes":      list[dict],       # per-detection bounding boxes
            "results":     list[dict],       # full info per detection
            "suggestions": list[str],        # deduplicated treatment tips
        }
    """
    detections = inference_output.get("detections", [])

    pests: list[str] = []
    confidences: list[float] = []
    bboxes: list[dict] = []
    full_results: list[dict] = []
    seen_suggestions: set[str] = set()
    all_suggestions: list[str] = []

    for det in detections:
        cls = det["class"]
        conf = det["confidence"]
        bbox = det["bbox"]

        pests.append(cls)
        confidences.append(conf)
        bboxes.append(bbox)

        info = get_full_pest_info(cls, conf)
        full_results.append(info)

        for tip in info["suggestions"]:
            if tip not in seen_suggestions:
                seen_suggestions.add(tip)
                all_suggestions.append(tip)

    return {
        "image": image_filename,
        "total": len(detections),
        "pests": pests,
        "confidence": confidences,
        "bboxes": bboxes,
        "results": full_results,
        "suggestions": all_suggestions,
        "annotated_image_path": inference_output.get("annotated_image_path"),
    }


# ---------------------------------------------------------------------------
# POST /detect
# ---------------------------------------------------------------------------

@router.post(
    "/detect",
    summary="Detect pests in an uploaded image",
    response_description="Detected pests with confidence scores and treatment suggestions",
    status_code=status.HTTP_200_OK,
)
async def detect_pests(
    file: UploadFile = File(..., description="Farm image to analyse (JPEG/PNG/WebP)"),
) -> JSONResponse:
    """
    Upload a farm/crop image and receive a pest detection report.

    - **file**: Image file (JPEG, PNG, BMP, or WebP).

    Returns a JSON payload containing:
    - `pests`: List of detected pest class names.
    - `confidence`: Matching confidence scores.
    - `suggestions`: Deduplicated treatment recommendations.
    - `results`: Full per-detection detail (pest, confidence, severity, suggestions).
    - `bboxes`: Bounding box coordinates for each detection.
    """
    # Guard: ai-service imports failed
    if run_inference is None or get_full_pest_info is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Inference module could not be loaded. "
                f"Ensure ai-service is on the Python path. Details: {_IMPORT_ERROR}"
            ),
        )

    # Guard: weights not trained yet
    if not DEFAULT_WEIGHTS.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Trained model weights not found. "
                "Please run: python ai-service/train.py  before using this endpoint."
            ),
        )

    # Validate file type
    _validate_upload(file)

    # Read file content
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Save to a temp file (YOLO expects a file path, not bytes)
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    tmp_path = Path(tempfile.gettempdir()) / f"fasalsaathi_{uuid.uuid4().hex}{suffix}"

    try:
        tmp_path.write_bytes(content)

        # Run YOLO inference
        inference_output = run_inference(
            image_path=tmp_path,
            conf_threshold=0.35,
            save_annotated=True,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {exc}",
        ) from exc
    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    # Build and return structured response
    payload = _build_response(inference_output, file.filename or "upload")
    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)
