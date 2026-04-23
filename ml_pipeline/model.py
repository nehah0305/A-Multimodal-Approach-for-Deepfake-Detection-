"""Baseline frame-encoder temporal-aggregation model."""

from __future__ import annotations

import torch
import torch.nn as nn
from torchvision.models import ResNet18_Weights, EfficientNet_B0_Weights
from torchvision import models


class DeepfakeBaselineModel(nn.Module):
    def __init__(self, backbone: str = "resnet18", pretrained: bool = True):
        super().__init__()
        self.backbone_name = backbone

        if backbone == "resnet18":
            weights = ResNet18_Weights.DEFAULT if pretrained else None
            try:
                net = models.resnet18(weights=weights)
            except Exception:
                net = models.resnet18(weights=None)

            feature_dim = net.fc.in_features
            net.fc = nn.Identity()
            self.frame_encoder = net

        elif backbone == "efficientnet_b0":
            weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
            try:
                net = models.efficientnet_b0(weights=weights)
            except Exception:
                net = models.efficientnet_b0(weights=None)

            feature_dim = net.classifier[1].in_features
            net.classifier = nn.Identity()
            self.frame_encoder = net

        else:
            raise ValueError(f"Unsupported backbone: {backbone}")

        self.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(feature_dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: [B, T, C, H, W]
        b, t, c, h, w = x.shape
        x = x.view(b * t, c, h, w)

        frame_features = self.frame_encoder(x)  # [B*T, F]
        frame_features = frame_features.view(b, t, -1)  # [B, T, F]

        # Temporal mean pooling baseline.
        video_features = frame_features.mean(dim=1)  # [B, F]
        logits = self.classifier(video_features).squeeze(1)  # [B]
        return logits
