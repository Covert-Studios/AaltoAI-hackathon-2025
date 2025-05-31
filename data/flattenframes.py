import os
import shutil
from pathlib import Path

SOURCE_DIR = Path("data/frames")
DEST_DIR = Path("data/prepared_frames")
DEST_DIR.mkdir(parents=True, exist_ok=True)

for class_dir in SOURCE_DIR.iterdir():
    if not class_dir.is_dir():
        continue

    dest_class_dir = DEST_DIR / class_dir.name
    dest_class_dir.mkdir(parents=True, exist_ok=True)

    for video_subdir in class_dir.iterdir():
        if not video_subdir.is_dir():
            continue

        for frame_file in video_subdir.glob("*.jpg"):
            # Make unique filename to avoid overwriting
            new_filename = f"{video_subdir.name}_{frame_file.name}"
            new_path = dest_class_dir / new_filename
            shutil.copy(frame_file, new_path)

print("✅ All frames have been flattened into per-class folders.")
