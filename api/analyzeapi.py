from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import uuid
import os
import torch
import logging
from torchvision import transforms
from PIL import Image
import cv2
import openai
import tempfile
import ffmpeg
from shazamio import Shazam
import whisper
from datetime import datetime
import clip
import re
import json

from analyze_db import insert_analysis, get_analyses_for_user, get_analysis_detail
from clerk_auth import get_current_user_id

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Initializing analyzeapi.py")

# Load CLIP model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f"Using device: {device}")

# Check model path
model_path = "../fine_tuned_clip.pth"
if not os.path.exists(model_path):
    logging.error(f"Model path not found: {model_path}")
    raise FileNotFoundError(f"Model file not found at {model_path}")

try:
    clip_model, preprocess = clip.load("ViT-B/32", device=device)
    logging.info("Original CLIP model loaded.")
    clip_model.load_state_dict(torch.load(model_path, map_location=device))
    clip_model.to(device)
    clip_model.eval()
    logging.info("Fine-tuned CLIP weights loaded and model set to eval mode.")
except Exception as e:
    logging.error(f"Failed to load CLIP model or weights: {e}")
    raise e

# Check OpenAI key
if not os.getenv("OPENAI_API_KEY"):
    logging.error("OPENAI_API_KEY is not set in environment.")
    raise EnvironmentError("OPENAI_API_KEY environment variable is not configured.")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Class names
class_names = [
    "skateboarding", "guitar playing", "cooking", "playing piano", "soccer juggling",
    "basketball dunk", "yoga", "weightlifting", "running", "biking", "swimming", "surfing",
    "boxing", "dancing", "karate", "walking a dog", "fishing", "skiing", "snowboarding",
    "playing drums", "parkour", "typing on a keyboard", "playing violin", "jump rope", "tennis serve"
]

@router.get("/analyze/history")
def get_analyze_history(user_id: str = Depends(get_current_user_id)):
    logging.info("GET /analyze/history called.")
    return get_analyses_for_user(user_id)

@router.get("/analyze/{analysis_id}")
def get_analyze_detail_endpoint(analysis_id: str, user_id: str = Depends(get_current_user_id)):
    logging.info(f"GET /analyze/{analysis_id} called.")
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
    logging.info("POST /analyze called.")
    temp_dir = tempfile.gettempdir()
    temp_video_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")
    temp_audio_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp3")

    try:
        logging.info("Saving uploaded video to temporary directory.")
        with open(temp_video_path, "wb") as f:
            f.write(await video.read())
        logging.info(f"Video saved to: {temp_video_path}")

        logging.info(f"Extracting frames every {frame_interval} frames.")
        frames = extract_frames(temp_video_path, frame_interval)
        logging.info(f"Extracted {len(frames)} frames.")

        if not frames:
            raise HTTPException(status_code=400, detail="No frames extracted from video.")

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
                predicted_label = class_names[top_class]
                class_votes.append(predicted_label)
                logging.info(f"Frame {i} predicted as: {predicted_label}")

        most_common_action = max(set(class_votes), key=class_votes.count)
        logging.info(f"Predicted action: {most_common_action}")

        logging.info("Extracting audio from video.")
        ffmpeg.input(temp_video_path).output(temp_audio_path).run(overwrite_output=True, quiet=True)
        logging.info(f"Audio extracted to: {temp_audio_path}")

        logging.info("Transcribing audio with Whisper.")
        whisper_model = whisper.load_model("base")
        transcription_result = whisper_model.transcribe(temp_audio_path)
        transcription = transcription_result.get("text", "")
        logging.info(f"Transcription: {transcription if transcription else 'None'}")

        logging.info("Recognizing music with Shazamio.")
        shazam = Shazam()
        shazam_result = await shazam.recognize(temp_audio_path)
        music_info = shazam_result.get("track", {})
        logging.info(f"Music recognition: {music_info if music_info else 'No track info found'}")

        chatgpt_prompt = f"""
You are an expert video and music analyst. Analyze the following video content for virality and improvement potential.
The data of the video: 

Transcription: {transcription if transcription else "None"},
Music Info: {music_info if music_info else "No track info found"},
Most Common Action: {most_common_action if most_common_action else "None"}.
Video Frames: {len(frames)} frames extracted.
Filename: {video.filename}.

Determine the topic of the video based on all that information.
Add a score from 0 to 100 based on the following factors:
However, don't base the videos center solely on the most common action, but rather on the overall content and context of the video.
Give a score based on the following factors:
1. **Music**: Is there a recognizable or trending song? How does it fit the video?
2. **Transcription:** What is the spoken content? Does it add value or context?
3. **Platform Accessibility:** Is the content suitable for platforms like TikTok, Instagram, or YouTube Shorts?
4. **Visual Appeal & Social Sharing:** How engaging are the visuals? Are they high quality?

Suggest improvements to increase the video's virality based on these factors as a list.
give it in JSON format with the following structure:
{{
    "score": "<integer from 0 to 100>",
    "explanation": "<string explaining the score and suggestions for improvement>"
}}
"""

        logging.info("Sending prompt to ChatGPT.")
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        chat_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert video and music analyst. Analyze the prompt and predict the virality of this video based on several factors, then offer improvements."},
                {"role": "user", "content": chatgpt_prompt},
            ],
            max_tokens=700
        )
        chatgpt_text = chat_response.choices[0].message.content.strip()
        logging.info(f"ChatGPT Response: {chatgpt_text}")

        # Parse JSON from GPT response
        try:
            chatgpt_text_clean = re.sub(r"^```json|^```|```$", "", chatgpt_text, flags=re.MULTILINE).strip()
            gpt_result = json.loads(chatgpt_text_clean)
            score = int(gpt_result.get("score", 0))
            explanation = gpt_result.get("explanation", "")
        except Exception as e:
            logging.error(f"Failed to parse GPT response as JSON: {e}")
            score = 0
            explanation = chatgpt_text

        today = datetime.now().strftime("%Y-%m-%d")
        new_id = str(uuid.uuid4())

        insert_analysis(new_id, user_id, f"Analysis {today}", today, explanation, video.filename)
        logging.info(f"Inserted analysis ID {new_id} for user {user_id}")

        return {
            "id": new_id,
            "title": f"Analysis {today}",
            "date": today,
            "result": explanation,
            "video_filename": video.filename,
            "predicted_action": most_common_action,
            "transcription": transcription,
            "music_info": music_info,
            "score": score,
        }

    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
            logging.info(f"Removed temporary video: {temp_video_path}")
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            logging.info(f"Removed temporary audio: {temp_audio_path}")

def extract_frames(video_path, frame_interval=30):
    logging.info("extract_frames function called.")
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
    logging.info("Frames extraction complete.")
    return frames
