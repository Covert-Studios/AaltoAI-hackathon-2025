from fastapi import APIRouter, Header, Depends
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import json
from clerk_auth import get_current_user_id

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

class NewsIdea(BaseModel):
    title: str
    description: str

class AIRequest(BaseModel):
    question: str

class AIResponse(BaseModel):
    reply: List[NewsIdea]

@router.post("/ai-news", response_model=AIResponse)
async def ai_news(
    req: AIRequest,
    user_id: str = Depends(get_current_user_id),
    authorization: Optional[str] = Header(None)
):
    try:
        prompt = (
            f"Give me 3 clickbait news ideas for: '{req.question}'. "
            "Respond ONLY as a JSON array of objects, each with 'title' and 'description' fields. "
            "Example: [{\"title\": \"Shocking AI Discovery!\", \"description\": \"Scientists reveal a new AI that writes clickbait.\"}]"
        )
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.8,
        )
        content = response.choices[0].message.content.strip()
        try:
            start = content.find('[')
            end = content.rfind(']')
            if start != -1 and end != -1:
                json_str = content[start:end+1]
                reply = json.loads(json_str)
            else:
                reply = []
            if not isinstance(reply, list) or not reply or not reply[0].get("title"):
                raise Exception("Bad format")
        except Exception:
            reply = [
                {"title": "Could not fetch ideas", "description": "Sorry, something went wrong with the AI."}
            ]
        return {"reply": reply}
    except Exception:
        return {"reply": [
            {"title": "Could not fetch ideas", "description": "Sorry, something went wrong with the AI."}
        ]}