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
import clip

from analyze_db import insert_analysis, get_analyses_for_user, get_analysis_detail
from clerk_auth import get_current_user_id

router = APIRouter()

# Load CLIP model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
clip_model, preprocess = clip.load("ViT-B/32", device=device)
clip_model.load_state_dict(torch.load("../fine_tuned_clip.pth", map_location=device))
clip_model.to(device)
clip_model.eval()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Your class names from training (UCF-101 example)
class_names = [
    "ApplyEyeMakeup", "Archery", "BabyCrawling", "BalanceBeam", "BandMarching",  # Extend with all your used classes
    "Basketball", "BenchPress", "Biking", "Billiards", "BlowDryHair",
    "BodyWeightSquats", "Bowling", "BoxingPunchingBag", "BreastStroke", "BrushingTeeth"
]

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
        # Save uploaded video
        logging.info("Saving uploaded video.")
        with open(temp_video_path, "wb") as f:
            f.write(await video.read())
        logging.info(f"Video saved to {temp_video_path}")

        # Extract frames
        logging.info(f"Extracting frames every {frame_interval} frames.")
        frames = extract_frames(temp_video_path, frame_interval)
        logging.info(f"Extracted {len(frames)} frames.")

        # Classify frames using CLIP
        logging.info("Classifying frames with CLIP model.")
        class_votes = []

        with torch.no_grad():
            text_inputs = torch.cat([clip.tokenize(f"a photo of a person doing {c}") for c in class_names]).to(device)
            text_features = clip_model.encode_text(text_inputs)

            for i, frame in enumerate(frames):
                image_input = preprocess(frame).unsqueeze(0).to(device)
                image_features = clip_model.encode_image(image_input)
                logits = (image_features @ text_features.T).softmax(dim=-1)
                top_class = logits.argmax().item()
                class_votes.append(class_names[top_class])

        # Determine most common class
        most_common_action = max(set(class_votes), key=class_votes.count)
        logging.info(f"Predicted action: {most_common_action}")

        # Extract audio from video
        logging.info("Extracting audio.")
        ffmpeg.input(temp_video_path).output(temp_audio_path).run(overwrite_output=True, quiet=True)
        logging.info(f"Audio saved to {temp_audio_path}")

        # Transcribe with Whisper
        logging.info("Transcribing audio with Whisper.")
        whisper_model = whisper.load_model("base")
        transcription_result = whisper_model.transcribe(temp_audio_path)
        transcription = transcription_result.get("text", "")
        logging.info("Transcription complete.")

        # Recognize music with Shazamio
        logging.info("Recognizing music.")
        shazam = Shazam()
        shazam_result = await shazam.recognize(temp_audio_path)
        music_info = shazam_result.get("track", {})
        logging.info("Music recognition complete.")

        # Prepare ChatGPT prompt
        logging.info("Preparing ChatGPT prompt.")  
        chatgpt_prompt = f"""Analyze the following transcription and music info:

Transcription: {transcription}

Music Info: {music_info}

Predicted Action: {most_common_action}
"""

        logging.info("Sending prompt to ChatGPT.")
        logging.info(f"ChatGPT Prompt:\n{chatgpt_prompt}")

        chat_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert video and music analyst, you gotta analyze the prompt and predict the virality of this video based of several factors and then give feedback on improvements that could be made."},
                {"role": "user", "content": chatgpt_prompt}
            ],
            max_tokens=500
        )

        chatgpt_text = chat_response.choices[0].message.content.strip()
        logging.info(f"ChatGPT Response:\n{chatgpt_text}")

        # Save result
        result = f"Predicted Action: {most_common_action}\n\nChatGPT says: {chatgpt_text}"
        today = datetime.today().date().isoformat()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_id = str(uuid.uuid4())

        insert_analysis(new_id, user_id, f"Analysis {today}", today, result, video.filename)

        return {
            "id": new_id,
            "title": f"Analysis {today}",
            "date": today,
            "result": result,
            "video_filename": video.filename,
            "date_time": current_datetime,
            "predicted_action": most_common_action,
            "transcription": transcription,
            "music_info": music_info,
            "chatgpt_response": chatgpt_text
        }

    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

def extract_frames(video_path, frame_interval=30):
    frames = []
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    success, image = cap.read()

    while success:
        if frame_count % frame_interval == 0:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            frames.append(pil_image)
        success, image = cap.read()
        frame_count += 1

    cap.release()
    return frames
