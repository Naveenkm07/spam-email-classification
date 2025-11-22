from __future__ import annotations

from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def test_tfidf_pipeline_learns_basic_spam_classification(
    sample_dataset: Tuple[List[str], List[int]],
) -> None:
    texts, labels = sample_dataset

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("clf", LogisticRegression(max_iter=200)),
        ],
    )

    pipeline.fit(texts, labels)
    predictions = pipeline.predict(texts)

    assert list(predictions) == labels
