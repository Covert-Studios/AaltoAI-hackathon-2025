from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid

router = APIRouter()

# Dummy in-memory storage for analysis history
analysis_history = [
    {
        "id": "1",
        "title": "First Analysis",
        "date": "2024-06-01",
        "result": "This is a dummy analysis result for the first video."
    },
    {
        "id": "2",
        "title": "Second Analysis",
        "date": "2024-06-02",
        "result": "This is a dummy analysis result for the second video."
    }
]

@router.get("/analyze/history")
def get_analyze_history():
    return analysis_history

@router.get("/analyze/{analysis_id}")
def get_analyze_detail(analysis_id: str):
    for item in analysis_history:
        if item["id"] == analysis_id:
            return item
    raise HTTPException(status_code=404, detail="Analysis not found")

@router.post("/analyze")
async def analyze_video(video: UploadFile = File(...)):
    
    new_id = str(uuid.uuid4())
    new_analysis = {
        "id": new_id,
        "title": f"Analysis {len(analysis_history) + 1}",
        "date": "2024-06-03",
        "result": f"Dummy analysis result for uploaded video: {video.filename}"
    }
    analysis_history.insert(0, new_analysis)
    return new_analysis