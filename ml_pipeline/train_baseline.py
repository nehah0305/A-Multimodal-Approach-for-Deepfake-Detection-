"""Train baseline deepfake detector on preprocessed tensors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from torch.utils.data import DataLoader, WeightedRandomSampler

from config import (
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    MODELS_DIR,
    NUM_WORKERS,
    PRETRAINED,
    MODEL_BACKBONE,
    RANDOM_SEED,
    WEIGHT_DECAY,
    DATA_DIR,
)
from dataset import PreprocessedVideoDataset
from model import DeepfakeBaselineModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline deepfake model")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch size")
    parser.add_argument("--num-workers", type=int, default=NUM_WORKERS, help="DataLoader workers")
    parser.add_argument(
        "--subset-size",
        type=int,
        default=None,
        help="Optional limit for number of samples from train/val manifests",
    )
    parser.add_argument(
        "--subset-mode",
        choices=["ratio", "balanced"],
        default="balanced",
        help="Subset strategy: keep original ratio or enforce real/fake balance",
    )
    return parser.parse_args()


def stratified_subset(df, subset_size: int, seed: int):
    if subset_size is None or subset_size >= len(df):
        return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    labels = sorted(df["label"].unique().tolist())
    pieces = []

    for label in labels:
        class_df = df[df["label"] == label]
        # Keep class ratio in subset while guaranteeing at least one sample per class.
        target = max(1, int(round(subset_size * len(class_df) / len(df))))
        take = min(target, len(class_df))
        pieces.append(class_df.sample(n=take, random_state=seed, replace=False))

    subset_df = np.concatenate([piece.index.to_numpy() for piece in pieces])
    selected = df.loc[subset_df]

    if len(selected) < subset_size:
        remaining = df.drop(selected.index, errors="ignore")
        extra = remaining.sample(n=min(subset_size - len(selected), len(remaining)), random_state=seed)
        selected = pd.concat([selected, extra], axis=0)
    elif len(selected) > subset_size:
        selected = selected.sample(n=subset_size, random_state=seed)

    return selected.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def balanced_subset(df, subset_size: int, seed: int):
    if subset_size is None or subset_size >= len(df):
        return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    real_df = df[df["label"] == 0]
    fake_df = df[df["label"] == 1]

    target_real = min(len(real_df), subset_size // 2)
    target_fake = min(len(fake_df), subset_size - target_real)

    real_part = real_df.sample(n=target_real, random_state=seed, replace=False)

    fake_parts = []
    remaining_fake = target_fake

    if "manipulation_type" in fake_df.columns and not fake_df.empty:
        groups = list(fake_df.groupby("manipulation_type"))
        per_group = max(1, target_fake // max(len(groups), 1))
        taken_indices = []
        for group_name, group_df in groups:
            take = min(per_group, len(group_df), remaining_fake)
            if take > 0:
                sampled = group_df.sample(n=take, random_state=seed, replace=False)
                fake_parts.append(sampled)
                taken_indices.extend(sampled.index.tolist())
                remaining_fake -= take

        if remaining_fake > 0:
            leftover_fake = fake_df.drop(index=taken_indices, errors="ignore")
            if len(leftover_fake) > 0:
                fake_parts.append(
                    leftover_fake.sample(n=min(remaining_fake, len(leftover_fake)), random_state=seed, replace=False)
                )
    elif target_fake > 0:
        fake_parts.append(fake_df.sample(n=target_fake, random_state=seed, replace=False))

    selected = pd.concat([real_part] + fake_parts, axis=0)

    if len(selected) < subset_size:
        remaining = df.drop(selected.index, errors="ignore")
        if len(remaining) > 0:
            extra = remaining.sample(n=min(subset_size - len(selected), len(remaining)), random_state=seed)
            selected = pd.concat([selected, extra], axis=0)

    if len(selected) > subset_size:
        selected = selected.sample(n=subset_size, random_state=seed)

    return selected.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


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

    return metrics


def run_epoch(model, loader, criterion, optimizer, device, train: bool):
    if train:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    all_labels = []
    all_probs = []

    with torch.set_grad_enabled(train):
        for frames, labels in loader:
            frames = frames.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            logits = model(frames)
            loss = criterion(logits, labels)

            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            probs = torch.sigmoid(logits)
            total_loss += loss.item() * labels.size(0)
            all_labels.extend(labels.detach().cpu().numpy().tolist())
            all_probs.extend(probs.detach().cpu().numpy().tolist())

    avg_loss = total_loss / max(len(loader.dataset), 1)
    metrics = compute_metrics(np.array(all_labels), np.array(all_probs))
    metrics["loss"] = float(avg_loss)
    return metrics


def main() -> None:
    args = parse_args()
    set_seed(RANDOM_SEED)

    train_csv = DATA_DIR / "train_preprocessed.csv"
    val_csv = DATA_DIR / "val_preprocessed.csv"

    if not train_csv.exists() or not val_csv.exists():
        raise FileNotFoundError(
            "Missing preprocessed manifests. Run: python preprocess_videos.py --split all"
        )

    train_ds = PreprocessedVideoDataset(str(train_csv))
    val_ds = PreprocessedVideoDataset(str(val_csv))

    if args.subset_size is not None:
        if args.subset_mode == "balanced":
            train_ds.df = balanced_subset(train_ds.df, args.subset_size, RANDOM_SEED)
        else:
            train_ds.df = stratified_subset(train_ds.df, args.subset_size, RANDOM_SEED)

        val_limit = max(args.subset_size // 4, 32)
        if args.subset_mode == "balanced":
            val_ds.df = balanced_subset(val_ds.df, val_limit, RANDOM_SEED)
        else:
            val_ds.df = stratified_subset(val_ds.df, val_limit, RANDOM_SEED)

        print(f"Using subset: train={len(train_ds)} val={len(val_ds)}")

    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = DeepfakeBaselineModel(backbone=MODEL_BACKBONE, pretrained=PRETRAINED).to(device)

    y_train = train_ds.df["label"].to_numpy()
    pos_count = int((y_train == 1).sum())
    neg_count = int((y_train == 0).sum())

    # Apply positive-class reweighting only when positive class is minority.
    if pos_count < neg_count and pos_count > 0:
        pos_weight_value = neg_count / pos_count
    else:
        pos_weight_value = 1.0

    print(
        f"Class counts (train): real={neg_count}, fake={pos_count}, "
        f"pos_weight={pos_weight_value:.4f}"
    )

    # Balanced mini-batches improve optimization on imbalanced data.
    class_counts = train_ds.df["label"].value_counts().to_dict()
    class_weights = {
        label: len(train_ds.df) / max(count, 1)
        for label, count in class_counts.items()
    }
    sample_weights = train_ds.df["label"].map(class_weights).to_numpy(dtype=np.float32)
    weighted_sampler = WeightedRandomSampler(
        weights=torch.from_numpy(sample_weights),
        num_samples=len(sample_weights),
        replacement=True,
    )
    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        sampler=weighted_sampler,
        num_workers=args.num_workers,
        pin_memory=True,
    )

    pos_weight = torch.tensor([pos_weight_value], dtype=torch.float32, device=device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    best_auc = -1.0
    history = []

    for epoch in range(1, args.epochs + 1):
        train_metrics = run_epoch(model, train_loader, criterion, optimizer, device, train=True)
        val_metrics = run_epoch(model, val_loader, criterion, optimizer, device, train=False)

        epoch_log = {
            "epoch": epoch,
            "train": train_metrics,
            "val": val_metrics,
        }
        history.append(epoch_log)

        print(
            f"Epoch {epoch:03d} | "
            f"train_loss={train_metrics['loss']:.4f} train_auc={train_metrics['auc']:.4f} | "
            f"val_loss={val_metrics['loss']:.4f} val_auc={val_metrics['auc']:.4f}"
        )

        if val_metrics["auc"] > best_auc:
            best_auc = val_metrics["auc"]
            checkpoint = {
                "model_state_dict": model.state_dict(),
                "epoch": epoch,
                "best_val_auc": best_auc,
                "backbone": MODEL_BACKBONE,
            }
            torch.save(checkpoint, MODELS_DIR / "best_baseline.pt")
            print(f"  Saved new best model (val_auc={best_auc:.4f})")

    with open(MODELS_DIR / "train_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(f"Training finished. Best val AUC: {best_auc:.4f}")


if __name__ == "__main__":
    main()
