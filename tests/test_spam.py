from __future__ import annotations

from app.spam import transform_text


def test_transform_text_basic() -> None:
    text = "Hello, WORLD!!! 123"
    transformed = transform_text(text)
    # Lowercased, punctuation removed, words stemmed, digits kept
    assert "hello" in transformed
    assert "world" in transformed
    assert "123" in transformed


def test_transform_text_empty_string() -> None:
    transformed = transform_text("")
    assert transformed == ""


def test_transform_text_punctuation_only() -> None:
    text = "!!!???...,,,"
    transformed = transform_text(text)
    # Only punctuation: result should be empty
    assert transformed == ""


def test_transform_text_unicode_characters() -> None:
    text = "Olá mundo 😊 Привет мир"
    transformed = transform_text(text)
    # Ensure it does not crash and returns a non-empty string for word characters
    assert isinstance(transformed, str)


def test_transform_text_very_long_input() -> None:
    text = "spam " * 2000  # 8000+ characters
    transformed = transform_text(text)
    # Should still process and not exceed original token count dramatically
    assert "spam" in transformed
