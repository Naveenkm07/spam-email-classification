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


def test_index_requires_login(client) -> None:
    response = client.get("/index", follow_redirects=False)

    assert response.status_code in (301, 302)
    assert "/signin" in (response.headers.get("Location") or "")


def test_index_and_predict_accessible_when_logged_in(monkeypatch, client) -> None:
    _install_mock_model(monkeypatch)

    # Establish a logged-in session
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    index_response = client.get("/index")
    assert index_response.status_code == 200

    predict_response = client.post(
        "/predict",
        data={"message": "hello world spam"},
        follow_redirects=True,
    )

    assert predict_response.status_code == 200


def test_predict_requires_login(client) -> None:
    response = client.post("/predict", data={"message": "hi"}, follow_redirects=False)

    assert response.status_code in (301, 302)
    assert "/signin" in (response.headers.get("Location") or "")


def test_csrf_protects_post_routes_when_enabled(app: Flask) -> None:  # type: ignore[override]
    app.config["WTF_CSRF_ENABLED"] = True

    with app.test_client() as client:
        response = client.post(
            "/predict",
            data={"message": "csrf protected"},
            follow_redirects=False,
        )

    assert response.status_code == 400
