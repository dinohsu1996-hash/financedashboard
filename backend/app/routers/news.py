from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.ai_functions import scrape_and_summarize, get_gemini_client

router = APIRouter()

class NewsRequest(BaseModel):
    urls: List[str]
    topic: str

@router.post("/news")
def get_news_summary(request: NewsRequest):
    client = get_gemini_client()
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client not initialized")

    summary = scrape_and_summarize(request.urls, request.topic, client)
    return summary
