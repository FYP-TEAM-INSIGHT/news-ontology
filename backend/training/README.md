
# TRAINING NLP MODELS

## SINHALA POS MODELS

Here we can train and evaluate models for Sinhala Part-of-Speech (POS) tagging. The training process involves using annotated datasets to teach the model how to classify words into their respective parts of speech. Currently, we are using pre-processed data `data/sinhala_pos_data.csv` which contains sentences with their corresponding POS tags.

Then, we train the model using the `train_sinhala_pos_model.py` script. The training process will save the model to a specified directory (default is `app/data/sinhala_pos_model.joblib`), which can then be used for inference.

