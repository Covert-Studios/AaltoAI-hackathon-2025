import os
import shutil
from pathlib import Path

INPUT_DIR = Path("data/frames")
OUTPUT_DIR = Path("data/prepared_frames")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

copied = 0
skipped = 0
failed = 0

print("🔁 Starting flattening process...\n")

copied_count = 0

for class_dir in INPUT_DIR.iterdir():
    if not class_dir.is_dir():
        continue

    for video_folder in class_dir.iterdir():
        if not video_folder.is_dir():
            continue

        for frame_file in video_folder.glob("*.jpg"):
            new_name = f"{class_dir.name}_{video_folder.name}_{frame_file.name}"
            new_path = OUTPUT_DIR / class_dir.name / new_name
            new_path.parent.mkdir(parents=True, exist_ok=True)

            if new_path.exists():
                continue

            try:
                shutil.copy(frame_file, new_path)
                copied_count += 1
                if copied_count % 100 == 0:
                    print(f"✅ Copied {copied_count} frames...")
            except Exception as e:
                print(f"❌ Failed to copy {frame_file} — {e}")
