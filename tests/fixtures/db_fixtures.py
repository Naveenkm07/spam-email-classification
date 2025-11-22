from __future__ import annotations

from app.extensions import db
from app.models import User


def create_user(
    full_name: str = "Test User",
    username: str = "testuser",
    email: str = "test@example.com",
    phone: str = "1234567890",
    password: str = "Password123",
) -> User:
    """Create and persist a User instance for tests."""

    user = User(
        full_name=full_name,
        username=username,
        email=email,
        phone=phone,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
