# % app/nlp/sinhala_pos_tagger.py %
import os
import joblib
from typing import List, Dict, Any
from sklearn.pipeline import Pipeline # For type hinting

# --- Configuration ---
# Path to the pre-trained model file within the app structure
# Assumes this script is in app/nlp/, so app/data/ is ../data/
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Should point to 'app'
MODEL_NAME = "sinhala_pos_model.joblib"
MODEL_PATH = os.path.join(APP_DIR, "data", MODEL_NAME)

# Global variable to hold the loaded pipeline
_pos_pipeline: Pipeline = None


# --- Feature extraction function ---
# This MUST be identical to the one used during training.
def features(sentence_tokens: List[str], index: int) -> Dict[str, Any]:
    word = sentence_tokens[index]
    is_capitalized = word[0].upper() == word[0] if word else False
    is_all_caps = word.upper() == word if word else False
    is_all_lower = word.lower() == word if word else False
    prefix_1 = word[0] if word else ""
    prefix_2 = word[:2] if len(word) >= 2 else ""
    prefix_3 = word[:3] if len(word) >= 3 else ""
    suffix_1 = word[-1] if word else ""
    suffix_2 = word[-2:] if len(word) >= 2 else ""
    suffix_3 = word[-3:] if len(word) >= 3 else ""
    capitals_inside = word[1:].lower() != word[1:] if len(word) > 1 else False

    return {
        "word": word,
        "is_first": index == 0,
        "is_last": index == len(sentence_tokens) - 1,
        "is_capitalized": is_capitalized,
        "is_all_caps": is_all_caps,
        "is_all_lower": is_all_lower,
        "prefix-1": prefix_1,
        "prefix-2": prefix_2,
        "prefix-3": prefix_3,
        "suffix-1": suffix_1,
        "suffix-2": suffix_2,
        "suffix-3": suffix_3,
        "prev_word": "" if index == 0 else sentence_tokens[index - 1],
        "next_word": (
            ""
            if index == len(sentence_tokens) - 1
            else sentence_tokens[index + 1]
        ),
        "has_hyphen": "-" in word,
        "is_numeric": word.isdigit(),
        "capitals_inside": capitals_inside,
    }


def load_pos_model():
    """Loads the Sinhala POS tagger model into the global _pos_pipeline."""
    global _pos_pipeline
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Sinhala POS model file not found at {MODEL_PATH}")
        print("Ensure the model is trained and placed in app/data/ directory.")
        _pos_pipeline = None # Explicitly set to None if not found
        return False
    try:
        _pos_pipeline = joblib.load(MODEL_PATH)
        print(f"Sinhala POS Tagger model loaded successfully from {MODEL_PATH}.")
        return True
    except Exception as e:
        print(f"Error loading Sinhala POS Tagger model: {e}")
        _pos_pipeline = None
        return False

def get_pos_model() -> Pipeline:
    """Returns the loaded POS pipeline. Raises RuntimeError if not loaded."""
    if _pos_pipeline is None:
        # This check is important. The lifespan manager should ensure it's loaded.
        raise RuntimeError(
            "Sinhala POS Tagger model is not loaded. Check server startup logs."
        )
    return _pos_pipeline

def tag_sinhala_sentence(text: str) -> List[Dict[str, str]]:
    """
    Tags a Sinhala sentence using the pre-loaded POS tagger.
    Returns a list of dictionaries, e.g., [{'word': 'මම', 'tag': 'PRP'}]
    """
    pipeline = get_pos_model() # This will raise an error if model not loaded

    # Tokenize (using simple split as per your original script)
    # For production, a more robust Sinhala tokenizer might be better.
    tokens = text.split()
    if not tokens:
        return []

    try:
        # Generate features for each token in the sentence
        sentence_features = [features(tokens, i) for i in range(len(tokens))]
        # Predict tags using the loaded pipeline
        predicted_tags = pipeline.predict(sentence_features)
        # Combine tokens with their predicted tags
        return [
            {"word": word, "tag": tag}
            for word, tag in zip(tokens, predicted_tags)
        ]
    except Exception as e:
        print(f"Error during POS tagging prediction: {e}")
        # Depending on desired behavior, could return empty or raise a specific error
        return [] # Return empty list on prediction error for now