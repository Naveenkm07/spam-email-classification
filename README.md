# Spam Email Classification (Secure Refactor)

![New Horizon College of Engineering Logo](assets/new-horizon-college-of-engineering-logo.png)

Secure, accessible Flask application that classifies emails as spam or not‑spam with a production‑ready API, robust tests, Docker support, and a modern, responsive UI.

— Built as an academic Mini Project with a focus on end‑to‑end quality: security, ML pipeline rigor, developer experience, and deployment readiness.

## Highlights

- Authentication with bcrypt, CSRF protection, server‑side validations
- ML pipeline (scikit‑learn) with training, evaluation, and a JSON API
- Real‑time classify UI (debounced) with confidence bar and theme toggle
- Accessibility improvements (labels, live regions, keyboard support)
- Dockerized dev stack + GitHub Actions CI (tests + coverage)
- Vercel serverless deployment support

## Demo endpoints (local)

- Web app: `http://127.0.0.1:5000/`
- JSON API: `POST http://127.0.0.1:5000/api/predict`

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"Congratulations! You won a free prize!"}' \
  http://127.0.0.1:5000/api/predict
```

Response

```json
{
  "prediction": "spam | ham",
  "probability": 0.92,
  "model_version": "v1.0"
}
```

## Project structure

```
Spam-Email-Classification/
├─ app/                  # Flask app (factory, routes, forms, models)
├─ ml/                   # Pipeline, train/evaluate scripts, quick_test
├─ tests/                # Pytest suite + fixtures
├─ docker/               # MySQL init scripts for Docker
├─ app/static/           # JS + CSS (theme, validation, realtime predict)
├─ app/templates/        # Jinja templates (accessible, responsive)
├─ api/index.py          # Vercel serverless entry (Flask app)
├─ vercel.json           # Vercel routing + env defaults
├─ requirements.txt      # Runtime dependencies
└─ README_SECURITY.md    # Hardening details
```

## Quick start (local dev)

```bash
python -m venv .venv
. .venv/Scripts/activate  # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env      # set FLASK_SECRET_KEY, DATABASE_URL etc.

# Initialize the SQLite DB (or point DATABASE_URL to your DB)
python -c "from app import create_app; from app.extensions import db; app = create_app();\nfrom app import models;\nwith app.app_context(): db.create_all()"

python run.py  # visit http://127.0.0.1:5000/
```

## Docker (full stack)

```bash
docker compose up --build
# App: http://localhost:8000
# Adminer: http://localhost:8080
```

## Training the model

1. Place dataset at `data/spam_dataset.csv` with columns `text,label`.
2. Train:

```bash
python ml/train.py
```

Artifacts:

- `model/model.pkl` (full pipeline)
- `model/metadata.json` (version, metrics)
- `reports/report_v1.0.json` (evaluation)

Quick local smoke test:

```bash
python ml/quick_test.py
```

## API usage

Endpoint: `POST /api/predict`

Request

```json
{ "text": "your email content here" }
```

Success

```json
{ "prediction": "spam|ham", "probability": 0.73, "model_version": "v1.0" }
```

Errors

- 400 if `text` is missing/empty/too long
- 503 if the model pipeline is not yet provisioned on the server

## Deployment (Vercel)

This repo includes `api/index.py` (Flask app) and `vercel.json`.

1. Push to GitHub and import the repo in Vercel
2. In Vercel → Project → Settings → Environment Variables, set:
   - `FLASK_SECRET_KEY` = a long random value
   - `DATABASE_URL` = `sqlite:////tmp/spam_classifier.db` (demo) or a managed DB URL
3. Deploy

Notes:

- SQLite on serverless is ephemeral; prefer a managed DB in production.
- The HTML `/predict` page has a built‑in fallback (no model files needed).
- The JSON `/api/predict` returns a 503 if the model pipeline is missing.

## Accessibility & UX

- Skip‑to‑content link, labeled nav, proper landmarks
- Client‑side validation (HTML5) with server‑side enforcement
- Live region + progress bar for real‑time prediction feedback
- Theme toggle (dark/light) persisted in `localStorage`

## Testing

```bash
pytest
# Coverage threshold enforced at 75% (actual ~80% in CI)
```

## Configuration

Key env vars (see `.env.example`):

- `FLASK_SECRET_KEY`
- `DATABASE_URL` (SQLite/MySQL/Postgres)
- `MODEL_DIR` (where `model.pkl` & `metadata.json` live; defaults to project root)

## Credits (Institution & Course)

- Institution: **New Horizon College of Engineering** — Department of Computer Science & Engineering
- Course: **Mini Project‑II** (Course Code: **22CSE58**), **Semester V**
- Duration: **Sep 2025 – Dec 2025**

Contributors:

- USN: **1NH23CS65** — Name: **KEERTHIKA.CH** — Section: **B**
- USN: **1NH23CS108** — Name: **NEHA SREE K** — Section: **B**

---

See `README_SECURITY.md` for a deeper dive into the app’s security posture, password hashing, CSRF protections, and operational hardening.
