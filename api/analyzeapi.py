from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import uuid
import os
import torch
from torchvision import transforms
from PIL import Image
import cv2
import openai
import logging
import tempfile
import ffmpeg
from shazamio import Shazam
import whisper
from datetime import datetime

from analyze_db import insert_analysis, get_analyses_for_user, get_analysis_detail
from clerk_auth import get_current_user_id
import clip

router = APIRouter()

# Load the CLIP model and preprocessing pipeline
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
clip_model, preprocess = clip.load("ViT-B/32", device=device)
clip_model.load_state_dict(torch.load("../fine_tuned_clip.pth", map_location=device))
clip_model.to(device)
clip_model.eval()

# Load OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@router.get("/analyze/history")
def get_analyze_history(user_id: str = Depends(get_current_user_id)):
    return get_analyses_for_user(user_id)

@router.get("/analyze/{analysis_id}")
def get_analyze_detail_endpoint(analysis_id: str, user_id: str = Depends(get_current_user_id)):
    detail = get_analysis_detail(user_id, analysis_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return detail

@router.post("/analyze")
async def analyze_video(
    video: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    frame_interval: int = 30
):
    temp_dir = tempfile.gettempdir()
    temp_video_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")
    temp_audio_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp3")
    try:
        # Save the uploaded video
        logging.info("Saving the uploaded video to a temporary file.")
        with open(temp_video_path, "wb") as f:
            f.write(await video.read())
        logging.info(f"Video saved to {temp_video_path}.")

        # Extract frames from the video
        logging.info(f"Extracting frames from the video with frame_interval={frame_interval}.")
        frames = extract_frames(temp_video_path, frame_interval=frame_interval)
        logging.info(f"Extracted {len(frames)} frames from the video.")

        # Process frames with CLIP
        logging.info("Processing frames with the CLIP model.")
        frame_results = []
        for i, frame in enumerate(frames):
            logging.debug(f"Processing frame {i + 1}/{len(frames)}.")
            image = preprocess(frame).unsqueeze(0).to(device)
            with torch.no_grad():
                image_features = clip_model.encode_image(image)
            frame_results.append(image_features.cpu().numpy().tolist())

        # Extract audio from the video
        logging.info("Extracting audio from the video.")
        ffmpeg.input(temp_video_path).output(temp_audio_path).run(overwrite_output=True, quiet=True)
        logging.info(f"Audio extracted to {temp_audio_path}.")

        # Transcribe audio with Whisper
        logging.info("Transcribing audio with Whisper.")
        whisper_model = whisper.load_model("base")
        transcription_result = whisper_model.transcribe(temp_audio_path)
        transcription = transcription_result.get("text", "")
        logging.info("Audio transcription completed.")

        # Recognize music with Shazamio (use recognize, not recognize_song)
        logging.info("Recognizing music with Shazamio.")
        shazam = Shazam()
        shazam_result = await shazam.recognize(temp_audio_path)
        music_info = shazam_result.get("track", {})
        logging.info("Music recognition completed.")

        # Generate ChatGPT response using openai>=1.0.0 API
        logging.info("Generating ChatGPT response.")
        chatgpt_prompt = f"Analyze the following transcription and music info:\n\nTranscription: {transcription}\n\nMusic Info: {music_info}"
        chat_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert video and music analyst."},
                {"role": "user", "content": chatgpt_prompt}
            ],
            max_tokens=500
        )
        chatgpt_text = chat_response.choices[0].message.content.strip()
        logging.info("ChatGPT response generated.")
        logging.info(f"ChatGPT Response: {chatgpt_text}")

        # Get the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.today().date().isoformat()
        result = f"ChatGPT's shit: {chatgpt_text}"

        # Save analysis to DB
        new_id = str(uuid.uuid4())
        try:
            insert_analysis(new_id, user_id, f"Analysis {today}", today, result, video.filename)
        except Exception as e:
            logging.error(f"Error occurred during DB insert: {str(e)}")

        # Return structured results
        return {
            "id": new_id,
            "title": f"Analysis {today}",
            "date": today,
            "result": result,
            "video_filename": video.filename,
            "date_time": current_datetime,
            "frames": {"features": frame_results, "frame_count": len(frames)},
            "transcription": transcription,
            "music_info": music_info,
            "chatgpt_response": chatgpt_text,
        }

    except Exception as e:
        logging.error(f"Error occurred during video analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze video: {str(e)}")

    finally:
        # Clean up temporary files
        if os.path.exists(temp_video_path):
            logging.info(f"Cleaning up temporary video file: {temp_video_path}.")
            os.remove(temp_video_path)
        if os.path.exists(temp_audio_path):
            logging.info(f"Cleaning up temporary audio file: {temp_audio_path}.")
            os.remove(temp_audio_path)

def extract_frames(video_path, frame_interval=30):
    """
    Extract frames from the video at the specified interval.
    Args:
        video_path (str): Path to the video file.
        frame_interval (int): Interval between frames to extract.
    Returns:
        List[PIL.Image]: List of extracted frames as PIL Images.
    """
    frames = []
    video = cv2.VideoCapture(video_path)
    frame_count = 0
    success, image = video.read()

    while success:
        if frame_count % frame_interval == 0:
            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame))
        success, image = video.read()
        frame_count += 1

    video.release()
    return frames