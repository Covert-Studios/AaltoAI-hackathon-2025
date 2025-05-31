import os
import cv2
import datetime
import os

root_dir = "data/youtube_clips"

for class_folder in os.listdir(root_dir):
    class_path = os.path.join(root_dir, class_folder)

    # Skip if it's not a directory
    if not os.path.isdir(class_path):
        continue

    for filename in os.listdir(class_path):
        if filename.endswith(".mp4"):
            file_path = os.path.join(class_path, filename)

            # Now do your check here (duration, size, etc.)
            data = cv2.VideoCapture(file_path)
            frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = data.get(cv2.CAP_PROP_FPS)

            seconds = round(frames / fps)
            video_time = datetime.timedelta(seconds=seconds)
            if seconds < 3:
                os.remove(file_path)
                print(f"Removed {file_path} due to short duration: {video_time}")
            else:
                file_size = os.path.getsize(file_path)
                #if file size is less than 500KB
                if file_size < 500 * 1024:
                    os.remove(file_path)
                    print(f"Removed {file_path} due to small file size: {file_size / 1024:.2f} KB")
            data.release()



