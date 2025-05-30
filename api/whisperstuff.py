import whisper
import ssl

import os
path = "/Users/otsoreijonen/Downloads/ttsMP3.com_VoiceText_2025-5-30_19-44-40.mp3"
print("File exists")

# Bypass SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

# Load the Whisper model
model = whisper.load_model("base")  # Use "base" or another valid model name
result = model.transcribe("/Users/otsoreijonen/Downloads/ttsMP3.com_VoiceText_2025-5-30_19-44-40.mp3")

 # Replace with the actual audio file path
print(result["text"])