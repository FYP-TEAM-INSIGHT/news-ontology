# % app/main.py %
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

# Import your existing routers and the new one
from app.api import health_router, news_router, nlp_processing_router # Adjusted imports

# Import the POS tagger model loader function
from app.nlp.sinhala_pos_tagger import load_pos_model

# Import ontology
from .core import ontology_manager

# --- NLTK Resource Download (Optional, if features ever need it) ---
# (You can include the NLTK download logic here if your 'features' function
#  ever evolves to use NLTK-specific resources like 'punkt' for tokenization)
# import nltk
# nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
# ... (rest of NLTK download logic if needed)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting up...")
    # download_nltk_resources() # Call if you implement NLTK downloads

    # Load the Sinhala POS Tagger model
    if load_pos_model(): # This function is from app.nlp.sinhala_pos_tagger
        print("Sinhala POS Tagger model initialized successfully during startup.")
    else:
        print("CRITICAL: Failed to initialize Sinhala POS Tagger model during startup.")
        # You might want to raise an error here to prevent the app from starting
        # if this model is absolutely critical for all operations.
        # For now, it will print an error, and endpoints using it will fail.
    yield
    print("Server shutting down...")

app = FastAPI(
    title="Sinhala NLP and News API", # Or your preferred title
    description="API for news processing and Sinhala NLP tasks including POS tagging.",
    version="1.0.0", # Or your app version
    lifespan=lifespan
)

# Include your API routers
app.include_router(health_router, prefix="/api/v1", tags=["System Health"])
app.include_router(news_router, prefix="/api/v1/news", tags=["News"]) # Example
app.include_router(nlp_processing_router, prefix="/api/v1/nlp", tags=["NLP Processing"])


@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Welcome to the Sinhala NLP and News API!",
        "documentation": "/docs"
    }

# To run (from project root, assuming uvicorn is installed):
# uvicorn app.main:app --reload