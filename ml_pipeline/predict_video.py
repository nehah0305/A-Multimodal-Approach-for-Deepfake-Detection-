"""Run single-video prediction with a trained checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from config import FRAME_SIZE, NUM_FRAMES_PER_VIDEO, MODELS_DIR
from model import DeepfakeBaselineModel
from preprocess_videos import extract_frames


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict deepfake probability for one video")
    parser.add_argument("video_path", type=str, help="Absolute or relative path to video")
    parser.add_argument("--checkpoint", type=str, default=str(MODELS_DIR / "best_baseline.pt"))
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    video_path = Path(args.video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    frames = extract_frames(video_path, FRAME_SIZE, NUM_FRAMES_PER_VIDEO)
    if frames.shape[0] == 0:
        raise RuntimeError("Could not decode frames from video")

    input_tensor = torch.from_numpy(frames).permute(0, 3, 1, 2).float().unsqueeze(0)  # [1, T, C, H, W]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model = DeepfakeBaselineModel(backbone=checkpoint.get("backbone", "resnet18"), pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    with torch.no_grad():
        logits = model(input_tensor.to(device))
        probability_fake = torch.sigmoid(logits).item()

    label = "FAKE" if probability_fake >= args.threshold else "REAL"
    confidence = probability_fake if label == "FAKE" else 1.0 - probability_fake

    print("Prediction result")
    print(f"  video: {video_path}")
    print(f"  label: {label}")
    print(f"  probability_fake: {probability_fake:.4f}")
    print(f"  confidence: {confidence:.4f}")


if __name__ == "__main__":
    main()
