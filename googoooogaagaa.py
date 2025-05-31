import os
import shutil

train_path = "data/UCF101_frames/train"
nested_path = os.path.join(train_path, "BrushingTeeth")

if os.path.exists(nested_path):
    for folder in os.listdir(nested_path):
        src = os.path.join(nested_path, folder)
        dst = os.path.join(train_path, folder)
        shutil.move(src, dst)
    os.rmdir(nested_path)
    print("✅ Moved class folders out of 'BrushingTeeth' and cleaned up.")
else:
    print("No nested 'BrushingTeeth' folder found.")
