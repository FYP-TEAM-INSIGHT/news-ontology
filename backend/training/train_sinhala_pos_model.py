# % training/train_sinhala_pos_model.py %
import csv
import os
import joblib # For saving scikit-learn models
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline

# --- Configuration ---
# Get the directory where this script is located (training/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Project root is one level up from the script's directory
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Path to the training data CSV file, now in training/data/
# Relative to this script's location
TRAINING_DATA_SUBDIR = "data"
TRAINING_DATA_CSV_NAME = "poss_sentence.csv"
TRAINING_DATA_CSV_PATH = os.path.join(
    SCRIPT_DIR, TRAINING_DATA_SUBDIR, TRAINING_DATA_CSV_NAME
)

# Output path for the trained model (it will be saved inside app/data/)
# Relative to the PROJECT_ROOT
MODEL_OUTPUT_APP_SUBDIR = "app"
MODEL_OUTPUT_DATA_SUBDIR = "data"
MODEL_FILE_NAME = "sinhala_pos_model.joblib"
MODEL_OUTPUT_DIR = os.path.join(
    PROJECT_ROOT, MODEL_OUTPUT_APP_SUBDIR, MODEL_OUTPUT_DATA_SUBDIR
)
MODEL_OUTPUT_PATH = os.path.join(MODEL_OUTPUT_DIR, MODEL_FILE_NAME)


# --- Feature extraction and data transformation functions ---
# These MUST be identical to what your server will use for prediction.
def features(sentence_tokens, index):
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

def untag(tagged_sentence):
    return [w for w, t in tagged_sentence]

def transform_to_dataset(tagged_sentences_list):
    X, y = [], []
    for tagged_sentence in tagged_sentences_list:
        sentence_tokens = untag(tagged_sentence)
        for i in range(len(tagged_sentence)):
            X.append(features(sentence_tokens, i))
            y.append(tagged_sentence[i][1])
    return X, y

def main():
    print("Starting Sinhala POS model training...")
    print(f"Script directory: {SCRIPT_DIR}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Expecting training data at: {TRAINING_DATA_CSV_PATH}")
    print(f"Model will be saved to directory: {MODEL_OUTPUT_DIR}")


    if not os.path.exists(TRAINING_DATA_CSV_PATH):
        print(f"ERROR: Training data CSV file not found at: {TRAINING_DATA_CSV_PATH}")
        print(f"Please ensure '{TRAINING_DATA_CSV_NAME}' is in the '{os.path.join(SCRIPT_DIR, TRAINING_DATA_SUBDIR)}' directory.")
        return

    loaded_sentences = []
    try:
        with open(TRAINING_DATA_CSV_PATH, "r", encoding="utf-8") as f_csv:
            reader = csv.reader(f_csv)
            for i, row in enumerate(reader):
                if row:
                    new_row_tuples = []
                    for item_str in row:
                        try:
                            item_tuple = eval(item_str)
                            if isinstance(item_tuple, tuple) and len(item_tuple) == 2:
                                new_row_tuples.append(item_tuple)
                            else:
                                print(f"Warning: Malformed item in CSV (row {i+1}): {item_str}")
                        except Exception as e:
                            print(f"Warning: Could not parse item '{item_str}' (row {i+1}): {e}")
                    if new_row_tuples:
                        loaded_sentences.append(new_row_tuples)
    except Exception as e:
        print(f"An error occurred while reading {TRAINING_DATA_CSV_PATH}: {e}")
        return

    if not loaded_sentences:
        print("No sentences loaded from CSV. Cannot train model.")
        return

    print(f"Loaded {len(loaded_sentences)} sentences for training.")
    X_train, y_train = transform_to_dataset(loaded_sentences)

    if not X_train or not y_train:
        print("Feature extraction or label generation failed. No data to train on.")
        return

    print(f"Training model with {len(X_train)} samples...")
    pipeline = Pipeline(
        [
            ("vectorizer", DictVectorizer(sparse=True)),
            ("classifier", DecisionTreeClassifier(criterion="entropy")),
        ]
    )
    pipeline.fit(X_train, y_train)
    print("Model training complete.")

    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_OUTPUT_PATH)
    print(f"Trained Sinhala POS model saved to: {MODEL_OUTPUT_PATH}")
    print("This model will be used by your FastAPI application.")

if __name__ == "__main__":
    main()