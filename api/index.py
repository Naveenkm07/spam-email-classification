from __future__ import annotations

# Vercel Serverless Function entrypoint for Flask
# Exposes a Flask app instance named `app`
from app import create_app

app = create_app()
