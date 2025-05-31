import ssl
import aiohttp
from shazamio import Shazam

# Bypass SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

async def recognize_audio_from_video(audio_path: str) -> dict:
    """
    Recognizes music in the given audio file using Shazam.
    
    Args:
        audio_path (str): Path to the audio file.
    
    Returns:
        dict: Recognition result from Shazam.
    """
    shazam = Shazam()
    result = await shazam.recognize(audio_path)
    return result

# Example usage for testing
if __name__ == "__main__":
    import asyncio

    async def main():
        # Replace with the path to your audio file
        path_to_audio = "/Users/otsoreijonen/Downloads/Rarin - YESSIR! (Official Visualizer).mp3"
        
        # Recognize the audio file
        try:
            out = await recognize_audio_from_video(path_to_audio)
            print(out)
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(main())