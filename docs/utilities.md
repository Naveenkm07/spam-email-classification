# Utilities Documentation (`scripts/`)

This document explains the standalone utility scripts used for maintaining the application and converting models.

---

## 1. `scripts/convert_to_onnx.py`

This script converts a trained scikit-learn model pipeline (a `.pkl` file) into an Open Neural Network Exchange (`.onnx`) format. Using ONNX allows the Flask backend to run fast inference without requiring the heavy `scikit-learn` dependency.

### Code Sections:

- **Path Definitions:** Uses `pathlib.Path` to locate the `model/` directory and the specific `model/v1.0/` version directory.
- **`convert()`:**
  - **Loading:** Attempts to find `model.pkl` in the version directory, falling back to the root `model/` directory. Loads it using Python's `pickle.load`.
  - **Extraction (Crucial Step):** The original scikit-learn pipeline (created in `ml/pipeline.py`) contains a `FunctionTransformer` to apply custom Python preprocessing. The ONNX standard, and the `skl2onnx` library, cannot export arbitrary Python code into the ONNX graph. Therefore, this script extracts *only* the `TfidfVectorizer` (`tfidf`) and `LogisticRegression` (`clf`) steps from the loaded pipeline.
  - **Re-assembly:** Creates a `new_pipe` containing only the compatible steps.
  - **ONNX Configuration:**
    - Defines the `initial_type` as a `StringTensorType` expecting string arrays.
    - Sets an important option: `{id(new_pipe): {'zipmap': False}}`. For `TfidfVectorizer` to preserve token patterns and output probabilities in a format `onnxruntime` can easily parse as an array (rather than a list of dictionaries mapping class to probability), `zipmap` is often disabled.
  - **Conversion:** Calls `to_onnx()` to generate the ONNX graph.
  - **Saving:** Serializes the ONNX graph to a file (`.SerializeToString()`) and writes it to `model/v1.0/model.onnx`.
  - **Copying:** Duplicates the newly created `.onnx` file into the root `model/` directory to act as the current active model.

---

## 2. `scripts/migrate_passwords.py`

A one-off, idempotent database utility script designed to upgrade user accounts from older plaintext passwords to secure bcrypt hashes.

### Code Sections:

- **Imports:** Imports the `create_app` factory and database models.
- **`migrate_passwords()`:**
  - **Initialization:** Calls `create_app()` to ensure all application configuration (like the Database URI) is loaded correctly.
  - **Context:** Enters the application context (`with app.app_context():`) so SQLAlchemy can connect to the database.
  - **Iteration:** Queries all `User` records.
  - **Validation & Hashing:**
    - For each user, it calls `is_bcrypt_hash(user.password)` (from `app.security`).
    - If the password is NOT a valid bcrypt hash, it treats it as a plaintext string, hashes it using `hash_password`, and assigns the hash back to `user.password`.
  - **Committing:** After iterating, if any records were modified (`updated > 0`), it calls `db.session.commit()` to persist the changes.
  - **Reporting:** Prints a summary of the total users scanned and how many were migrated.
- **Execution Guard:** The `if __name__ == "__main__":` block sets the `FLASK_ENV` environment variable to `"production"` before running, ensuring it doesn't accidentally run against an in-memory testing database unless specifically configured otherwise.
