from fastapi import FastAPI
from .api import news  # Import the news router

app = FastAPI()

app.include_router(news.router)  # Include the news router in the app


@app.get("/")
async def root():
    """
    Root endpoint for the API.
    """
    return {"message": "News Ontology API - Backend is running!"}