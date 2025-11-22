# Spam Classifier JSON API

This document describes the JSON prediction endpoint exposed by the Flask
application, along with example `curl` commands and a small JavaScript usage
snippet.

## Endpoint: `POST /api/predict`

- **URL**: `/api/predict`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request body**:

  ```json
  {
    "text": "your email text here"
  }
  ```

- **Validation rules**:

  - `text` is required.
  - Must be a non-empty string.
  - Maximum length: **10,000 characters**. Longer inputs receive `400`.

- **Response** (`200 OK` on success):

  ```json
  {
    "prediction": "spam" | "ham",
    "probability": 0.92,
    "model_version": "v1.0"
  }
  ```

  - `prediction`: human-readable label.
  - `probability`: model-estimated probability that the message is **spam**
    (float in `[0, 1]`).
  - `model_version`: version string loaded from the model metadata (e.g.
    `v1.0`).

- **Error responses** (`Content-Type: application/json`):

  - `400 Bad Request` – invalid or missing payload, or text too long.

    ```json
    { "error": "Field 'text' is required and must be a non-empty string." }
    ```

    or

    ```json
    { "error": "Text too long. Maximum length is 10,000 characters." }
    ```

## Training and model files

The training script lives in `ml/train.py` and expects a dataset at
`data/spam_dataset.csv` with columns `text,label`.

From the repository root:

```bash
python ml/train.py
```

This will:

1. Load the dataset from `data/spam_dataset.csv`.
2. Split into train/test sets, run a small grid search over TF-IDF and
   classifier hyperparameters, and fit the best `Pipeline`.
3. Save the trained `Pipeline` to:

   - `model/v1.0/model.pkl`
   - `model/v1.0/metadata.json`

4. Copy the current version to:

   - `model/model.pkl`
   - `model/metadata.json`

5. Write an evaluation report to:

   - `reports/report_v1.0.json`

The Flask app and `/api/predict` endpoint read the model and metadata from the
**directory pointed to by** `MODEL_DIR` in the Flask configuration
(e.g. `MODEL_DIR=model` for local runs, `/app/model` inside Docker).

## Example `curl` commands

Assuming the app is running on `http://localhost:8000`:

### 1. Basic spam prediction

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "Congratulations! You have won a free prize. Click here."}' \
  http://localhost:8000/api/predict
```

### 2. Ham (non-spam) prediction

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey, are we still meeting tomorrow at 10?"}' \
  http://localhost:8000/api/predict
```

### 3. Handling errors

Missing `text` field:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  http://localhost:8000/api/predict
```

Long text (over 10,000 characters) will return an error explaining the
limit.

## JavaScript usage example

Below is a minimal JavaScript example using `fetch` to call `/api/predict`
from a browser environment.

```html
<script>
  async function predictSpam() {
    const text = document.getElementById('message').value;

    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('Error from API:', data.error || data);
      return;
    }

    console.log('Prediction:', data.prediction);
    console.log('Probability:', data.probability);
    console.log('Model version:', data.model_version);
  }
</script>

<textarea id="message" rows="4" cols="60"></textarea>
<button type="button" onclick="predictSpam()">Predict</button>
```

This snippet assumes the Flask app is serving both the HTML page and the
`/api/predict` endpoint on the same origin.
