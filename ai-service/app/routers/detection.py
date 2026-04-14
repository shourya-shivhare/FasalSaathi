from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import tempfile
import uuid
from pathlib import Path
from infer import run_inference
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed image types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

@router.post("/", summary="Detect pests in an image")
async def detect_pests(file: UploadFile = File(...)):
    """
    Endpoint for YOLOv8 pest detection.
    Usage: POST /detect
    Returns: JSON with detections and annotated image path.
    """
    # Validate extension
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file extension {ext}. Use JPG, PNG, or WebP."
        )

    # Save to temp file
    tmp_path = Path(tempfile.gettempdir()) / f"ai_service_det_{uuid.uuid4().hex}{ext}"
    
    try:
        content = await file.read()
        tmp_path.write_bytes(content)

        # Run inference using the helper in project root
        result = run_inference(
            image_path=tmp_path,
            conf_threshold=0.35,
            save_annotated=True
        )
        
        return result

    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
