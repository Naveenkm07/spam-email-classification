from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple

from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

from .pipeline import build_pipeline


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_ROOT = BASE_DIR / "model"
MODEL_VERSION = "v1.0"


def _load_dataset(path: Path) -> Tuple[List[str], List[int]]:
    from ml.train import _load_dataset as load_ds  # reuse

    return load_ds(path)


def evaluate() -> None:
    data_path = DATA_DIR / "spam_dataset.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    texts, labels = _load_dataset(data_path)

    version_dir = MODEL_ROOT / MODEL_VERSION
    model_path = version_dir / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")

    import pickle

    with model_path.open("rb") as model_file:
        pipeline = pickle.load(model_file)

    y_pred = pipeline.predict(texts)
    y_proba = pipeline.predict_proba(texts)[:, 1]

    print("Confusion matrix:")
    print(confusion_matrix(labels, y_pred))
    print()

    print("Classification report:")
    print(classification_report(labels, y_pred))
    print()

    print(f"ROC AUC: {roc_auc_score(labels, y_proba):.4f}")


if __name__ == "__main__":  # pragma: no cover
    evaluate()
