import api.whisperstuff as whisperstuff
import torch

model = whisperstuff.load_model("turbo")
result = model.transcribe("/Users/otsoreijonen/Downloads")
print(result["text"])