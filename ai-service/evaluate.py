"""
evaluate.py — Evaluate the FasalSaathi YOLO pest detection model.

Runs YOLO validation on the test split and reports:
  • Overall mAP@0.5, mAP@0.5:0.95
  • Precision, Recall, F1
  • Per-class breakdown
  • Confusion matrix saved to disk

Usage (from project root):
    python ai-service/evaluate.py
    python ai-service/evaluate.py --split test
    python ai-service/evaluate.py --split val
"""

import argparse
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT  = Path(__file__).resolve().parent.parent   # FasalSaathi/
WEIGHTS       = PROJECT_ROOT / "models" / "best.pt"
DATA_YAML     = PROJECT_ROOT / "data" / "data.yaml"
SAVE_DIR      = PROJECT_ROOT / "runs" / "evaluate"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate FasalSaathi YOLO model")
    p.add_argument("--weights", default=str(WEIGHTS),
                   help=f"Path to .pt weights (default: {WEIGHTS})")
    p.add_argument("--data",    default=str(DATA_YAML),
                   help=f"Path to data.yaml (default: {DATA_YAML})")
    p.add_argument("--split",   default="test", choices=["test", "val", "train"],
                   help="Dataset split to evaluate on (default: test)")
    p.add_argument("--imgsz",   default=640, type=int,
                   help="Image size (default: 640)")
    p.add_argument("--conf",    default=0.25, type=float,
                   help="Confidence threshold (default: 0.25)")
    p.add_argument("--iou",     default=0.50, type=float,
                   help="IoU threshold for NMS (default: 0.50)")
    p.add_argument("--device",  default="",
                   help="Device: '' auto, 'cpu', '0' for GPU 0")
    return p.parse_args()


def print_banner(args):
    print("\n" + "=" * 62)
    print("  FasalSaathi - Pest Detection Model Evaluation")
    print("=" * 62)
    print(f"  Weights : {args.weights}")
    print(f"  Data    : {args.data}")
    print(f"  Split   : {args.split}")
    print(f"  ImgSz   : {args.imgsz}")
    print(f"  Conf    : {args.conf}   IoU : {args.iou}")
    print("=" * 62 + "\n")


def run_evaluation(args):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[✗] ultralytics not installed. Run: pip install ultralytics")
        sys.exit(1)

    w = Path(args.weights)
    if not w.exists():
        print(f"[✗] Weights not found: {w}")
        sys.exit(1)

    d = Path(args.data)
    if not d.exists():
        print(f"[✗] data.yaml not found: {d}")
        sys.exit(1)

    print(f"[→] Loading model from: {w}")
    model = YOLO(str(w))

    print(f"[→] Running validation on [{args.split}] split …\n")

    metrics = model.val(
        data=str(d),
        split=args.split,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        device=args.device if args.device else None,
        project=str(SAVE_DIR),
        name=f"eval_{args.split}",
        exist_ok=True,
        verbose=False,        # suppress ultralytics raw logs; we print our own
        save_json=True,       # saves COCO-format results
        plots=True,           # saves confusion matrix + PR curve PNGs
    )

    return metrics


def print_results(metrics, args):
    # ── class names ─────────────────────────────────────────────────────────
    from ultralytics import YOLO
    model_temp = YOLO(args.weights)
    class_names = model_temp.names   # {0: 'Ants', 1: 'Bees', …}

    # ── top-level metrics ─────────────────────────────────────────────────
    mp   = float(metrics.box.mp)     # mean precision
    mr   = float(metrics.box.mr)     # mean recall
    map50     = float(metrics.box.map50)
    map50_95  = float(metrics.box.map)
    f1_mean   = 2 * mp * mr / (mp + mr + 1e-9)

    print("\n" + "=" * 62)
    print("  [STATS] OVERALL RESULTS")
    print("=" * 62)
    print(f"  {'Metric':<28} {'Value':>10}")
    print("  " + "-" * 40)
    print(f"  {'Precision (mean)':<28} {mp:>10.4f}")
    print(f"  {'Recall    (mean)':<28} {mr:>10.4f}")
    print(f"  {'F1-Score  (mean)':<28} {f1_mean:>10.4f}")
    print(f"  {'mAP @ IoU 0.50':<28} {map50:>10.4f}")
    print(f"  {'mAP @ IoU 0.50:0.95':<28} {map50_95:>10.4f}")
    print("=" * 62)

    # ── per-class breakdown ──────────────────────────────────────────────
    ap50_per_class = metrics.box.ap50          # shape: (num_classes,)
    ap_per_class   = metrics.box.ap            # mAP 0.5:0.95 per class
    p_per_class    = metrics.box.p             # precision per class
    r_per_class    = metrics.box.r             # recall per class

    print("\n  [TABLE] PER-CLASS BREAKDOWN")
    print("  " + "-" * 62)
    header = f"  {'Class':<16} {'P':>8} {'R':>8} {'F1':>8} {'AP@.5':>8} {'AP@.5:.95':>10}"
    print(header)
    print("  " + "─" * 62)

    rows = []
    for i, name in class_names.items():
        if i >= len(ap50_per_class):
            continue
        p_i  = float(p_per_class[i])  if i < len(p_per_class)  else 0.0
        r_i  = float(r_per_class[i])  if i < len(r_per_class)  else 0.0
        f1_i = 2 * p_i * r_i / (p_i + r_i + 1e-9)
        ap50_i  = float(ap50_per_class[i])
        ap_i    = float(ap_per_class[i]) if i < len(ap_per_class) else 0.0
        rows.append((name, p_i, r_i, f1_i, ap50_i, ap_i))

    # sort by AP@.5 descending
    rows.sort(key=lambda x: x[4], reverse=True)

    for name, p_i, r_i, f1_i, ap50_i, ap_i in rows:
        bar = "#" * int(ap50_i * 10) + "-" * (10 - int(ap50_i * 10))
        print(f"  {name:<16} {p_i:>8.4f} {r_i:>8.4f} {f1_i:>8.4f} "
              f"{ap50_i:>8.4f} {ap_i:>10.4f}  [{bar}]")

    print("  " + "─" * 62)

    # ── quick grade ────────────────────────────────────────────────────────
    print("\n  [GRADE] MODEL GRADE")
    print("  " + "-" * 40)
    if map50 >= 0.80:
        grade = "Excellent"
    elif map50 >= 0.65:
        grade = "Good"
    elif map50 >= 0.50:
        grade = "Fair -- consider more epochs / augmentation"
    else:
        grade = "Needs improvement -- review data quality and training"
    print(f"  mAP@0.5 = {map50:.4f}  ->  {grade}")

    # ── saved artifacts ────────────────────────────────────────────────────
    eval_dir = SAVE_DIR / f"eval_{args.split}"
    print(f"\n  [FILES] Artifacts saved to: {eval_dir}")
    print("       - confusion_matrix.png")
    print("       - PR_curve.png")
    print("       - predictions.json  (COCO format)")
    print("\n" + "=" * 62 + "\n")


def main():
    args = parse_args()
    print_banner(args)
    metrics = run_evaluation(args)
    print_results(metrics, args)


if __name__ == "__main__":
    main()
