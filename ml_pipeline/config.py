"""ML Pipeline Configuration"""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_ROOT = PROJECT_ROOT / "FaceForensic Dataset" / "FaceForensics++_C23"
PIPELINE_ROOT = PROJECT_ROOT / "ml_pipeline"

DATA_DIR = PIPELINE_ROOT / "data"
PREPROCESSED_DIR = PIPELINE_ROOT / "preprocessed"
MODELS_DIR = PIPELINE_ROOT / "models"
LOGS_DIR = PIPELINE_ROOT / "logs"

# Dataset
DATASET_MANIFEST = DATA_DIR / "dataset_manifest.csv"
TRAIN_SPLIT = DATA_DIR / "train_split.csv"
VAL_SPLIT = DATA_DIR / "val_split.csv"
TEST_SPLIT = DATA_DIR / "test_split.csv"

# Preprocessing
FRAME_SAMPLING_FPS = 8  # Sample 8 frames per second
FRAME_SIZE = (384, 384)  # Input size for model
BATCH_SIZE = 16
NUM_WORKERS = 4

# Training
EPOCHS = 50
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-5
VALIDATION_SPLIT = 0.15  # 15% of train for validation
TEST_SPLIT_RATIO = 0.1   # 10% for test

# Model
MODEL_BACKBONE = "resnet18"  # Options: resnet18, efficientnet_b0
NUM_CLASSES = 2
PRETRAINED = True

# Inference
CONFIDENCE_THRESHOLD = 0.5
MIN_FRAMES_TO_ANALYZE = 4

print(f"Dataset root: {DATASET_ROOT}")
print(f"Pipeline root: {PIPELINE_ROOT}")
