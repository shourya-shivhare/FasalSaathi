"""
detect.py — Pest detection endpoint for FasalSaathi backend.

Route  : POST /api/v1/detect
Accepts: multipart/form-data image upload
Returns: JSON with detected pests, confidence scores, and treatment suggestions.
"""

import sys
import tempfile
import uuid
import io
from pathlib import Path
from typing import Any, Optional
from PIL import Image, UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve weights path
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
_AI_SERVICE_DIR = _PROJECT_ROOT / "ai_service"
WEIGHTS_PATH = _AI_SERVICE_DIR / "models" / "best.pt"

try:
    from ai_service.infer import run_inference
    from ai_service.app.tools.pest_map import get_full_pest_info
except ImportError as exc:
    run_inference = None       # type: ignore[assignment]
    get_full_pest_info = None  # type: ignore[assignment]
    _IMPORT_ERROR = str(exc)
else:
    _IMPORT_ERROR = None

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.models.user import User
from backend.app.models.enums import PestDetectionSource, NotificationType
from backend.app.models.crop_cycle import CropCycle
from backend.app.models.farm import Farm
from backend.app.models.pest_detection_history import PestDetectionHistory
from backend.app.models.notification import Notification
from backend.app.schemas.pest_history import PestHistoryCreate
from backend.app.services.pest_history_service import PestHistoryService
from backend.app.services.notification_service import NotificationService

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
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

router = APIRouter()


# ---------------------------------------------------------------------------
# Helper: validate uploaded file
# ---------------------------------------------------------------------------

def _validate_upload(file: UploadFile) -> None:
    """Raise HTTPException if the file type is not an accepted image format."""
    content_type = (file.content_type or "").lower()
    file_ext = Path(file.filename or "").suffix.lower()

    if content_type not in ALLOWED_CONTENT_TYPES or file_ext not in ALLOWED_EXTENSIONS:
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

    annotated_path = inference_output.get("annotated_image_path")
    image_url = None
    if annotated_path:
        filename = Path(annotated_path).name
        image_url = f"/static/detections/{filename}"

    return {
        "image": image_filename,
        "total": len(detections),
        "pests": pests,
        "confidence": confidences,
        "bboxes": bboxes,
        "results": full_results,
        "suggestions": all_suggestions,
        "annotated_image_path": image_url,
    }


# ---------------------------------------------------------------------------
# POST /detect
# ---------------------------------------------------------------------------

@router.post(
    "/",
    summary="Detect pests in an uploaded image",
    response_description="Detected pests with confidence scores and treatment suggestions",
    status_code=status.HTTP_200_OK,
)
async def detect_pests(
    file: UploadFile = File(..., description="Farm image to analyse (JPEG/PNG/WebP)"),
    crop_cycle_id: Optional[int] = Form(None, description="Optional crop cycle to link detection to"),
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
) -> JSONResponse:
    """
    Upload a farm/crop image and receive a pest detection report.

    - **file**: Image file (JPEG, PNG, BMP, or WebP).
    - **crop_cycle_id**: Optional ID of the crop cycle to associate this detection with.

    Returns a JSON payload containing:
    - `pests`: List of detected pest class names.
    - `confidence`: Matching confidence scores.
    - `suggestions`: Deduplicated treatment recommendations.
    - `results`: Full per-detection detail (pest, confidence, severity, suggestions).
    - `bboxes`: Bounding box coordinates for each detection.
    """
    # Guard: validate crop ownership early to prevent IDOR and wasted inference work
    crop_name = None
    if current_user and crop_cycle_id is not None:
        crop_cycle = db.query(CropCycle).join(Farm).filter(
            CropCycle.id == crop_cycle_id,
            Farm.user_id == current_user.id
        ).first()
        if crop_cycle:
            crop_name = crop_cycle.crop_name
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or unauthorized crop_cycle_id"
            )

    # Guard: ai_service imports failed
    if run_inference is None or get_full_pest_info is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Inference module could not be loaded. "
                f"Ensure ai_service is on the Python path. Details: {_IMPORT_ERROR}"
            ),
        )

    # Guard: weights not trained yet
    if not WEIGHTS_PATH.exists():
        print(f"[ERROR] Inference failed: weights not found at {WEIGHTS_PATH}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Trained model weights not found. "
                "Please run: python ai_service/train.py  before using this endpoint."
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
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)}MB.",
        )

    # Signature verification
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid or corrupted image content."
        )

    # Save to a temp file (YOLO expects a file path, not bytes)
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    tmp_path = Path(tempfile.gettempdir()) / f"fasalsaathi_{uuid.uuid4().hex}{suffix}"

    try:
        tmp_path.write_bytes(content)

        # Run YOLO inference without blocking the event loop
        inference_output = await run_in_threadpool(
            run_inference,
            image_path=tmp_path,
            weights_path=WEIGHTS_PATH,
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

    # --- Auto-persist pest detections & notify (for authenticated users) ---
    if current_user and payload["total"] > 0:
        # Atomic transaction for persisting history
        try:
            for i, pest_name in enumerate(payload["pests"]):
                confidence = payload["confidence"][i] if i < len(payload["confidence"]) else None
                record = PestDetectionHistory(
                    user_id=current_user.id,
                    crop_cycle_id=crop_cycle_id,
                    disease_name=pest_name,
                    confidence=confidence,
                    image_url=f"detections/{Path(inference_output['annotated_image_path']).name}" if inference_output.get("annotated_image_path") else None,
                    source=PestDetectionSource.YOLO,
                )
                db.add(record)
            db.commit()

        except SQLAlchemyError as exc:
            db.rollback()
            # Clean up orphaned annotated image
            if inference_output.get("annotated_image_path"):
                annot_path = Path(inference_output["annotated_image_path"])
                if annot_path.exists():
                    annot_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while saving detection history."
            ) from exc

        # Dispatch notification separately to avoid coupling
        try:
            disease_names = list(set(payload["pests"]))
            title = f"Pest Alert: {', '.join(disease_names)}"
            message = f"{', '.join(disease_names)} was detected"
            if crop_name:
                message += f" on your {crop_name} crop"
            message += ". Open the Assistant to get treatment recommendations."

            notif = Notification(
                user_id=current_user.id,
                title=title,
                message=message,
                notification_type=NotificationType.PEST_ALERT,
            )
            db.add(notif)
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            print(f"[ERROR] Failed to save notification: {exc}")

    return JSONResponse(content=payload, status_code=status.HTTP_200_OK)

