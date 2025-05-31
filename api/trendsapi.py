import requests
from fastapi import APIRouter, Depends, HTTPException
from clerk_auth import get_current_user_id 
import os
import logging
import openai
from datetime import datetime, timedelta
import re
import json

router = APIRouter()

NEWSAPI_KEY = os.getenv("NEWSAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOAD_COUNT = 5

def categorize_articles_with_gpt(articles):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    # Prepare the prompt
    prompt = (
        "Categorize the following news articles into one of these categories: Tech, Science, Art, Sports.\n"
        "Return a JSON array with objects containing: id, category, title, summary, details, image.\n"
        "Here are the articles:\n"
    )
    for idx, article in enumerate(articles, 1):
        prompt += f"{idx}. Title: {article['title']}\nSummary: {article['description']}\nImage: {article['image']}\n\n"
    prompt += (
        "Respond ONLY with the JSON array, no explanation. Always include the image URL in the 'image' field."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        # Remove markdown code block markers if present
        if content.startswith("```"):
            content = content.split('\n', 1)[1]
            if content.endswith("```"):
                content = content.rsplit('\n', 1)[0]
        # Extract the first JSON array from the response
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            content = match.group(0)
        else:
            raise ValueError("No JSON array found in GPT response")
        return json.loads(content)
    except Exception as e:
        logging.exception("Failed to categorize articles with GPT")
        raise HTTPException(status_code=500, detail=f"Failed to categorize articles: {e}")

def fetch_trends_from_newsapi():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize={LOAD_COUNT}"
    headers = {"Authorization": NEWSAPI_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error("NewsAPI error: %s", response.text)
        raise HTTPException(status_code=500, detail="Failed to fetch news trends")
    articles = response.json().get("articles", [])
    prepared_articles = []
    for idx, article in enumerate(articles, 1):
        prepared_articles.append({
            "id": idx,
            "title": article.get("title"),
            "description": article.get("description"),
            "details": article.get("content"),
            "image": article.get("urlToImage"),
        })
    return categorize_articles_with_gpt(prepared_articles)

@router.get("/trends")
def get_trends(user_id: str = Depends(get_current_user_id)):
    return fetch_trends_from_newsapi()

@router.get("/trend-growth")
async def trend_growth(id: int):
    # Fetch the latest articles
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=50"
    headers = {"Authorization": NEWSAPI_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error("NewsAPI error: %s", response.text)
        raise HTTPException(status_code=500, detail="Failed to fetch news trends")
    articles = response.json().get("articles", [])

    if id < 1 or id > len(articles):
        raise HTTPException(status_code=404, detail="Article not found")
    target_article = articles[id - 1]
    title = target_article.get("title", "")

    now = datetime.utcnow()
    buckets = [0, 0, 0, 0, 0]  # 5 days
    for art in articles:
        pub = art.get("publishedAt")
        if not pub:
            continue
        try:
            pub_dt = datetime.strptime(pub, "%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            continue
        days_ago = (now - pub_dt).days
        if 0 <= days_ago < 5:
            if any(word.lower() in art.get("title", "").lower() for word in title.split() if len(word) > 3):
                buckets[4 - days_ago] += 1

    return {"growth": buckets}
