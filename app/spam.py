from __future__ import annotations

import json
import re
import string
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import onnxruntime as rt
from flask import current_app
from nltk.stem import PorterStemmer

_TOKEN_PATTERN = re.compile(r"\b\w+\b")
_ps = PorterStemmer()

_SESSION = None
_PIPELINE_METADATA: Dict[str, Any] | None = None


def get_pipeline_and_metadata() -> Tuple[Any, Dict[str, Any]]:
    """Lazy-load and cache a trained ONNX InferenceSession and its metadata.

    The model and a companion ``metadata.json`` file are expected to live in
    the directory configured by ``MODEL_DIR`` (see :mod:`app.config`).  This is
    used by the JSON ``/api/predict`` endpoint.
    """

    global _SESSION, _PIPELINE_METADATA

    if _SESSION is None or _PIPELINE_METADATA is None:
        base_dir = Path(current_app.config.get("MODEL_DIR", "model"))
        model_path = base_dir / "model.onnx"
        metadata_path = base_dir / "metadata.json"

        if not model_path.exists():
            raise FileNotFoundError(f"Model pipeline file not found at {model_path}")

        try:
            _SESSION = rt.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        except Exception as exc:  # pragma: no cover - defensive guard
            raise RuntimeError("Failed to load model pipeline.") from exc

        metadata: Dict[str, Any] = {}
        if metadata_path.exists():
            with metadata_path.open(encoding="utf-8") as meta_file:
                metadata = json.load(meta_file)

        _PIPELINE_METADATA = metadata

    return _SESSION, _PIPELINE_METADATA


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

    session, metadata = get_pipeline_and_metadata()
    
    # Preprocess text
    processed_text = transform_text(text)
    
    # Prepare inputs for ONNX runtime
    input_name = session.get_inputs()[0].name
    label_name = session.get_outputs()[0].name
    proba_name = session.get_outputs()[1].name
    
    # Run inference
    inputs = {input_name: np.array([[processed_text]], dtype=object)}
    pred_onx = session.run([label_name, proba_name], inputs)
    
    # ONNX probabilities output for sklearn models is a list of dictionaries mapping class -> prob
    proba_dict = pred_onx[1][0]
    # Assuming label 1 is Spam, get its probability (default to 0.0 if not found)
    proba = float(proba_dict.get(1, 0.0))
    
    label = "Spam" if proba >= 0.5 else "Not Spam"
    return label, proba
