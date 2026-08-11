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


# Removed get_model_and_vectorizer and _build_fallback_model_and_vectorizer


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

        if not model_path.exists():
            raise FileNotFoundError(f"Model pipeline file not found at {model_path}")

        try:
            _PIPELINE = _load_pickle(model_path)
        except Exception as exc:  # pragma: no cover - defensive guard
            raise RuntimeError("Failed to load model pipeline.") from exc

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


def predict_spam_label(text: str) -> Tuple[str, float]:
    """Return ``("Spam" / "Not Spam", confidence_probability)`` for the given email *text*."""

    pipeline, metadata = get_pipeline_and_metadata()
    proba = float(pipeline.predict_proba([text])[0][1])
    label = "Spam" if proba >= 0.5 else "Not Spam"
    return label, proba
