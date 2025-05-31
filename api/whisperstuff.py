import whisper
import ssl

# Bypass SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

# Load the Whisper model globally to avoid reloading for every request
model = whisper.load_model("base")  # Use "base" or another valid model name

def whisper_transcribe(audio_path: str) -> str:
    """
    Transcribes the audio file at the given path using Whisper.
    
    Args:
        audio_path (str): Path to the audio file.
    
    Returns:
        str: Transcribed text from the audio.
    """
    result = model.transcribe(audio_path)
    return result["text"]