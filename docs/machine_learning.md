# Machine Learning Pipeline (`ml/` and `model/`)

This document provides a detailed breakdown of the machine learning training pipeline, evaluation scripts, and the exported model artifacts.

---

## 1. `ml/pipeline.py` (Model Architecture)

Defines the scikit-learn pipeline structure for text classification.

### Code Sections:

- **Imports:** Imports `TfidfVectorizer`, `LogisticRegression`, `MultinomialNB`, `Pipeline`, and `FunctionTransformer`. It also imports the `transform_text` function from `app.spam` to ensure preprocessing is identical between training and production inference.
- **`_preprocess_texts(texts)`:** A wrapper function that applies `transform_text` to an entire list/sequence of strings. This is necessary because scikit-learn transformers expect iterables of data.
- **`build_pipeline(model_type, **classifier_kwargs)`:**
  - **Preprocessor:** Wraps `_preprocess_texts` in a `FunctionTransformer`.
  - **Vectorizer:** Instantiates a default `TfidfVectorizer`.
  - **Classifier:** Chooses between `MultinomialNB` and `LogisticRegression` (the default) based on the `model_type` argument.
  - **Pipeline construction:** Chains the three steps (`preprocess` -> `tfidf` -> `clf`) into a single `Pipeline` object and returns it.

---

## 2. `ml/train.py` (Training Script)

The primary script for training, tuning, and exporting the model.

### Code Sections:

- **`_load_dataset(path)`:**
  - Opens the CSV dataset (`data/spam_dataset.csv`).
  - Validates that the CSV contains `text` and `label` columns.
  - Iterates through the rows, mapping string labels (e.g., "spam", "true", "1") to the integer `1`, and all other labels ("ham", "0") to `0`.
  - Returns two lists: `texts` (features) and `labels` (targets).
- **`train()`:**
  - **Data Loading:** Calls `_load_dataset`.
  - **Splitting:** Uses `train_test_split` to create an 80/20 train/test split. `stratify=y` ensures the proportion of spam/ham remains consistent in both splits.
  - **Pipeline Instantiation:** Calls `build_pipeline("logreg")`.
  - **Hyperparameter Tuning:** Defines a `param_grid` (tuning n-grams, min_df, and regularization C). Runs `GridSearchCV` with 3-fold cross-validation, optimizing for the `f1` score.
  - **Evaluation:** Predicts labels (`y_pred`) and probabilities (`y_proba`) on the test set. Calculates precision, recall, f1, ROC AUC, and a confusion matrix.
  - **Directory Setup:** Ensures the target directories (`model/v1.0/`, `reports/`) exist.
  - **Exporting the Model:** Uses `pickle` to serialize the `best_pipeline` to `model/v1.0/model.pkl`.
  - **Exporting Metadata:** Creates a dictionary containing the version, timestamp, best hyperparameters, evaluation metrics, and label mappings. Saves this to `model/v1.0/metadata.json`.
  - **Updating the "Current" Model:** Copies the newly trained version into the root `model/` directory, overwriting the previous "latest" version.
  - **Reporting:** Writes a smaller summary JSON report to the `reports/` directory.

---

## 3. `ml/evaluate.py` (Evaluation Script)

A standalone script to evaluate an existing trained model without retraining.

### Code Sections:

- **`_load_dataset(path)`:** Reuses the dataset loading logic by importing `_load_dataset` directly from `ml.train`.
- **`evaluate()`:**
  - Loads the dataset.
  - Checks for the existence of `model/v1.0/model.pkl`.
  - Uses `pickle.load` to deserialize the pipeline.
  - Runs inference on the entire dataset.
  - Prints the confusion matrix, a detailed classification report, and the ROC AUC score to the console.

---

## 4. `ml/quick_test.py` (Sanity Check)

Provides a fast way to verify that the loaded model can process strings correctly.

### Code Sections:

- **`main()`:**
  - Checks for `model/model.pkl`.
  - Deserializes the model via `pickle`.
  - Defines a small list of hardcoded string `examples`.
  - Runs `predict` and `predict_proba`.
  - Iterates through the results, printing the text, the predicted integer label, and the probability array (ham probability, spam probability).

---

## 5. `model/` Directory (Exported Artifacts)

This directory is populated by the `ml/train.py` and `scripts/convert_to_onnx.py` scripts. It is read by the `app/spam.py` backend logic during production inference.

- **`model.pkl`:** The full scikit-learn pipeline object, serialized by Python's `pickle` library. This contains the custom `FunctionTransformer`, the fitted `TfidfVectorizer` vocabulary, and the trained `LogisticRegression` weights.
- **`model.onnx`:** An optimized, interoperable format of the model generated for faster inference using `onnxruntime`. *Note: The ONNX format lacks the custom `FunctionTransformer`, meaning preprocessing must be applied manually before passing data to the ONNX session.*
- **`metadata.json`:** Contains crucial contextual information about the model, including the version (`v1.0`), performance metrics on the test set, the parameters found by GridSearchCV, and the timestamp of creation.
- **`v1.0/`:** A snapshot directory containing the exact `.pkl`, `.onnx`, and `.json` artifacts generated for version 1.0, preserving them even if the root `model/` directory is updated with a newer version later.
