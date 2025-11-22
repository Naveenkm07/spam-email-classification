from __future__ import annotations

import pickle

from flask import Flask

from app import spam as spam_module
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


def test_load_pickle_roundtrip(tmp_path) -> None:  # type: ignore[override]
    path = tmp_path / "obj.pkl"
    with path.open("wb") as handle:
        pickle.dump({"value": 1}, handle)

    from app.spam import _load_pickle

    loaded = _load_pickle(path)
    assert loaded["value"] == 1


def test_fallback_model_used_when_no_pickles(tmp_path, app: Flask) -> None:  # type: ignore[override]
    spam_module._MODEL = None
    spam_module._VECTORIZER = None

    with app.app_context():
        app.config["MODEL_DIR"] = tmp_path

        model, vectorizer = spam_module.get_model_and_vectorizer()
        assert hasattr(model, "predict")
        assert hasattr(vectorizer, "transform")

        label_spam = spam_module.predict_spam_label("You WIN free money now!")
        label_ham = spam_module.predict_spam_label("Hello friend, how are you?")

    assert label_spam == "Spam"
    assert label_ham == "Not Spam"


def test_get_pipeline_and_metadata_raises_if_missing(tmp_path, app: Flask) -> None:  # type: ignore[override]
    from app.spam import get_pipeline_and_metadata

    with app.app_context():
        app.config["MODEL_DIR"] = tmp_path

        try:
            get_pipeline_and_metadata()
        except FileNotFoundError:
            # Expected when no model.pkl exists
            return

        assert False, "Expected FileNotFoundError when model pipeline is missing"
