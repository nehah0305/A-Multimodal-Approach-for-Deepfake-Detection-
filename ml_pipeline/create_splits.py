"""
Create leakage-safe train/val/test splits based on identity groups.
This ensures videos of the same person don't leak across splits.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from config import DATA_DIR, DATASET_MANIFEST, TRAIN_SPLIT, VAL_SPLIT, TEST_SPLIT, VALIDATION_SPLIT, TEST_SPLIT_RATIO

def create_splits():
    """Create identity-safe splits."""
    print("Creating leakage-safe train/val/test splits...")
    
    # Load manifest
    if not DATASET_MANIFEST.exists():
        print(f"Error: {DATASET_MANIFEST} not found. Run build_manifest.py first.")
        return
    
    manifest_df = pd.read_csv(DATASET_MANIFEST)
    print(f"Loaded manifest with {len(manifest_df)} videos")
    
    # Get unique identity groups
    identity_groups = manifest_df.groupby('identity_group')
    print(f"Total identity groups: {len(identity_groups)}")
    
    # First split: test set (10% of identities)
    identities = manifest_df['identity_group'].unique()
    train_identities, test_identities = train_test_split(
        identities,
        test_size=TEST_SPLIT_RATIO,
        random_state=42
    )
    print(f"Test identities: {len(test_identities)}")
    print(f"Train+Val identities: {len(train_identities)}")
    
    # Second split: train/val from remaining (15% val)
    train_identities, val_identities = train_test_split(
        train_identities,
        test_size=VALIDATION_SPLIT,
        random_state=42
    )
    print(f"Train identities: {len(train_identities)}")
    print(f"Val identities: {len(val_identities)}")
    
    # Assign videos to splits based on identity
    train_df = manifest_df[manifest_df['identity_group'].isin(train_identities)].copy()
    val_df = manifest_df[manifest_df['identity_group'].isin(val_identities)].copy()
    test_df = manifest_df[manifest_df['identity_group'].isin(test_identities)].copy()
    
    # Add split column
    train_df['split'] = 'train'
    val_df['split'] = 'val'
    test_df['split'] = 'test'
    
    # Save splits
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(TRAIN_SPLIT, index=False)
    val_df.to_csv(VAL_SPLIT, index=False)
    test_df.to_csv(TEST_SPLIT, index=False)
    
    print(f"\nSplit sizes:")
    print(f"  Train: {len(train_df)} videos ({len(train_df)/len(manifest_df)*100:.1f}%)")
    print(f"  Val:   {len(val_df)} videos ({len(val_df)/len(manifest_df)*100:.1f}%)")
    print(f"  Test:  {len(test_df)} videos ({len(test_df)/len(manifest_df)*100:.1f}%)")
    
    # Class distribution check
    print(f"\nClass distribution:")
    for split_name, split_df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        real = (split_df['label'] == 0).sum()
        fake = (split_df['label'] == 1).sum()
        print(f"  {split_name}: {real} REAL, {fake} FAKE (ratio: {real/fake:.2f})")
    
    # Save full split assignment for reference
    combined_df = pd.concat([train_df, val_df, test_df])
    combined_df.to_csv(DATA_DIR / "all_splits.csv", index=False)
    
    print(f"\nSplits saved to {DATA_DIR}/")

if __name__ == "__main__":
    create_splits()
