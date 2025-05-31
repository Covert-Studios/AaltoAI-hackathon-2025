import os
import shutil
import random
from pathlib import Path

SOURCE_DIR = Path("data/prepared_frames")
TRAIN_DIR = Path("data/split/train")
VAL_DIR = Path("data/split/val")
SPLIT_RATIO = 0.8  # 80% train, 20% val

# Make sure split folders exist
for folder in [TRAIN_DIR, VAL_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Get all images recursively
image_paths = list(SOURCE_DIR.rglob("*.jpg"))
print(f"🔍 Found {len(image_paths)} total images.")

random.shuffle(image_paths)
split_index = int(len(image_paths) * SPLIT_RATIO)

train_images = image_paths[:split_index]
val_images = image_paths[split_index:]

def copy_images(images, dest_dir):
    for img in images:
        label = img.parent.name  # Class name from folder
        target_dir = dest_dir / label
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / img.name
        shutil.copy(img, target_path)

copy_images(train_images, TRAIN_DIR)
copy_images(val_images, VAL_DIR)

print("✅ Splitting complete. Check 'data/split/train' and 'data/split/val'")
