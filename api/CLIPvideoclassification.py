import os
import glob
from collections import Counter
from tqdm import tqdm
from PIL import Image
import torch
import clip
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from torch.utils.data import DataLoader, Dataset
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

# Main function
if __name__ == "__main__":
    # Step 1: Load topics
    topics_file = "data/topics.txt"  # Updated relative path to topics.txt
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

    # Paths for training and validation
    train_dir = "data/UCF101_frames/train"  # Path to training frames
    val_dir = "data/UCF101_frames/val"      # Path to validation frames

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
