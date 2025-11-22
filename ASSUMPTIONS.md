# Assumptions

This document lists key assumptions made during the security & code-quality refactor.

## Application & database

- The **user table** is named `users` and has at least the following columns:
  - `id` (primary key)
  - `full_name` (string)
  - `username` (string, unique)
  - `email` (string, unique)
  - `phone` (string)
  - `password` (string) – now used to store **bcrypt hashes**, not plaintext.
- The new app is free to create this schema with SQLAlchemy if it does not already exist.
- Existing deployments can adapt their current `users` table to match these fields.

## Password migration

- Existing databases currently store **plaintext passwords** in the `users.password` column.
- The migration script `scripts/migrate_passwords.py`:
  - Connects to the database specified by `DATABASE_URL`.
  - Reads all `users` records.
  - Treats values that **do not start with `$2`** as plaintext and re-hashes them with bcrypt.
  - Leaves already-hashed passwords unchanged.
- No additional schema migrations (e.g., adding a new `password_hash` column) are performed; the existing `password` column is reused.

## Model files

- The ML artifacts `model.pkl` and `vectorizer.pkl` are **not** included in this new refactored repo.
- It is assumed you will:
  - Copy compatible `model.pkl` and `vectorizer.pkl` files into the project root (same directory as this file), or
  - Point `MODEL_DIR` (in `.env`) to the directory containing these files.
- The classifier expects a scikit-learn-compatible model and vectorizer with:
  - `.transform([...])` on the vectorizer
  - `.predict(vector)` on the model

## Environment & deployment

- Python 3.10+ is available.
- `DATABASE_URL` may point to SQLite (default), MySQL, or another SQLAlchemy-supported database.
- In production, you will:
  - Set a strong `FLASK_SECRET_KEY`.
  - Serve the app behind HTTPS so that `SESSION_COOKIE_SECURE=true` is effective.
- For local development and automated tests, SQLite is acceptable and is used by default.

## Testing

- Tests assume an **empty database** at startup; they create tables in an in-memory SQLite database.
- CSRF protection is disabled only in the test configuration (`TestingConfig`) to simplify form submissions in tests.
- The prediction tests use a **mock classifier** instead of loading real model files; this keeps tests fast and deterministic.

If any of these assumptions differ from your environment, you may need to adjust configuration or models accordingly.
