import torch
import clip
from torchvision import transforms
from PIL import Image
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import seaborn as sns

# Define your class names
class_names = [
    "skateboarding", "guitar playing", "cooking", "playing piano", "soccer juggling",
    "basketball dunk", "yoga", "weightlifting", "running", "biking", "swimming", "surfing",
    "boxing", "dancing", "karate", "walking a dog", "fishing", "skiing", "snowboarding",
    "playing drums", "parkour", "typing on a keyboard", "playing violin", "jump rope", "tennis serve"
]

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device)
model.load_state_dict(torch.load("fine_tuned_clip.pth", map_location=device))
model.eval()

# Example: Load test images and labels
test_images = [...]  # List of PIL Images
true_labels = [...]  # List of class indices (0 to 24)

# Encode text once
text_inputs = torch.cat([clip.tokenize(f"a photo of a person doing {c}") for c in class_names]).to(device)
text_features = model.encode_text(text_inputs)

predicted_labels = []

with torch.no_grad():
    for image in test_images:
        image_input = preprocess(image).unsqueeze(0).to(device)
        image_features = model.encode_image(image_input)
        logits = (image_features @ text_features.T).softmax(dim=-1)
        pred = logits.argmax().item()
        predicted_labels.append(pred)

# Confusion Matrix
cm = confusion_matrix(true_labels, predicted_labels)
plt.figure(figsize=(14, 12))
sns.heatmap(cm, xticklabels=class_names, yticklabels=class_names, annot=True, fmt="d", cmap="Blues")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()
