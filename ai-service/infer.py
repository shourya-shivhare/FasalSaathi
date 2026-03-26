"""
infer.py — YOLOv8 inference module for FasalSaathi pest detection.

Can be used as a standalone CLI tool or imported as a module by the API layer.

CLI Usage (from project root):
    python ai-service/infer.py --image path/to/image.jpg
    python ai-service/infer.py --image path/to/image.jpg --conf 0.40 --save-dir outputs/
"""

import argparse
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Canonical paths (project-root relative)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # FasalSaathi/
_AI_SERVICE_DIR = Path(__file__).resolve().parent      # FasalSaathi/ai-service/
DEFAULT_WEIGHTS = PROJECT_ROOT / "models" / "best.pt"
DEFAULT_SAVE_DIR = PROJECT_ROOT / "outputs" / "detections"


# ---------------------------------------------------------------------------
# Core inference function (importable by FastAPI routes)
# ---------------------------------------------------------------------------

def load_model(weights_path: Path | str = DEFAULT_WEIGHTS):
    """
    Load a YOLO model from the given weights file.

    Args:
        weights_path: Path to .pt weights file.

    Returns:
        Loaded ultralytics YOLO model object.

    Raises:
        FileNotFoundError: If the weights file does not exist.
        ImportError: If ultralytics is not installed.
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        raise ImportError(
            "ultralytics is not installed. Run: pip install ultralytics"
        )

    weights_path = Path(weights_path)
    if not weights_path.exists():
        raise FileNotFoundError(
            f"Model weights not found at: {weights_path}\n"
            "Place your trained best.pt at:  ai-service/models/best.pt\n"
            "Or run training first:          python ai-service/train.py"
        )

    model = YOLO(str(weights_path))
    return model


def run_inference(
    image_path: str | Path,
    weights_path: str | Path = DEFAULT_WEIGHTS,
    conf_threshold: float = 0.35,
    save_dir: str | Path = DEFAULT_SAVE_DIR,
    save_annotated: bool = True,
) -> dict[str, Any]:
    """
    Run pest detection on a single image.

    Args:
        image_path:      Path to the input image file.
        weights_path:    Path to trained YOLO weights (.pt).
        conf_threshold:  Minimum confidence score to include a detection.
        save_dir:        Directory where annotated output image is saved.
        save_annotated:  Whether to save the annotated result image.

    Returns:
        Dictionary with keys:
            - detections (list[dict]): Per-box results with class, confidence, bbox.
            - annotated_image_path (str | None): Path to saved annotated image.
            - detection_count (int): Total number of detections.

    Raises:
        FileNotFoundError: If image or weights file is missing.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")

    save_dir = Path(save_dir)

    # Load model
    model = load_model(weights_path)

    # Run prediction
    results = model.predict(
        source=str(image_path),
        conf=conf_threshold,
        save=False,          # We handle saving ourselves for better control
        verbose=False,
    )

    detections: list[dict] = []
    annotated_path: str | None = None

    for result in results:
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            continue

        # Extract tensors → Python primitives
        class_ids = boxes.cls.cpu().numpy().astype(int).tolist()
        confidences = boxes.conf.cpu().numpy().tolist()
        bboxes = boxes.xyxy.cpu().numpy().tolist()  # [x1, y1, x2, y2]
        class_names = [result.names[cid] for cid in class_ids]

        for cls_name, conf, bbox in zip(class_names, confidences, bboxes):
            detections.append(
                {
                    "class": cls_name,
                    "confidence": round(float(conf), 4),
                    "bbox": {
                        "x1": round(bbox[0], 2),
                        "y1": round(bbox[1], 2),
                        "x2": round(bbox[2], 2),
                        "y2": round(bbox[3], 2),
                    },
                }
            )

        # Save annotated image
        if save_annotated:
            save_dir.mkdir(parents=True, exist_ok=True)
            annotated_img = result.plot()  # Returns BGR numpy array
            out_filename = f"det_{image_path.stem}{image_path.suffix}"
            out_path = save_dir / out_filename

            import cv2  # opencv-python comes with ultralytics
            cv2.imwrite(str(out_path), annotated_img)
            annotated_path = str(out_path)

    return {
        "detections": detections,
        "annotated_image_path": annotated_path,
        "detection_count": len(detections),
    }


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run YOLOv8 pest inference on an image."
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to the input image file.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default=str(DEFAULT_WEIGHTS),
        help=f"Path to trained weights (default: {DEFAULT_WEIGHTS})",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.35,
        help="Minimum confidence threshold (default: 0.35)",
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        default=str(DEFAULT_SAVE_DIR),
        help=f"Directory to save annotated images (default: {DEFAULT_SAVE_DIR})",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Skip saving the annotated output image.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"\n[→] Running inference on: {args.image}")
    print(f"    Weights  : {args.weights}")
    print(f"    Conf     : {args.conf}\n")

    try:
        output = run_inference(
            image_path=args.image,
            weights_path=args.weights,
            conf_threshold=args.conf,
            save_dir=args.save_dir,
            save_annotated=not args.no_save,
        )
    except (FileNotFoundError, ImportError) as exc:
        print(f"[✗] {exc}")
        sys.exit(1)

    detections = output["detections"]
    print(f"[✓] Detections found: {output['detection_count']}")

    if detections:
        print("\n  Class            | Confidence | Bounding Box")
        print("  " + "-" * 60)
        for det in detections:
            bb = det["bbox"]
            print(
                f"  {det['class']:<16} | {det['confidence']:.4f}     | "
                f"({bb['x1']}, {bb['y1']}) → ({bb['x2']}, {bb['y2']})"
            )
    else:
        print("  No pests detected above confidence threshold.")

    if output["annotated_image_path"]:
        print(f"\n[✓] Annotated image saved: {output['annotated_image_path']}")

    print()


if __name__ == "__main__":
    main()
