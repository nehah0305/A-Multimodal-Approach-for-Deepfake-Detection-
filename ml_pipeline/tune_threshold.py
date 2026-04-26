"""Tune decision threshold on validation split for best F1."""

from __future__ import annotations

import argparse
import json

import numpy as np
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from torch.utils.data import DataLoader

from config import DATA_DIR, MODELS_DIR, NUM_WORKERS, RANDOM_SEED
from dataset import PreprocessedVideoDataset
from model import DeepfakeBaselineModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune threshold on validation split")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--num-workers", type=int, default=NUM_WORKERS)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--start", type=float, default=0.1)
    parser.add_argument("--end", type=float, default=0.9)
    parser.add_argument("--step", type=float, default=0.02)
    parser.add_argument(
        "--objective",
        type=str,
        default="f1",
        choices=["f1", "balanced_accuracy", "macro_f1", "min_recall"],
        help="Metric used to select the best threshold",
    )
    return parser.parse_args()


def evaluate_at_threshold(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict:
    y_pred = (y_prob >= threshold).astype(np.int32)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    recall_fake = float(recall_score(y_true, y_pred, zero_division=0))
    recall_real = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    balanced_accuracy = float((recall_real + recall_fake) / 2.0)

    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": recall_fake,
        "recall_fake": recall_fake,
        "recall_real": recall_real,
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "balanced_accuracy": balanced_accuracy,
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
    }


def main() -> None:
    args = parse_args()

    val_csv = DATA_DIR / "val_preprocessed.csv"
    checkpoint_path = MODELS_DIR / "best_baseline.pt"

    if not val_csv.exists():
        raise FileNotFoundError("Missing val_preprocessed.csv. Run preprocess first.")
    if not checkpoint_path.exists():
        raise FileNotFoundError("Missing checkpoint best_baseline.pt. Train model first.")

    val_ds = PreprocessedVideoDataset(str(val_csv))
    if args.max_samples is not None and args.max_samples < len(val_ds.df):
        val_ds.df = val_ds.df.sample(n=args.max_samples, random_state=RANDOM_SEED).reset_index(drop=True)
        print(f"Tuning on subset: {len(val_ds)} samples")

    loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = DeepfakeBaselineModel(backbone=checkpoint.get("backbone", "resnet18"), pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    y_true = []
    y_prob = []

    with torch.no_grad():
        total_batches = len(loader)
        for batch_idx, (frames, labels) in enumerate(loader, start=1):
            frames = frames.to(device)
            logits = model(frames)
            probs = torch.sigmoid(logits).cpu().numpy()

            y_prob.extend(probs.tolist())
            y_true.extend(labels.numpy().tolist())

            if batch_idx % 20 == 0 or batch_idx == total_batches:
                print(f"Processed {batch_idx}/{total_batches} batches")

    y_true_arr = np.array(y_true)
    y_prob_arr = np.array(y_prob)

    thresholds = np.arange(args.start, args.end + 1e-9, args.step)
    results = [evaluate_at_threshold(y_true_arr, y_prob_arr, t) for t in thresholds]

    if args.objective == "min_recall":
        best = max(
            results,
            key=lambda x: (min(x["recall_real"], x["recall_fake"]), x["macro_f1"], x["accuracy"]),
        )
    else:
        best = max(results, key=lambda x: (x[args.objective], x["macro_f1"], x["accuracy"]))

    print("Best threshold on validation split:")
    print(json.dumps(best, indent=2))

    out = {
        "objective": args.objective,
        "best": best,
        "all": results,
    }

    out_path = MODELS_DIR / "threshold_tuning.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Saved threshold tuning to {out_path}")


if __name__ == "__main__":
    main()
