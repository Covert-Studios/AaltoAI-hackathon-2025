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
import clip  # Import CLIP library

router = APIRouter()

# Load the CLIP model and preprocessing pipeline
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
clip_model, preprocess = clip.load("ViT-B/32", device=device)  # Load the model architecture and preprocessing
clip_model.load_state_dict(torch.load("../fine_tuned_clip.pth", map_location=device))  # Load your fine-tuned weights
clip_model.to(device)
clip_model.eval()

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
    try:
        # Save the uploaded video
        temp_video_path = f"/tmp/{uuid.uuid4()}.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(await video.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")

    # Extract frames from the video (you already have an `extract_frames` function)
    frames = extract_frames(temp_video_path)

    # Process frames with CLIP
    results = []
    batch_size = 16
    for i in range(0, len(frames), batch_size):
        batch = frames[i:i + batch_size]
        images = torch.stack([preprocess(frame) for frame in batch]).to(device)
        with torch.no_grad():
            image_features = clip_model.encode_image(images)
        results.extend(image_features.cpu().numpy())

    # Clean up the temporary file
    os.remove(temp_video_path)

    return {"features": results}

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