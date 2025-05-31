import os
import logging
from collections import Counter
from tqdm import tqdm
from PIL import Image
import torch
import clip
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from torch.utils.data import DataLoader, Dataset

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Custom dataset for loading frames
class FrameDataset(Dataset):
    def __init__(self, data_dir, preprocess, class_names):
        self.data_dir = data_dir
        self.preprocess = preprocess
        self.samples = []
        self.classes = class_names
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.classes)}

        for cls_name in self.classes:
            cls_path = os.path.join(data_dir, cls_name)
            if not os.path.exists(cls_path):
                logging.warning(f"Class directory not found: {cls_path}")
                continue
            for root, _, files in os.walk(cls_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        self.samples.append((os.path.join(root, file), self.class_to_idx[cls_name]))
        logging.info(f"Initialized FrameDataset with {len(self.samples)} samples from {data_dir}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        try:
            image = self.preprocess(Image.open(img_path).convert("RGB"))
        except Exception as e:
            logging.warning(f"Failed to load image {img_path}: {e}")
            return self.__getitem__((idx + 1) % len(self.samples))  # Skip to next image
        return image, label

# Training function
def train_clip(model, dataloader, optimizer, loss_fn, device, class_texts):
    model.train()
    total_loss = 0

    with torch.no_grad():
        text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}") for c in class_texts]).to(device)
        text_features = model.encode_text(text_inputs)

    for images, labels in tqdm(dataloader, desc="Training"):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()

        image_features = model.encode_image(images)
        logits_per_image = (image_features @ text_features.T)
        loss = loss_fn(logits_per_image, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    avg_loss = total_loss / len(dataloader)
    logging.info(f"Training Loss: {avg_loss:.4f}")
    return avg_loss

# Validation function
def validate_clip(model, dataloader, loss_fn, device, class_texts):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}") for c in class_texts]).to(device)
        text_features = model.encode_text(text_inputs)

    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Validating"):
            images, labels = images.to(device), labels.to(device)

            if labels.max() >= len(class_texts) or labels.min() < 0:
                logging.error(f"Invalid label detected. Labels must be in [0, {len(class_texts)-1}].")
                raise ValueError("Label out of range.")

            image_features = model.encode_image(images)
            logits_per_image = (image_features @ text_features.T)
            loss = loss_fn(logits_per_image, labels)
            total_loss += loss.item()

            preds = logits_per_image.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total
    avg_loss = total_loss / len(dataloader)
    logging.info(f"Validation Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")
    return avg_loss, accuracy

if __name__ == "__main__":
    # Paths (use your own data path here)
    train_dir = 'data/split/train'
    val_dir = 'data/split/val'



    # Load CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    logging.info(f"Using device: {device}")

    # Get common classes
    train_classes = set([d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d)) and not d.startswith('.')])
    val_classes = set([d for d in os.listdir(val_dir) if os.path.isdir(os.path.join(val_dir, d)) and not d.startswith('.')])

    common_classes = train_classes.intersection(val_classes)
    if not common_classes:
        logging.error("No common classes found between train and val sets.")
        raise ValueError("Check your data directories.")

    class_names = sorted(list(common_classes))
    logging.info(f"Using {len(class_names)} classes: {class_names}")

    # Datasets and loaders
    train_dataset = FrameDataset(train_dir, preprocess, class_names)
    val_dataset = FrameDataset(val_dir, preprocess, class_names)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
    loss_fn = torch.nn.CrossEntropyLoss()

    epochs = 2
    for epoch in range(epochs):
        logging.info(f"\nEpoch {epoch + 1}/{epochs}")
        train_loss = train_clip(model, train_loader, optimizer, loss_fn, device, class_names)
        val_loss, val_accuracy = validate_clip(model, val_loader, loss_fn, device, class_names)

    torch.save(model.state_dict(), "fine_tuned_clip.pth")
    logging.info("Model saved as fine_tuned_clip.pth")
