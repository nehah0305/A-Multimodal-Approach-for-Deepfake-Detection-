"""
Validate FaceForensics++ dataset integrity and report statistics.
"""

import pandas as pd
from pathlib import Path
from config import DATASET_MANIFEST, DATA_DIR, DATASET_ROOT

def validate_dataset():
    """Check dataset files and report statistics."""
    print("Validating FaceForensics++ dataset...\n")
    
    # Build manifest if not exists
    if not DATASET_MANIFEST.exists():
        print("Building manifest first...")
        from build_manifest import build_manifest
        manifest_df = build_manifest()
    else:
        manifest_df = pd.read_csv(DATASET_MANIFEST)
    
    print("\n=== Dataset Statistics ===")
    print(f"Total videos: {len(manifest_df)}")
    print(f"\nBy manipulation type:")
    print(manifest_df['manipulation_type'].value_counts().to_string())
    
    print(f"\nBy label:")
    print(manifest_df['label_name'].value_counts().to_string())
    
    print(f"\n=== File Validation ===")
    missing_files = []
    total_size_gb = 0
    
    for idx, row in manifest_df.iterrows():
        video_path = Path(row['video_path'])
        if not video_path.exists():
            missing_files.append(row['relative_path'])
        else:
            total_size_gb += video_path.stat().st_size / (1024 ** 3)
        
        if (idx + 1) % 100 == 0:
            print(f"  Checked {idx + 1}/{len(manifest_df)} files...")
    
    print(f"\nTotal dataset size: {total_size_gb:.2f} GB")
    print(f"Missing files: {len(missing_files)}")
    
    if missing_files:
        print("\nFirst 10 missing files:")
        for f in missing_files[:10]:
            print(f"  - {f}")
    
    print(f"\n=== Video Properties ===")
    print(f"Frame count - Min: {manifest_df['frame_count'].min()}, Max: {manifest_df['frame_count'].max()}, Mean: {manifest_df['frame_count'].mean():.0f}")
    print(f"Resolution distribution:")
    resolutions = manifest_df.groupby(lambda x: f"{manifest_df.loc[x, 'width']}x{manifest_df.loc[x, 'height']}").size()
    print(resolutions.sort_values(ascending=False).head(10).to_string())
    
    print(f"\nDataset validation complete!")

if __name__ == "__main__":
    validate_dataset()
