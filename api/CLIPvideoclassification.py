import os
import glob
from collections import Counter
from tqdm import tqdm
from PIL import Image
import torch
import clip
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
import cv2

# Step 1: Load topics from topics.txt
def load_topics(file_path):
    with open(file_path, "r") as file:
        topics = [line.strip() for line in file if line.strip() and not line.startswith("#")]
    return topics

# Step 2: Extract frames from video
def extract_frames(video_path, output_dir, frame_interval=2):
    os.makedirs(output_dir, exist_ok=True)
    video = cv2.VideoCapture(video_path)
    frame_count = 0
    success, frame = video.read()

    while success:
        if frame_count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
        success, frame = video.read()
        frame_count += 1

    video.release()

# Step 3: Analyze frames
def analyze_frames(frame_dir, model, preprocess, text_features, topics, device):
    frame_paths = sorted(glob.glob(f"{frame_dir}/*.jpg"))
    results = []

    for frame_path in tqdm(frame_paths, desc="Analyzing frames"):
        image = preprocess(Image.open(frame_path)).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            similarity = (100.0 * image_features @ text_features.T).squeeze()

        best_topic = topics[similarity.argmax().item()]
        results.append((frame_path, best_topic))

    return results

# Main function
if __name__ == "__main__":
    # Step 1: Load topics
    topics_file = "topics.txt"  # Path to your topics.txt file
    topics = load_topics(topics_file)
    print(f"Loaded {len(topics)} topics:")
    for topic in topics:
        print(topic)

    # Step 2: Load CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    text_tokens = clip.tokenize(topics).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    # Step 3: Extract frames and analyze them
    video_path = "/Users/otsoreijonen/Downloads/Theyre my favorite  #carsales #carsalesman #cardealership #dealership.mp4"
    frame_dir = "frames"
    extract_frames(video_path, frame_dir, frame_interval=2)
    results = analyze_frames(frame_dir, model, preprocess, text_features, topics, device)

    # Step 4: Summarize results
    topics_detected = [topic for _, topic in results]
    summary = Counter(topics_detected).most_common()

    # Step 5: Print summary
    print("\nSummary of detected topics:")
    for topic, count in summary:
        print(f"{topic}: {count}")
