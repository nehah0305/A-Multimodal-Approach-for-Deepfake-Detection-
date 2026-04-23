# ML Pipeline - Getting Started

Follow these steps **in order** to prepare your dataset for training.

## Step 1: Install ML Dependencies

First, add these packages to your environment:

```bash
pip install torch torchvision opencv-python scikit-learn pandas matplotlib seaborn tensorboard
```

Or run:
```bash
pip install -r requirements_ml.txt
```

## Step 2: Build the Dataset Manifest

This creates a single CSV with all videos and metadata:

```bash
cd ml_pipeline
python build_manifest.py
```

**Output:**
- `data/dataset_manifest.csv` - All videos with labels, identity groups, and properties
- Prints total video count, class distribution, and manipulation types

**Expected output example:**
```
Total videos: 1000
Real videos: 500
Fake videos: 500

Manipulation type distribution:
original           500
Face2Face          100
FaceSwap           100
...
```

## Step 3: Create Leakage-Safe Splits

This ensures no person appears in multiple splits (train/val/test):

```bash
python create_splits.py
```

**Output:**
- `data/train_split.csv` - 75% of identity groups
- `data/val_split.csv` - 10% of identity groups
- `data/test_split.csv` - 15% of identity groups
- `data/all_splits.csv` - Combined reference

**Key feature:** Splitting by identity prevents data leakage

## Step 4: Validate Your Dataset

Check if all files exist and report statistics:

```bash
python validate_dataset.py
```

**Output:**
- Total dataset size in GB
- Missing files count
- Resolution distribution
- Frame count statistics

## Next Steps After Validation

Now run the training pipeline in this order:

### 1) Preprocess videos into tensors

```bash
python preprocess_videos.py --split all
```

This creates:
- `data/train_preprocessed.csv`
- `data/val_preprocessed.csv`
- `data/test_preprocessed.csv`
- frame tensors under `preprocessed/train`, `preprocessed/val`, `preprocessed/test`

Quick sanity run (small subset):

```bash
python preprocess_videos.py --split train --max-videos 50
python preprocess_videos.py --split val --max-videos 20
python preprocess_videos.py --split test --max-videos 20
```

### 2) Train baseline model

```bash
python train_baseline.py
```

Artifacts:
- `models/best_baseline.pt`
- `models/train_history.json`

### 3) Evaluate on held-out test set

```bash
python evaluate_model.py
```

Artifacts:
- `models/test_metrics.json`

### 4) Predict one video (manual check)

```bash
python predict_video.py "path/to/video.mp4"
```

## File Structure

```
ml_pipeline/
├── config.py                 # Configuration (paths, hyperparams)
├── build_manifest.py         # Create unified dataset manifest
├── create_splits.py          # Identity-safe train/val/test split
├── validate_dataset.py       # Check dataset integrity
├── data/                     # Generated CSVs (splits + preprocessed manifests)
├── preprocessed/             # Will store preprocessed frames
├── models/                   # Will store trained checkpoints
└── logs/                     # Training logs
```

## Key Configuration Values

Edit `config.py` to adjust:
- `FRAME_SAMPLING_FPS` - Frames per second to extract (default: 8)
- `FRAME_SIZE` - Input size for model (default: 384x384)
- `BATCH_SIZE` - Training batch size (default: 16)
- `LEARNING_RATE` - Optimizer LR (default: 1e-4)
- `CONFIDENCE_THRESHOLD` - Decision threshold (default: 0.5)

## Troubleshooting

- **"dataset_manifest.csv not found"**: Run `python build_manifest.py` first
- **"original/000.mp4 not found"**: Check `DATASET_ROOT` path in config.py
- **Missing files in validation**: Some videos may not have downloaded completely, that's OK
