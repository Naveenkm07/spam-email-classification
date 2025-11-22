from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split

from .pipeline import build_pipeline


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_ROOT = BASE_DIR / "model"
REPORTS_DIR = BASE_DIR / "reports"

MODEL_VERSION = "v1.0"


def _load_dataset(path: Path) -> Tuple[List[str], List[int]]:
    """Load dataset from CSV with columns `text,label`.

    Labels are mapped to integers: 0 = ham, 1 = spam.
    """

    texts: List[str] = []
    labels: List[int] = []

    with path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if "text" not in reader.fieldnames or "label" not in reader.fieldnames:
            raise ValueError("CSV must contain 'text' and 'label' columns")

        for row in reader:
            text = (row["text"] or "").strip()
            raw_label = (row["label"] or "").strip().lower()
            if not text:
                continue

            if raw_label in {"spam", "1", "true"}:
                label_int = 1
            else:
                label_int = 0

            texts.append(text)
            labels.append(label_int)

    if not texts:
        raise ValueError("Dataset is empty or contains no valid rows")

    return texts, labels


def train() -> None:
    data_path = DATA_DIR / "spam_dataset.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    X, y = _load_dataset(data_path)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline(model_type="logreg")

    param_grid = {
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "tfidf__min_df": [1, 2],
        "clf__C": [0.5, 1.0, 2.0],
    }

    grid = GridSearchCV(
        pipeline,
        param_grid=param_grid,
        cv=3,
        scoring="f1",
        n_jobs=-1,
        verbose=1,
    )

    grid.fit(X_train, y_train)
    best_pipeline = grid.best_estimator_

    y_pred = best_pipeline.predict(X_test)
    y_proba = best_pipeline.predict_proba(X_test)[:, 1]

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    metrics: Dict[str, Any] = {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": auc,
        "confusion_matrix": cm,
        "classification_report": report,
    }

    version_dir = MODEL_ROOT / MODEL_VERSION
    version_dir.mkdir(parents=True, exist_ok=True)
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = version_dir / "model.pkl"
    metadata_path = version_dir / "metadata.json"

    # Persist the trained pipeline
    import pickle

    with model_path.open("wb") as model_file:
        pickle.dump(best_pipeline, model_file)

    metadata = {
        "version": MODEL_VERSION,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "best_params": grid.best_params_,
        "metrics": metrics,
        "label_mapping": {"ham": 0, "spam": 1},
        "classifier": type(best_pipeline.named_steps["clf"]).__name__,
    }

    with metadata_path.open("w", encoding="utf-8") as meta_file:
        json.dump(metadata, meta_file, indent=2)

    # Also write/overwrite top-level "current" model and metadata
    shutil.copy2(model_path, MODEL_ROOT / "model.pkl")
    shutil.copy2(metadata_path, MODEL_ROOT / "metadata.json")

    # Write evaluation report
    report_path = REPORTS_DIR / f"report_{MODEL_VERSION}.json"
    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(
            {
                "version": MODEL_VERSION,
                "created_at": metadata["created_at"],
                "metrics": metrics,
            },
            report_file,
            indent=2,
        )

    print(f"Saved model to {model_path}")
    print(f"Saved metadata to {metadata_path}")
    print(f"Saved report to {report_path}")


if __name__ == "__main__":  # pragma: no cover
    train()
