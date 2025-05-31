import os
from collections import Counter
from tqdm import tqdm
from PIL import Image
import torch
import clip
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from torch.utils.data import DataLoader, Dataset

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