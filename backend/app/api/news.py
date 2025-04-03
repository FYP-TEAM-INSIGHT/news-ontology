from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class NewsItem(BaseModel):
    text: str  # Temporary: Just receiving a text string for now


@router.post("/news/")
async def process_news(news_item: NewsItem):
    """
    Endpoint to receive news data (for now, just a text string) and print it.
    Will eventually process the news data and interact with the ontology.
    """
    try:
        print(f"Received news: {news_item.text}")  # Print to check if it works
        return {"message": "News received and printed to console (backend)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))