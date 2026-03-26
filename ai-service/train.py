"""
train.py — YOLOv8 training pipeline for FasalSaathi pest detection.

Usage (from project root):
    python ai-service/train.py
    python ai-service/train.py --epochs 50 --imgsz 640 --batch 16 --device cpu
"""

import argparse
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — ensure project root is importable regardless of CWD
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # FasalSaathi/
DATA_YAML = PROJECT_ROOT / "data" / "data.yaml"
WEIGHTS_DIR = PROJECT_ROOT / "runs" / "detect"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train YOLOv8 pest detection model for FasalSaathi"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="Base YOLO model checkpoint (default: yolov8n.pt)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=10,
        help="Number of training epochs (default: 10)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Input image size in pixels (default: 640)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Batch size per step (default: 16, use -1 for auto)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="",
        help="Training device: '' for auto-select, 'cpu', '0' for GPU 0 (default: auto)",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=str(PROJECT_ROOT / "runs" / "detect"),
        help="Output directory for training runs",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="train",
        help="Name of this training run (default: train)",
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=20,
        help="Early stopping patience in epochs (default: 20)",
    )
    return parser.parse_args()


def validate_dataset(data_yaml: Path) -> None:
    """Raise an informative error if data.yaml or expected dirs are missing."""
    if not data_yaml.exists():
        raise FileNotFoundError(
            f"Dataset config not found at: {data_yaml}\n"
            "Make sure your data/ folder is at the project root."
        )
    print(f"[✓] Dataset config found: {data_yaml}")


def train(args: argparse.Namespace) -> Path:
    """
    Run the YOLO training loop.

    Returns:
        Path to the best weights file produced by training.
    """
    # Late import so missing ultralytics gives a clear message
    try:
        from ultralytics import YOLO
    except ImportError:
        print(
            "[✗] ultralytics is not installed.\n"
            "    Run:  pip install ultralytics"
        )
        sys.exit(1)

    validate_dataset(DATA_YAML)

    print("\n" + "=" * 60)
    print("  FasalSaathi — YOLOv8 Pest Detection Training")
    print("=" * 60)
    print(f"  Model      : {args.model}")
    print(f"  Epochs     : {args.epochs}")
    print(f"  Image size : {args.imgsz}")
    print(f"  Batch      : {args.batch}")
    print(f"  Device     : {args.device or 'auto'}")
    print(f"  Output     : {args.project}/{args.name}")
    print("=" * 60 + "\n")

    # Load base model
    print(f"[→] Loading model: {args.model}")
    model = YOLO(args.model)

    start = time.time()

    try:
        results = model.train(
            data=str(DATA_YAML),
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device if args.device else None,
            project=args.project,
            name=args.name,
            patience=args.patience,
            exist_ok=True,          # Re-use run dir on repeated calls
            verbose=True,
        )
    except Exception as exc:
        print(f"\n[✗] Training failed: {exc}")
        raise

    elapsed = time.time() - start
    print(f"\n[✓] Training completed in {elapsed / 60:.1f} minutes.")

    # Locate best weights
    best_weights = Path(args.project) / args.name / "weights" / "best.pt"
    if best_weights.exists():
        print(f"[✓] Best weights saved at: {best_weights}")
    else:
        print(
            "[!] best.pt not found at expected path — check the runs/ directory manually."
        )

    return best_weights


def main() -> None:
    args = parse_args()
    best_weights = train(args)
    print(f"\n[→] Next step — run inference:")
    print(f"    python ai-service/infer.py --image <path/to/image.jpg>")
    print(f"    (weights: {best_weights})\n")


if __name__ == "__main__":
    main()
