from flask import Flask, jsonify, request, abort
import subprocess
import os
from collections import Counter
from tqdm import tqdm
from PIL import Image
import torch
import clip
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from torch.utils.data import DataLoader, Dataset

app = Flask(__name__)

# Predefined API key
API_KEY = "prohackerschmacker6969"

# Decorator to require API key
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != API_KEY:
            abort(401, description="Unauthorized: Invalid API Key")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # Preserve function name for Flask
    return wrapper

def get_video(video):
    # get the users video 


@app.route('/date', methods=['GET'])
@require_api_key
def get_date():
    result = subprocess.check_output(['date']).decode('utf-8')
    return jsonify({'date': result.strip()})

@app.route('/cal', methods=['GET'])
@require_api_key
def get_cal():
    result = subprocess.check_output(['cal']).decode('utf-8')
    return jsonify({'calendar': result.strip()})

@app.route('/docker', methods=['GET'])
@require_api_key
def get_docker():
    result = subprocess.check_output(['docker', 'ps']).decode('utf-8')
    return jsonify({'docker': result.strip()})

@app.route('/cls', methods=['GET'])
@require_api_key
def get_cls():
    result = subprocess.check_output(['cls']).decode('utf-8')
    return jsonify({'cls': result.strip()})

@app.route('/upload', methods=['POST'])
@require_api_key
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the video to the uploads folder
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)

    # Log the received video
    print(f"[INFO] Received video: {video.filename}")
    print(f"[INFO] Saved to: {video_path}")

    return jsonify({"message": "Video uploaded successfully", "path": video_path}), 200

@app.route('/analyze', methods=['POST'])
@require_api_key
def analyze_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded video
    video_path = os.path.join("uploads", video.filename)
    os.makedirs("uploads", exist_ok=True)
    video.save(video_path)

    # Log the received video
    print(f"[INFO] Received video for analysis: {video.filename}")
    print(f"[INFO] Saved to: {video_path}")

    # Call the CLIP classification script
    frame_dir = "frames"
    os.makedirs(frame_dir, exist_ok=True)
    extract_frames(video_path, frame_dir, frame_interval=2)

    # Load topics and analyze frames
    topics_file = "data/topics.txt"
    topics = load_topics(topics_file)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    text_tokens = clip.tokenize(topics).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    results = analyze_frames(frame_dir, model, preprocess, text_features, topics, device)

    # Summarize results
    topics_detected = [topic for _, topic in results]
    summary = Counter(topics_detected).most_common()

    # Log the analysis summary
    print(f"[INFO] Analysis complete for: {video.filename}")
    print(f"[INFO] Summary: {summary}")

    return jsonify({"summary": summary})

# Custom dataset for loading frames
class FrameDataset(Dataset):
    def __init__(self, data_dir, preprocess):
        self.data_dir = data_dir
        self.preprocess = preprocess
        self.samples = []
        self.classes = sorted(os.listdir(data_dir))
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.classes)}

        for cls_name in self.classes:
            cls_path = os.path.join(data_dir, cls_name)
            for img_name in os.listdir(cls_path):
                self.samples.append((os.path.join(cls_path, img_name), self.class_to_idx[cls_name]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = self.preprocess(Image.open(img_path).convert("RGB"))
        return image, label

# Training function
def train_clip(model, dataloader, optimizer, loss_fn, device):
    model.train()
    total_loss = 0
    for images, labels in tqdm(dataloader, desc="Training"):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        logits_per_image, _ = model(images, None)
        loss = loss_fn(logits_per_image, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(dataloader)

# Validation function
def validate_clip(model, dataloader, loss_fn, device):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Validating"):
            images, labels = images.to(device), labels.to(device)
            logits_per_image, _ = model(images, None)
            loss = loss_fn(logits_per_image, labels)
            total_loss += loss.item()
            preds = logits_per_image.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    accuracy = correct / total
    return total_loss / len(dataloader), accuracy

if __name__ == "__main__":
    # Paths
    train_dir = "data/UCF101_frames/train"  # Path to training frames
    val_dir = "data/UCF101_frames/val"      # Path to validation frames

    # Load CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Prepare datasets and dataloaders
    train_dataset = FrameDataset(train_dir, preprocess)
    val_dataset = FrameDataset(val_dir, preprocess)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    # Define optimizer and loss function
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
    loss_fn = torch.nn.CrossEntropyLoss()

    # Training loop
    epochs = 5
    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")
        train_loss = train_clip(model, train_loader, optimizer, loss_fn, device)
        val_loss, val_accuracy = validate_clip(model, val_loader, loss_fn, device)
        print(f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, Val Accuracy: {val_accuracy:.4f}")

    # Save the fine-tuned model
    torch.save(model.state_dict(), "fine_tuned_clip.pth")
    print("Model saved as fine_tuned_clip.pth")