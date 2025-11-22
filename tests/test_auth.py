from __future__ import annotations

from flask import Flask

from app.extensions import db
from app.models import User


def test_register_creates_user_with_hashed_password(client, app: Flask) -> None:  # type: ignore[override]
    response = client.post(
        "/signup",
        data={
            "full_name": "Test User",
            "username": "testuser",
            "email": "test@example.com",
            "phone": "1234567890",
            "password": "Password123",
            "confirm_password": "Password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None
        # Password should not be stored in plaintext
        assert user.password != "Password123"
        assert user.check_password("Password123")


def test_login_success_sets_session(client, app: Flask) -> None:  # type: ignore[override]
    with app.app_context():
        user = User(
            full_name="Login User",
            username="loginuser",
            email="login@example.com",
            phone="1234567890",
        )
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/signin",
        data={"email": "login@example.com", "password": "Password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Signed in successfully" in response.data


def test_login_invalid_credentials(client, app: Flask) -> None:  # type: ignore[override]
    with app.app_context():
        user = User(
            full_name="Other User",
            username="otheruser",
            email="other@example.com",
            phone="1234567890",
        )
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/signin",
        data={"email": "other@example.com", "password": "WrongPass"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data
