import clip
import torch
from PIL import Image
import cv2
import os
import glob
from collections import Counter
from tqdm import tqdm  # Optional but helpful

# Load CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Step 1: Extract frames
def extract_frames(video_path, output_dir, frame_interval=2):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    count = 0
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if int(cap.get(1)) % int(fps * frame_interval) == 0:
            frame_path = os.path.join(output_dir, f"frame{saved:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            saved += 1
        count += 1

    cap.release()
    return saved

# Step 2: Define topics
topics = [
    "a football match", "a basketball game", "a baseball game", "a cooking show",
    "a nature documentary", "a person giving a lecture", "a music concert",
    "a workout video", "a wedding", "a person running", "a dog playing",
    "a news broadcast", "a haunted house", "a sword fight", "a cosplay event"
]

text_tokens = clip.tokenize(topics).to(device)
with torch.no_grad():
    text_features = model.encode_text(text_tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

# Step 3: Analyze frames
def analyze_frames(frame_dir):
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

# Step 4: Run everything
extract_frames("my_video.mp4", "frames", frame_interval=2)
results = analyze_frames("frames")
topics_detected = [topic for _, topic in results]
summary = Counter(topics_detected).most_common()

# Step 5: Print summary
print("🔍 Video Topic Summary:")
for topic, count in summary:
    print(f"{topic}: {count} frames")
