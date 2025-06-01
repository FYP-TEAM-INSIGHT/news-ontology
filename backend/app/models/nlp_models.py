# % app/models/nlp_models.py %
from pydantic import BaseModel, Field
from typing import List, Dict

class PosTaggingRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The Sinhala text to be tagged.")

class TaggedWord(BaseModel):
    word: str
    tag: str

class PosTaggingResponse(BaseModel):
    tagged_sentence: List[TaggedWord]
    model_version: str = Field(default="sinhala_pos_v1.0", description="Version of the POS tagging model used.")