from __future__ import annotations

from datetime import datetime

from .extensions import db
from .security import hash_password, verify_password


class User(db.Model):
    """User model storing bcrypt password hashes (no plaintext)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, raw_password: str) -> None:
        self.password = hash_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return verify_password(raw_password, self.password)
