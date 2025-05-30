import whisper
import torch

model = whisper.load_model("turbo")
result = model.transcribe("/Users/otsoreijonen/Downloads")
print(result["text"])