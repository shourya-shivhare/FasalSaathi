"""
Temporary image storage layer.
Only image_id (string) enters graph state — never raw bytes.
Prevents checkpoint bloat, slow resumes, and memory pressure.

Phase 1: local uploads/ directory
Future: S3-compatible object storage (swap this class)
"""
from __future__ import annotations

import uuid
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone

import aiofiles

logger = logging.getLogger(__name__)


class ImageStore:
    """Temporary image storage. Only image_id enters graph state, never bytes."""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, image_bytes: bytes, filename: str = "upload.jpg") -> str:
        """Save image bytes to disk. Returns image_id (UUID hex)."""
        ext = Path(filename).suffix or ".jpg"
        image_id = uuid.uuid4().hex
        dest = self.upload_dir / f"{image_id}{ext}"

        async with aiofiles.open(dest, "wb") as f:
            await f.write(image_bytes)

        logger.info(
            "📸 Image saved: id=%s, size=%dKB, file=%s",
            image_id, len(image_bytes) // 1024, dest.name,
        )
        return image_id

    async def get(self, image_id: str) -> bytes:
        """Retrieve image bytes by ID from uploads directory."""
        matches = list(self.upload_dir.glob(f"{image_id}.*"))
        if not matches:
            raise FileNotFoundError(f"No image found for id: {image_id}")

        async with aiofiles.open(matches[0], "rb") as f:
            return await f.read()

    async def delete(self, image_id: str) -> None:
        """Remove image after processing."""
        for f in self.upload_dir.glob(f"{image_id}.*"):
            f.unlink(missing_ok=True)
            logger.debug("🗑️ Image deleted: %s", image_id)

    def get_metadata(self, image_id: str, filename: str, size: int) -> dict:
        """Build metadata dict for graph state (small serializable dict)."""
        return {
            "image_id": image_id,
            "filename": filename,
            "mime_type": f"image/{Path(filename).suffix.lstrip('.')}",
            "size_kb": round(size / 1024, 1),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def cleanup_expired(self, ttl_hours: int = 24) -> int:
        """
        Remove images older than TTL. Called at startup and periodically.
        Prevents orphaned files from YOLO crashes, graph interruptions, etc.
        """
        cutoff = datetime.utcnow() - timedelta(hours=ttl_hours)
        count = 0

        for f in self.upload_dir.glob("*"):
            if f.name == ".gitkeep":
                continue
            try:
                if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                    f.unlink(missing_ok=True)
                    count += 1
            except OSError:
                continue

        if count:
            logger.info("🧹 Cleaned %d expired images (TTL=%dh)", count, ttl_hours)
        return count
