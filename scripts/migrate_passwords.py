from __future__ import annotations

"""One-time migration script to bcrypt-hash existing plaintext passwords.

Usage:
    # Ensure DATABASE_URL in .env points to the target database
    python scripts/migrate_passwords.py

The script is idempotent: rows whose password already looks like a bcrypt hash
(starting with "$2") are left unchanged.
"""

import os

from app import create_app
from app.extensions import db
from app.models import User
from app.security import hash_password, is_bcrypt_hash


def migrate_passwords() -> None:
    # Use the normal application configuration (DATABASE_URL, etc.)
    app = create_app()

    updated = 0
    total = 0

    with app.app_context():
        users = User.query.all()
        total = len(users)
        for user in users:
            if not is_bcrypt_hash(user.password):
                # Treat existing value as plaintext and re-hash it
                user.password = hash_password(user.password or "")
                updated += 1
        if updated:
            db.session.commit()

    print(f"Users scanned: {total}")
    print(f"Passwords updated to bcrypt hashes: {updated}")


if __name__ == "__main__":  # pragma: no cover
    # Ensure we are not accidentally running in testing mode
    os.environ.setdefault("FLASK_ENV", "production")
    migrate_passwords()
