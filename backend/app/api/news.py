from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core import ontology_manager
from ..nlp import ner_simulator

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
        # === Simulate NER output using the ner_simulator module ===
        simulated_entities = ner_simulator.simulate_ner(news_item.text)

        # Add the news item to the ontology
        article = ontology_manager.add_news_to_ontology(ontology_manager.onto, news_item.dict(), simulated_entities)

        if article:
            print(f"Saved to data {article.name}")
            return {"message": "News received and added to the ontology."}
        else:
            raise HTTPException(status_code=500, detail="Failed to add news to ontology.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))