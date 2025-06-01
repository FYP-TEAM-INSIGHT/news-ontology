# % app/api/nlp_processing.py %
from fastapi import APIRouter, HTTPException, Depends
from app.models.nlp_models import PosTaggingRequest, PosTaggingResponse # Or adjust import path
from app.nlp.sinhala_pos_tagger import tag_sinhala_sentence, get_pos_model # Or adjust import
from sklearn.pipeline import Pipeline # For dependency type hint

router = APIRouter()

# Dependency to ensure the model is loaded and ready
def get_active_pos_model() -> Pipeline:
    try:
        return get_pos_model()
    except RuntimeError as e: # Catch if model wasn't loaded
        raise HTTPException(status_code=503, detail=str(e))


@router.post(
    "/pos-tag-sinhala",
    response_model=PosTaggingResponse,
    summary="Part-of-Speech Tagging for Sinhala Text",
    tags=["NLP Processing"],
)
async def pos_tag_text(
    request_body: PosTaggingRequest,
    # This dependency ensures that get_pos_model() doesn't raise RuntimeError
    # because the lifespan manager should have loaded it.
    # If not, this will raise a 503.
    model: Pipeline = Depends(get_active_pos_model)
):
    """
    Accepts a Sinhala text string and returns its Part-of-Speech (POS) tags.
    """
    if not request_body.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    try:
        tagged_words = tag_sinhala_sentence(request_body.text)
        return PosTaggingResponse(tagged_sentence=tagged_words)
    except Exception as e:
        # Log the exception for server-side debugging
        print(f"Unexpected error during POS tagging: {e}")
        raise HTTPException(
            status_code=500, detail="An internal error occurred during POS tagging."
        )