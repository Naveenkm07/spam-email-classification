#!/usr/bin/env sh
set -e

echo "[entrypoint] Starting container..."

# Default FLASK_ENV to production if not set
if [ -z "$FLASK_ENV" ]; then
  export FLASK_ENV=production
fi

echo "[entrypoint] Running database migrations (db.create_all)..."
python - << 'PYCODE'
from app import create_app
from app.extensions import db
from app import models  # noqa: F401

app = create_app()
with app.app_context():
    db.create_all()
PYCODE

if [ -f "scripts/migrate_passwords.py" ]; then
  echo "[entrypoint] Running password migration script (if needed)..."
  python scripts/migrate_passwords.py || echo "[entrypoint] Password migration script failed or not needed."
fi

echo "[entrypoint] Starting gunicorn on 0.0.0.0:8000..."
exec gunicorn -b 0.0.0.0:8000 wsgi:app
