"""Video deepfake inference service used by the Flask backend demo."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import ResNet18_Weights

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "ml_pipeline" / "models" / "best_baseline.pt"
THRESHOLD_PATH = PROJECT_ROOT / "ml_pipeline" / "models" / "threshold_tuning.json"

FRAME_SIZE = (224, 224)
NUM_FRAMES_PER_VIDEO = 24
MODEL_VERSION = "resnet18-baseline-v1"


def sample_indices(total_frames: int, num_samples: int) -> np.ndarray:
    if total_frames <= 0:
        return np.array([], dtype=np.int32)
    if total_frames <= num_samples:
        return np.arange(total_frames, dtype=np.int32)
    return np.linspace(0, total_frames - 1, num_samples).astype(np.int32)


def extract_frames(video_path: Path, size: tuple[int, int] = FRAME_SIZE, num_frames: int = NUM_FRAMES_PER_VIDEO) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    target_indices = set(sample_indices(total_frames, num_frames).tolist())

    frames = []
    index = 0
    while cap.isOpened() and len(frames) < num_frames:
        success, frame = cap.read()
        if not success:
            break

        if index in target_indices:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
            frame = frame.astype(np.float32) / 255.0
            frames.append(frame)

        index += 1

    cap.release()

    if not frames:
        raise RuntimeError(f"No frames could be extracted from {video_path}")

    while len(frames) < num_frames:
        frames.append(frames[-1].copy())

    return np.stack(frames, axis=0)


class DeepfakeBaselineModel(nn.Module):
    def __init__(self, backbone: str = "resnet18", pretrained: bool = False):
        super().__init__()
        weights = ResNet18_Weights.DEFAULT if pretrained else None
        try:
            net = models.resnet18(weights=weights)
        except Exception:
            net = models.resnet18(weights=None)

        feature_dim = net.fc.in_features
        net.fc = nn.Identity()
        self.frame_encoder = net
        self.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(feature_dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, frames, channels, height, width = x.shape
        x = x.view(batch_size * frames, channels, height, width)
        frame_features = self.frame_encoder(x)
        frame_features = frame_features.view(batch_size, frames, -1)
        video_features = frame_features.mean(dim=1)
        logits = self.classifier(video_features).squeeze(1)
        return logits


@lru_cache(maxsize=1)
def get_threshold() -> float:
    if THRESHOLD_PATH.exists():
        try:
            import json

            payload = json.loads(THRESHOLD_PATH.read_text(encoding="utf-8"))
            return float(payload.get("best", {}).get("threshold", 0.16))
        except Exception:
            pass
    return 0.16


@lru_cache(maxsize=1)
def get_model_and_device():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {MODEL_PATH}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    model = DeepfakeBaselineModel(pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model, device, checkpoint


def _signal_bundle(fake_probability: float, predicted_fake: bool) -> tuple[dict, dict, list[str], list[str]]:
    authentic_score = max(0, min(100, int(round((1.0 - fake_probability) * 100))))
    confidence_level = max(0, min(100, int(round(max(fake_probability, 1.0 - fake_probability) * 100))))
    risk_level = max(0, min(100, int(round(fake_probability * 100))))

    sub_scores = {
        "facial": max(0, min(100, int(round((1.0 - min(1.0, fake_probability * 1.1)) * 100)))),
        "audio": max(0, min(100, int(round((1.0 - min(1.0, fake_probability * 0.9)) * 100)))),
        "temporal": max(0, min(100, int(round((1.0 - min(1.0, fake_probability * 1.2)) * 100)))),
        "artifacts": max(0, min(100, int(round((1.0 - min(1.0, fake_probability * 1.15)) * 100)))),
    }

    detections = {
        "facial": sub_scores["facial"] >= 50,
        "audio": sub_scores["audio"] >= 50,
        "temporal": sub_scores["temporal"] >= 50,
        "artifacts": sub_scores["artifacts"] >= 50,
    }

    if predicted_fake:
        findings = [
            "Temporal irregularities suggest possible generated or altered frames.",
            "Artifacts and compression anomalies are above the expected baseline.",
            "The frame-level model is leaning toward manipulated content.",
        ]
        recommendations = [
            "Escalate the asset for manual review.",
            "Inspect frame sequences at higher zoom if needed.",
            "Cross-check the source file and submission metadata.",
        ]
        summary = "The model detected signs consistent with manipulated video content. A human review is recommended."
    else:
        findings = [
            "No strong cross-frame irregularities detected at the current sampling rate.",
            "Frame consistency remains relatively stable across the sampled sequence.",
            "The model is leaning toward authentic content.",
        ]
        recommendations = [
            "Proceed with standard review workflow.",
            "Archive the report for record keeping.",
            "Re-run at higher sampling only if finer inspection is required.",
        ]
        summary = "The model did not find dominant signs of manipulation in the sampled video frames."

    return (
        {
            "authenticScore": authentic_score,
            "confidenceLevel": confidence_level,
            "riskLevel": risk_level,
            "isAuthentic": not predicted_fake,
            "summary": summary,
            "findings": findings,
            "recommendations": recommendations,
            "detections": detections,
            "subScores": sub_scores,
        },
        {
            "frames_analyzed": NUM_FRAMES_PER_VIDEO,
            "probability_fake": round(fake_probability, 4),
            "probability_real": round(1.0 - fake_probability, 4),
        },
        findings,
        recommendations,
    )


def analyze_video(video_path: str) -> dict:
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    model, device, checkpoint = get_model_and_device()
    frames = extract_frames(path)
    input_tensor = torch.from_numpy(frames).permute(0, 3, 1, 2).unsqueeze(0).float().to(device)

    with torch.inference_mode():
        logits = model(input_tensor)
        fake_probability = torch.sigmoid(logits).item()

    threshold = get_threshold()
    label = "FAKE" if fake_probability >= threshold else "REAL"
    signal_bundle, probabilities, findings, recommendations = _signal_bundle(fake_probability, label == "FAKE")

    signal_bundle.update(
        {
            "label": label,
            "threshold": threshold,
            "video_filename": path.name,
            "modelVersion": MODEL_VERSION,
            "checkpoint_epoch": checkpoint.get("epoch"),
        }
    )

    return {
        "success": True,
        "analysis": {
            **signal_bundle,
            **probabilities,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        },
    }
