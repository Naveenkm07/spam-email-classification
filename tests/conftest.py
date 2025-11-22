from __future__ import annotations

import os
from typing import Iterator

import pytest
from flask import Flask

from app import create_app
from app.extensions import db


@pytest.fixture()
def app() -> Iterator[Flask]:
    os.environ["FLASK_ENV"] = "testing"
    application = create_app()

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.drop_all()


@pytest.fixture()
def client(app: Flask):  # type: ignore[override]
    return app.test_client()
