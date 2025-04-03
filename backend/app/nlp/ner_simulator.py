

def simulate_ner(text):
    """
    Simulates Named Entity Recognition (NER) on the input text.
    This is a placeholder and should be replaced with a real NER system later.
    """
    # Very basic keyword matching for demonstration
    entities = []
    text_lower = text.lower()
    if "joe biden" in text_lower:
        entities.append(("Joe Biden", "Person"))
    if "white house" in text_lower:
        entities.append(("White House", "Location"))
    if "ukraine" in text_lower:
        entities.append(("Ukraine", "Location"))
    # Add more rules as needed

    return entities