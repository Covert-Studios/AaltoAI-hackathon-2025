import os
import cv2
from pathlib import Path

VIDEO_DIR = "data/youtube_clips"
OUTPUT_DIR = "data/frames"
FRAME_RATE = 1  # frames per second

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_frames_from_video(video_path, output_folder, frame_rate=1):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ Failed to open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(fps * frame_rate)

    count = 0
    saved = 0
    while True:
        success, frame = cap.read()
        if not success:
            break

        if count % interval == 0:
            frame_filename = output_folder / f"frame_{saved:03d}.jpg"
            cv2.imwrite(str(frame_filename), frame)
            saved += 1

        count += 1

    cap.release()

def process_all_videos():
    for label_dir in Path(VIDEO_DIR).iterdir():
        if not label_dir.is_dir():
            continue

        label = label_dir.name
        output_label_dir = Path(OUTPUT_DIR) / label
        output_label_dir.mkdir(parents=True, exist_ok=True)

        for video_file in label_dir.glob("*.mp4"):
            video_title = video_file.stem.replace(" ", "_").replace("/", "_")
            output_folder = output_label_dir / video_title
            output_folder.mkdir(parents=True, exist_ok=True)

            print(f"🎞️ Extracting from: {video_file.name}")
            extract_frames_from_video(video_file, output_folder, frame_rate=FRAME_RATE)

if __name__ == "__main__":
    process_all_videos()
