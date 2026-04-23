"""Preprocess FaceForensics++ videos into fixed frame tensors for training."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from config import (
    DATA_DIR,
    FRAME_SIZE,
    NUM_FRAMES_PER_VIDEO,
    PREPROCESSED_DIR,
    TRAIN_SPLIT,
    VAL_SPLIT,
    TEST_SPLIT,
)


def sample_indices(total_frames: int, num_samples: int) -> np.ndarray:
    if total_frames <= 0:
        return np.array([], dtype=np.int32)
    if total_frames <= num_samples:
        return np.arange(total_frames, dtype=np.int32)
    return np.linspace(0, total_frames - 1, num_samples).astype(np.int32)


def extract_frames(video_path: Path, size: tuple[int, int], num_frames: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return np.empty((0, size[1], size[0], 3), dtype=np.float32)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = set(sample_indices(total_frames, num_frames).tolist())

    frames = []
    idx = 0
    while cap.isOpened() and len(frames) < num_frames:
        success, frame = cap.read()
        if not success:
            break

        if idx in indices:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
            frame = frame.astype(np.float32) / 255.0
            frames.append(frame)

        idx += 1

    cap.release()

    if not frames:
        return np.empty((0, size[1], size[0], 3), dtype=np.float32)

    # Pad short clips by repeating last frame so shape is fixed.
    while len(frames) < num_frames:
        frames.append(frames[-1].copy())

    return np.stack(frames, axis=0)


def process_split(split_name: str, split_file: Path, max_videos: int | None = None) -> None:
    if not split_file.exists():
        raise FileNotFoundError(f"Missing split file: {split_file}")

    split_df = pd.read_csv(split_file)
    if max_videos is not None:
        split_df = split_df.head(max_videos).copy()

    out_dir = PREPROCESSED_DIR / split_name
    out_dir.mkdir(parents=True, exist_ok=True)

    output_records = []
    print(f"Processing {split_name}: {len(split_df)} videos")

    for idx, row in split_df.iterrows():
        video_path = Path(row["video_path"])
        if not video_path.exists():
            continue

        tensor = extract_frames(video_path, FRAME_SIZE, NUM_FRAMES_PER_VIDEO)
        if tensor.shape[0] == 0:
            continue

        relative_id = row["relative_path"].replace("/", "__").replace(".mp4", ".npy")
        tensor_path = out_dir / relative_id
        np.save(tensor_path, tensor)

        output_records.append(
            {
                "video_path": row["video_path"],
                "relative_path": row["relative_path"],
                "label": int(row["label"]),
                "label_name": row["label_name"],
                "manipulation_type": row["manipulation_type"],
                "identity_group": row["identity_group"],
                "tensor_path": str(tensor_path),
                "num_frames_sampled": int(tensor.shape[0]),
                "height": tensor.shape[1],
                "width": tensor.shape[2],
            }
        )

        if (len(output_records) % 100) == 0:
            print(f"  Saved {len(output_records)} tensors...")

    out_manifest = DATA_DIR / f"{split_name}_preprocessed.csv"
    pd.DataFrame(output_records).to_csv(out_manifest, index=False)
    print(f"Saved {split_name} manifest: {out_manifest} ({len(output_records)} samples)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess videos into frame tensors")
    parser.add_argument(
        "--split",
        choices=["all", "train", "val", "test"],
        default="all",
        help="Which split to preprocess",
    )
    parser.add_argument("--max-videos", type=int, default=None, help="Limit videos for quick test")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.split in ("all", "train"):
        process_split("train", TRAIN_SPLIT, args.max_videos)
    if args.split in ("all", "val"):
        process_split("val", VAL_SPLIT, args.max_videos)
    if args.split in ("all", "test"):
        process_split("test", TEST_SPLIT, args.max_videos)


if __name__ == "__main__":
    main()
