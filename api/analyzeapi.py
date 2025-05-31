from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
import uuid
import datetime
import os
import shazamioapi
import whisperstuff
import torch
from torchvision import transforms
from PIL import Image
import cv2  # For frame extraction
import openai

from analyze_db import insert_analysis, get_analyses_for_user, get_analysis_detail
from clerk_auth import get_current_user_id
from my_clip_model import MyCLIPModel  # Import your model class

router = APIRouter()

# Load the fine-tuned CLIP model globally
clip_model_path = "../fine_tuned_clip.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
clip_model = MyCLIPModel()  # Instantiate the model
clip_model.load_state_dict(torch.load(clip_model_path, map_location=device))
clip_model.to(device)
clip_model.eval()

# Define preprocessing for CLIP
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])

# Load OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    user_id: str = Depends(get_current_user_id)
):
    # Save the uploaded video to a temporary file
    video_path = f"temp/{uuid.uuid4()}_{video.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(video_path, "wb") as f:
        f.write(await video.read())

    try:
        # Analyze the audio using Shazam
        shazam_result = await shazamioapi.recognize_audio_from_video(video_path)

        # Analyze the audio using Whisper
        whisper_result = whisperstuff.whisper_transcribe(video_path)

        # Extract frames from the video
        frames = extract_frames(video_path)

        # Analyze frames using the fine-tuned CLIP model
        clip_results = []
        for frame in frames:
            image = preprocess(frame).unsqueeze(0).to(device)
            with torch.no_grad():
                clip_output = clip_model(image)
            clip_results.append(clip_output.cpu().numpy().tolist())

        # Combine results
        result = {
            "shazam": shazam_result,
            "whisper": whisper_result,
            "clip": clip_results,
        }

        # Query ChatGPT for virality prediction and content suggestions
        chatgpt_prompt = f"""
        Based on the following data:
        - Song: {shazam_result.get('track', 'Unknown')} by {shazam_result.get('artist', 'Unknown')}
        - Transcription: {whisper_result}
        - Video Classification: {clip_results}

        1. Predict the virality of this content and explain why.
        2. Suggest trending content ideas that align with current popular topics.
        """
        chatgpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a content analysis expert."},
                {"role": "user", "content": chatgpt_prompt}
            ]
        )
        chatgpt_result = chatgpt_response['choices'][0]['message']['content']

        # Add ChatGPT results to the final result
        result["chatgpt"] = chatgpt_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing video: {str(e)}")
    finally:
        # Clean up the temporary file
        os.remove(video_path)

    # Insert the analysis into the database
    today = datetime.date.today().isoformat()
    new_id = str(uuid.uuid4())
    insert_analysis(new_id, user_id, f"Analysis {today}", today, result, video.filename)

    # Return the full result, including ChatGPT output
    return {
        "id": new_id,
        "title": f"Analysis {today}",
        "date": today,
        "result": result,
        "video_filename": video.filename,
        "chatgpt_result": chatgpt_result  # Include ChatGPT result directly in the response
    }

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
            # Convert the frame (BGR to RGB) and append as PIL Image
            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame))
        success, image = video.read()
        frame_count += 1

    video.release()
    return frames