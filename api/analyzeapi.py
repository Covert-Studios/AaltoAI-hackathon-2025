from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
import uuid
import datetime
import os

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
    # Save the uploaded video to disk
    save_dir = "videos"
    os.makedirs(save_dir, exist_ok=True)
    file_location = os.path.join(save_dir, video.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(await video.read())

    new_id = str(uuid.uuid4())
    today = datetime.date.today().isoformat()
    result = f"Saved uploaded video as: {file_location}"

    insert_analysis(new_id, user_id, f"Analysis {today}", today, result, video.filename)
    return {
        "id": new_id,
        "title": f"Analysis {today}",
        "date": today,
        "result": result,
        "video_filename": video.filename
    }