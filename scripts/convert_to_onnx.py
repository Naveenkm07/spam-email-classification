import pickle
import json
import shutil
from pathlib import Path
from sklearn.pipeline import Pipeline
from skl2onnx import to_onnx
from skl2onnx.common.data_types import StringTensorType

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_ROOT = BASE_DIR / "model"
MODEL_VERSION = "v1.0"
VERSION_DIR = MODEL_ROOT / MODEL_VERSION

def convert():
    model_path = VERSION_DIR / "model.pkl"
    if not model_path.exists():
        model_path = MODEL_ROOT / "model.pkl"
    
    if not model_path.exists():
        print(f"Error: Could not find {model_path}")
        return

    print(f"Loading scikit-learn model from {model_path}")
    with model_path.open("rb") as f:
        pipe = pickle.load(f)

    print("Extracting TfidfVectorizer and LogisticRegression...")
    # The original pipeline has: FunctionTransformer -> TfidfVectorizer -> LogisticRegression
    # We strip the FunctionTransformer out because skl2onnx cannot export arbitrary Python code.
    tfidf = pipe.named_steps["tfidf"]
    clf = pipe.named_steps["clf"]

    new_pipe = Pipeline([
        ("tfidf", tfidf),
        ("clf", clf)
    ])

    print("Converting to ONNX...")
    # TfidfVectorizer takes an array of strings
    initial_type = [('input', StringTensorType([None, 1]))]
    
    # We must provide options for TfidfVectorizer to preserve the token pattern
    options = {id(new_pipe): {'zipmap': False}}
    onx = to_onnx(new_pipe, initial_types=initial_type, options=options)

    onnx_path_version = VERSION_DIR / "model.onnx"
    print(f"Saving ONNX model to {onnx_path_version}")
    with onnx_path_version.open("wb") as f:
        f.write(onx.SerializeToString())

    onnx_path_root = MODEL_ROOT / "model.onnx"
    print(f"Copying to {onnx_path_root}")
    shutil.copy2(onnx_path_version, onnx_path_root)
    print("Done!")

if __name__ == "__main__":
    convert()
