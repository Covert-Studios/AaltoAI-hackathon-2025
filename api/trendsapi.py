from fastapi import APIRouter, Depends, HTTPException
from clerk_auth import get_current_user_id 
import openai
import os
import json
import logging

router = APIRouter()

LOAD_COUNT = 5

def fetch_trends_from_gpt():
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = (
        f"List {LOAD_COUNT} current trending topics in the world right now. "
        "For each, provide: category (Tech, Science, Art, Sports, etc.), "
        "title, summary, and a short detail. Respond ONLY with a valid JSON array with keys: "
        "id, category, title, summary, details. No explanation or extra text. Example:\n"
        '[{"id": 1, "category": "Tech", "title": "...", "summary": "...", "details": "..."}, ...]'
    )
    try:
        logging.info("Sending prompt to OpenAI: %s", prompt)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()
        logging.info("GPT response: %s", content)
        if content.startswith("```"):
            content = content.split('\n', 1)[1]
            if content.endswith("```"):
                content = content.rsplit('\n', 1)[0]
        try:
            trends = json.loads(content)
        except json.JSONDecodeError as jde:
            logging.error("JSON decode error: %s", jde)
            logging.error("Raw GPT response: %s", content)
            raise HTTPException(status_code=500, detail=f"Invalid JSON from GPT: {content}")
        return trends
    except Exception as e:
        logging.exception("Failed to fetch trends from GPT")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {e}")

@router.get("/trends")
def get_trends(user_id: str = Depends(get_current_user_id)):
    return fetch_trends_from_gpt()
