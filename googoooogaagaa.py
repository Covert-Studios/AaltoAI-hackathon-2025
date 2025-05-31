import os
import shutil

base_dir = "/Users/otsoreijonen/Documents/AaltoAI-hackathon-2025/data/UCF101_frames/val"


for action_class in os.listdir(base_dir):
    class_path = os.path.join(base_dir, action_class)

    if not os.path.isdir(class_path):
        continue

    for subfolder in os.listdir(class_path):
        subfolder_path = os.path.join(class_path, subfolder)

        if not os.path.isdir(subfolder_path):
            continue

        # Only go into folders starting with v_*
        if not subfolder.startswith("v_"):
            continue

        for filename in os.listdir(subfolder_path):
            src = os.path.join(subfolder_path, filename)
            dst = os.path.join(class_path, filename)

            # If file with same name exists, rename
            if os.path.exists(dst):
                name, ext = os.path.splitext(filename)
                i = 1
                while os.path.exists(dst):
                    dst = os.path.join(class_path, f"{name}_{i}{ext}")
                    i += 1

            shutil.move(src, dst)

        # Delete the empty v_* folder
        os.rmdir(subfolder_path)
        print(f"✅ Moved and removed: {subfolder_path}")
