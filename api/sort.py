import os
import shutil
from pathlib import Path

def restructure_split(split_path):
    """
    Moves video clip folders into class-named subfolders.
    Example: v_TennisSwing_g14_c03 → TennisSwing/v_TennisSwing_g14_c03
    """
    split_path = Path(split_path)
    for item in split_path.iterdir():
        if item.is_dir() and item.name.startswith("v_") and "_g" in item.name:
            # Extract class name
            try:
                class_name = item.name.split("_g")[0].replace("v_", "")
                class_dir = split_path / class_name
                class_dir.mkdir(exist_ok=True)
                shutil.move(str(item), class_dir / item.name)
            except Exception as e:
                print(f"Failed to move {item}: {e}")

if __name__ == "__main__":
    train_path = "data/UCF101_frames/train"
    val_path = "data/UCF101_frames/val"

    print("Restructuring training set...")
    restructure_split(train_path)
    print("Restructuring validation set...")
    restructure_split(val_path)

    print("✅ Done restructuring!")
