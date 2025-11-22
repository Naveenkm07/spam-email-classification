from __future__ import annotations

from typing import List, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from app.spam import transform_text


def _preprocess_texts(texts: Sequence[str]) -> List[str]:
    """Apply app.transform_text to a sequence of raw texts."""

    return [transform_text(text) for text in texts]


def build_pipeline(model_type: str = "logreg", **classifier_kwargs) -> Pipeline:
    """Return a scikit-learn Pipeline for spam classification.

    Steps:
      - Preprocessor: wraps :func:`app.spam.transform_text` via FunctionTransformer
      - TF-IDF vectorizer
      - Classifier: LogisticRegression (default) or MultinomialNB
    """

    preprocessor = FunctionTransformer(_preprocess_texts, validate=False)
    vectorizer = TfidfVectorizer()

    if model_type == "nb":
        classifier = MultinomialNB(**classifier_kwargs)
    else:
        # Default to LogisticRegression with sane defaults for text
        classifier = LogisticRegression(max_iter=1000, **classifier_kwargs)

    pipeline = Pipeline(
        [
            ("preprocess", preprocessor),
            ("tfidf", vectorizer),
            ("clf", classifier),
        ],
    )

    return pipeline
