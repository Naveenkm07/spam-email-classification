from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_ROOT = BASE_DIR / "model"


def main() -> None:
    model_path = MODEL_ROOT / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}. Run ml/train.py first.")

    import pickle

    with model_path.open("rb") as model_file:
        pipeline = pickle.load(model_file)

    examples = [
        "Win a free prize now!!!",
        "Hey, are we still meeting tomorrow?",
    ]

    preds = pipeline.predict(examples)
    probas = pipeline.predict_proba(examples)

    for text, label, proba in zip(examples, preds, probas):
        print("Text:", text)
        print("Predicted label:", label)
        print("Probabilities (ham, spam):", proba)
        print("---")


if __name__ == "__main__":  # pragma: no cover
    main()
