# Spam Email Classification (Secure Refactor)

Secure, testable Flask application for classifying emails as spam or not spam.

This project is a **security-focused refactor** of an email spam classifier. It uses:

- Flask app factory and SQLAlchemy ORM
- Bcrypt password hashing (no plaintext passwords)
- CSRF-protected forms (Flask-WTF)
- Environment-based configuration (no hard-coded secrets)
- Server-side validation for auth and prediction
- Pytest test suite and static-analysis configs (flake8, black, mypy)

## Quick start

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt  # optional, dev tools

# Copy your trained model/vectorizer files next to this README
# (see ASSUMPTIONS.md for details)

cp /path/to/model.pkl ./model.pkl
cp /path/to/vectorizer.pkl ./vectorizer.pkl

# Create .env from template and edit values
cp .env.example .env

# Initialize database
python -c "from app import create_app; from app.extensions import db; app = create_app();\nfrom app import models;\nwith app.app_context(): db.create_all()"

# Run the app
python run.py
```

## Tests

```bash
pytest
```

## Security details

See `README_SECURITY.md` for a full description of hardening measures, how to run tests, and how to run the password-migration script.
