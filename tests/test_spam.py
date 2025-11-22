from __future__ import annotations

from app.spam import transform_text


def test_transform_text_basic() -> None:
    text = "Hello, WORLD!!! 123"
    transformed = transform_text(text)
    # Lowercased, punctuation removed, words stemmed, digits kept
    assert "hello" in transformed
    assert "world" in transformed
    assert "123" in transformed


def test_transform_text_removes_punctuation_only() -> None:
    text = "Spam???!!!"
    transformed = transform_text(text)
    # Should not contain raw question/exclamation marks
    assert "?" not in transformed
    assert "!" not in transformed
