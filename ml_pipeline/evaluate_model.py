"""Evaluate trained baseline model on test split."""

from __future__ import annotations

import argparse
import json

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
from torch.utils.data import DataLoader

from config import BATCH_SIZE, DATA_DIR, MODELS_DIR, NUM_WORKERS, RANDOM_SEED
from dataset import PreprocessedVideoDataset
from model import DeepfakeBaselineModel


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict:
    y_pred = (y_prob >= threshold).astype(np.int32)

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }

    try:
        metrics["auc"] = float(roc_auc_score(y_true, y_prob))
    except ValueError:
        metrics["auc"] = 0.0

    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = cm.tolist()
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate trained baseline model")
    parser.add_argument("--threshold", type=float, default=0.5, help="Decision threshold")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Evaluation batch size (use smaller value on low-memory CPU machines)",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=NUM_WORKERS,
        help="DataLoader worker processes",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Optional random subset size for quick evaluation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    test_csv = DATA_DIR / "test_preprocessed.csv"
    checkpoint_path = MODELS_DIR / "best_baseline.pt"

    if not test_csv.exists():
        raise FileNotFoundError("Missing test_preprocessed.csv. Run preprocess_videos.py first.")
    if not checkpoint_path.exists():
        raise FileNotFoundError("Missing model checkpoint best_baseline.pt. Train model first.")

    test_ds = PreprocessedVideoDataset(str(test_csv))
    if args.max_samples is not None and args.max_samples < len(test_ds.df):
        test_ds.df = test_ds.df.sample(n=args.max_samples, random_state=RANDOM_SEED).reset_index(drop=True)
        print(f"Evaluating on quick subset: {len(test_ds)} samples")

    test_loader = DataLoader(
        test_ds,
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
        total_batches = len(test_loader)
        for batch_idx, (frames, labels) in enumerate(test_loader, start=1):
            frames = frames.to(device)
            logits = model(frames)
            probs = torch.sigmoid(logits).cpu().numpy()

            y_prob.extend(probs.tolist())
            y_true.extend(labels.numpy().tolist())

            if batch_idx % 20 == 0 or batch_idx == total_batches:
                print(f"Processed {batch_idx}/{total_batches} batches")

    y_true_arr = np.array(y_true)
    y_prob_arr = np.array(y_prob)

    metrics = compute_metrics(y_true_arr, y_prob_arr, threshold=args.threshold)

    print("Test metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    with open(MODELS_DIR / "test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved metrics to {MODELS_DIR / 'test_metrics.json'}")


if __name__ == "__main__":
    main()
