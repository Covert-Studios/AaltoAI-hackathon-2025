import os
import cv2
from tqdm import tqdm

def extract_frames_from_ucf101(input_dir, output_dir, frame_interval=10):
    os.makedirs(output_dir, exist_ok=True)
    classes = os.listdir(input_dir)

    for class_name in tqdm(classes, desc="Processing classes"):
        class_path = os.path.join(input_dir, class_name)
        output_class_dir = os.path.join(output_dir, class_name)
        os.makedirs(output_class_dir, exist_ok=True)

        for video_name in os.listdir(class_path):
            video_path = os.path.join(class_path, video_name)
            video_output_dir = os.path.join(output_class_dir, os.path.splitext(video_name)[0])
            os.makedirs(video_output_dir, exist_ok=True)

            video = cv2.VideoCapture(video_path)
            frame_count = 0
            success, frame = video.read()

            while success:
                if frame_count % frame_interval == 0:
                    frame_path = os.path.join(video_output_dir, f"frame_{frame_count:04d}.jpg")
                    cv2.imwrite(frame_path, frame)
                success, frame = video.read()
                frame_count += 1

            video.release()

if __name__ == "__main__":
    input_dir = "/Users/otsoreijonen/Documents/AaltoAI-hackathon-2025/data/UCF-101"  # Correct path to the UCF101 dataset
    output_dir = "/Users/otsoreijonen/Documents/AaltoAI-hackathon-2025/data/UCF101_frames"  # Path to save extracted frames
    extract_frames_from_ucf101(input_dir, output_dir, frame_interval=10)