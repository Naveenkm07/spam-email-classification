from __future__ import annotations

import json
import pickle
import re
import string
from pathlib import Path
from typing import Any, Dict, Tuple

from flask import current_app
from nltk.stem import PorterStemmer

_TOKEN_PATTERN = re.compile(r"\b\w+\b")
_ps = PorterStemmer()

_MODEL = None
_VECTORIZER = None
_PIPELINE = None
_PIPELINE_METADATA: Dict[str, Any] | None = None


def _load_pickle(path: Path) -> Any:
    with path.open("rb") as handle:
        return pickle.load(handle)


def get_model_and_vectorizer() -> Tuple[Any, Any]:
    """Lazy-load and cache the ML model and vectorizer.

    Looks for `model.pkl` and `vectorizer.pkl` in the directory configured by
    ``MODEL_DIR`` (see :mod:`app.config`).
    """

    global _MODEL, _VECTORIZER

    if _MODEL is None or _VECTORIZER is None:
        base_dir = Path(current_app.config["MODEL_DIR"])
        model_path = base_dir / "model.pkl"
        vectorizer_path = base_dir / "vectorizer.pkl"

        _VECTORIZER = _load_pickle(vectorizer_path)
        _MODEL = _load_pickle(model_path)

    return _MODEL, _VECTORIZER


def get_pipeline_and_metadata() -> Tuple[Any, Dict[str, Any]]:
    """Lazy-load and cache a trained scikit-learn Pipeline and its metadata.

    The pipeline and a companion ``metadata.json`` file are expected to live in
    the directory configured by ``MODEL_DIR`` (see :mod:`app.config`).  This is
    used by the JSON ``/api/predict`` endpoint.
    """

    global _PIPELINE, _PIPELINE_METADATA

    if _PIPELINE is None or _PIPELINE_METADATA is None:
        base_dir = Path(current_app.config["MODEL_DIR"])
        model_path = base_dir / "model.pkl"
        metadata_path = base_dir / "metadata.json"

        _PIPELINE = _load_pickle(model_path)

        metadata: Dict[str, Any] = {}
        if metadata_path.exists():
            with metadata_path.open(encoding="utf-8") as meta_file:
                metadata = json.load(meta_file)

        _PIPELINE_METADATA = metadata

    return _PIPELINE, _PIPELINE_METADATA


def transform_text(text: str) -> str:
    """Normalize and stem input text for spam classification."""

    text = text.lower()
    tokens = _TOKEN_PATTERN.findall(text)

    filtered_tokens = []
    for token in tokens:
        if token.isalnum() and token not in string.punctuation:
            filtered_tokens.append(_ps.stem(token))

    return " ".join(filtered_tokens)


def predict_spam_label(text: str) -> str:
    """Return ``"Spam"`` or ``"Not Spam"`` for the given email *text*."""

    model, vectorizer = get_model_and_vectorizer()
    transformed = transform_text(text)
    vector_input = vectorizer.transform([transformed])
    result = model.predict(vector_input)[0]
    return "Spam" if int(result) == 1 else "Not Spam"
