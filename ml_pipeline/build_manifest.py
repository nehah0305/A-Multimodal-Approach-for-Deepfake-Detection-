"""
Build unified dataset manifest from FaceForensics++ metadata CSVs.
This creates a single CSV with all videos, labels, and identity information for leakage-safe splitting.
"""

import pandas as pd
import re
from pathlib import Path
from config import DATASET_ROOT, DATA_DIR, DATASET_MANIFEST

def extract_identity(filepath: str) -> str:
    """Extract subject/identity ID from file path."""
    path = Path(filepath)
    filename = path.stem
    
    # For original videos: original/000 -> 000
    if "original" in filepath:
        return f"original_{filename}"
    
    # For manipulated videos: the first number is source, second is target
    # Face2Face/024_073 -> sources: 024, 073
    # FaceSwap/350_349 -> sources: 350, 349
    # Deepfakes/941_940 -> sources: 941, 940
    # Pattern: XXX_YYY
    match = re.search(r'(\d+)_(\d+)', filename)
    if match:
        source, target = match.groups()
        manipulation_type = path.parent.name
        # Return both source and target as a group key to prevent both appearing in train/test
        return f"{manipulation_type}_{source}_{target}"
    
    # Fallback
    return filepath

def build_manifest():
    """Build unified manifest from all FaceForensics++ CSVs."""
    print("Building unified dataset manifest...")
    
    records = []
    
    # Read all metadata CSVs
    csv_files = {
        "original": DATASET_ROOT / "csv" / "original.csv",
        "Deepfakes": DATASET_ROOT / "csv" / "Deepfakes.csv",
        "Face2Face": DATASET_ROOT / "csv" / "Face2Face.csv",
        "FaceSwap": DATASET_ROOT / "csv" / "FaceSwap.csv",
        "FaceShifter": DATASET_ROOT / "csv" / "FaceShifter.csv",
        "NeuralTextures": DATASET_ROOT / "csv" / "NeuralTextures.csv",
    }
    
    for source_type, csv_file in csv_files.items():
        if not csv_file.exists():
            print(f"Warning: {csv_file} not found, skipping.")
            continue
        
        print(f"  Reading {source_type}...")
        df = pd.read_csv(csv_file, index_col=0)
        
        for _, row in df.iterrows():
            video_path = row["File Path"]
            label = 0 if row["Label"] == "REAL" else 1
            identity = extract_identity(video_path)
            
            records.append({
                "video_path": str(DATASET_ROOT / video_path),
                "relative_path": video_path,
                "label": label,
                "label_name": "REAL" if label == 0 else "FAKE",
                "manipulation_type": source_type,
                "identity_group": identity,
                "frame_count": row.get("Frame Count", 0),
                "width": row.get("Width", 0),
                "height": row.get("Height", 0),
                "file_size_mb": row.get("File Size(MB)", 0),
            })
    
    manifest_df = pd.DataFrame(records)
    
    # Save manifest
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest_df.to_csv(DATASET_MANIFEST, index=False)
    
    print(f"\nManifest built: {DATASET_MANIFEST}")
    print(f"Total videos: {len(manifest_df)}")
    print(f"Real videos: {(manifest_df['label'] == 0).sum()}")
    print(f"Fake videos: {(manifest_df['label'] == 1).sum()}")
    print(f"\nManipulation type distribution:")
    print(manifest_df['manipulation_type'].value_counts())
    print(f"\nUnique identity groups: {manifest_df['identity_group'].nunique()}")
    
    return manifest_df

if __name__ == "__main__":
    build_manifest()
