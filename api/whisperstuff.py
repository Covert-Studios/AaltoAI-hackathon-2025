import whisper
import ssl

# Bypass SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

# Load the Whisper model
model = whisper.load_model("base")  # Use "base" or another valid model name
result = model.transcribe("/Users/otsoreijonen/Downloads/audio_file.mp3")  # Replace with the actual audio file path
print(result["text"])