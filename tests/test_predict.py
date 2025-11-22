from __future__ import annotations

from flask import Flask

from app import spam as spam_module


def _install_mock_model(monkeypatch) -> None:
    class DummyVectorizer:
        def transform(self, texts):  # type: ignore[override]
            return texts

    class DummyModel:
        def predict(self, vectors):  # type: ignore[override]
            text = vectors[0]
            return [1 if "spam" in text.lower() else 0]

    def fake_get_model_and_vectorizer():  # type: ignore[override]
        return DummyModel(), DummyVectorizer()

    monkeypatch.setattr(spam_module, "get_model_and_vectorizer", fake_get_model_and_vectorizer)


def test_predict_spam_label_with_mock(monkeypatch, app: Flask) -> None:  # type: ignore[override]
    _install_mock_model(monkeypatch)

    with app.app_context():
        label_spam = spam_module.predict_spam_label("this is spam offer")
        label_ham = spam_module.predict_spam_label("hello friend")

    assert label_spam == "Spam"
    assert label_ham == "Not Spam"


def test_predict_route_uses_mock_model(monkeypatch, client, app: Flask) -> None:  # type: ignore[override]
    _install_mock_model(monkeypatch)

    # Simulate a logged-in user for the protected /predict route
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post(
        "/predict",
        data={"message": "this is spam content"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Spam" in response.data
