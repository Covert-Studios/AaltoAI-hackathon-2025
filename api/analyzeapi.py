from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
import uuid
import datetime
import os
import shazamioapi
import whisperstuff

from analyze_db import insert_analysis, get_analyses_for_user, get_analysis_detail
from clerk_auth import get_current_user_id

router = APIRouter()

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

        # Combine results
        result = {
            "shazam": shazam_result,
            "whisper": whisper_result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing video: {str(e)}")
    finally:
        # Clean up the temporary file
        os.remove(video_path)

    # Insert the analysis into the database
    today = datetime.date.today().isoformat()
    new_id = str(uuid.uuid4())
    insert_analysis(new_id, user_id, f"Analysis {today}", today, result, video.filename)

    return {
        "id": new_id,
        "title": f"Analysis {today}",
        "date": today,
        "result": result,
        "video_filename": video.filename
    }