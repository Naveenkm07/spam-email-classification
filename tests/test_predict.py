from __future__ import annotations

from flask import Flask

from app import spam as spam_module


def _install_mock_model(monkeypatch) -> None:
    class DummyPipeline:
        def predict_proba(self, texts):  # type: ignore[override]
            text = texts[0]
            if "spam" in text.lower():
                return [[0.1, 0.9]]
            else:
                return [[0.8, 0.2]]

    def fake_get_pipeline_and_metadata():  # type: ignore[override]
        return DummyPipeline(), {"version": "mock"}

    monkeypatch.setattr(spam_module, "get_pipeline_and_metadata", fake_get_pipeline_and_metadata)


def test_predict_spam_label_with_mock(monkeypatch, app: Flask) -> None:  # type: ignore[override]
    _install_mock_model(monkeypatch)

    with app.app_context():
        label_spam, proba_spam = spam_module.predict_spam_label("this is spam offer")
        label_ham, proba_ham = spam_module.predict_spam_label("hello friend")

    assert label_spam == "Spam"
    assert proba_spam == 0.9
    assert label_ham == "Not Spam"
    assert proba_ham == 0.2


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
