from fastapi import APIRouter, Depends
from clerk_auth import get_current_user_id 

router = APIRouter()

@router.get("/trends")
def get_trends(user_id: str = Depends(get_current_user_id)):
    """
    DUMMY DATA FOR TRENDS API
    """ 
    return [
        {
            "id": 1,
            "category": "Tech",
            "title": "AI Revolutionizes Coding",
            "image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c",
            "summary": "AI tools are changing how developers write code.",
            "details": "AI-powered code assistants are making development faster and more efficient by providing real-time suggestions and automating repetitive tasks.",
        },
        {
            "id": 2,
            "category": "Science",
            "title": "New Planet Discovered",
            "image": "https://images.unsplash.com/photo-1465101046530-73398c7f28ca",
            "summary": "Astronomers have found a new Earth-like planet.",
            "details": "The planet, located in the habitable zone, could potentially support life. Scientists are excited about future research opportunities.",
        },
        {
            "id": 3,
            "category": "Art",
            "title": "Modern Art Exhibition",
            "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
            "summary": "A new exhibition showcases modern art from around the world.",
            "details": "The exhibition features works from over 50 artists and explores themes of identity, technology, and society.",
        },
        {
            "id": 4,
            "category": "Sports",
            "title": "Championship Finals",
            "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b",
            "summary": "The finals were full of surprises and upsets.",
            "details": "Fans witnessed an intense battle as underdogs took the lead and secured a historic victory.",
        },
    ]