"""Datasets for preprocessed deepfake training data."""

from __future__ import annotations

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


class PreprocessedVideoDataset(Dataset):
    def __init__(self, manifest_csv: str):
        self.df = pd.read_csv(manifest_csv)
        if self.df.empty:
            raise ValueError(f"Empty dataset manifest: {manifest_csv}")

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, index: int):
        row = self.df.iloc[index]
        frames = np.load(row["tensor_path"])  # [T, H, W, C]

        frames_tensor = torch.from_numpy(frames).permute(0, 3, 1, 2).float()  # [T, C, H, W]
        label = torch.tensor(float(row["label"]), dtype=torch.float32)

        return frames_tensor, label
