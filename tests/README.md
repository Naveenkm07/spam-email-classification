# Tests and CI

This project uses **pytest** for tests, **pytest-cov / coverage.py** for coverage, and
GitHub Actions for CI.

## How tests are structured

- `tests/conftest.py` – creates a Flask app using the `TestingConfig` and an
  in-memory SQLite database. Tables are created before and dropped after each
  test session.
- `tests/test_auth.py` – registration and login flows using the real Flask
  routes and forms.
- `tests/test_spam.py` – unit tests for `transform_text`, including basic and
  edge-case coverage.
- `tests/test_predict.py` – tests for the spam prediction helper and `/predict`
  route using a **mock model and vectorizer** (no real pickle files required).
- `tests/test_pipeline.py` – integration test of a small TF-IDF + classifier
  pipeline trained on the sample dataset from `tests/fixtures/`.
- `tests/test_security.py` – security-oriented route tests: access control for
  protected routes and CSRF behaviour.
- `tests/fixtures/` – shared data and helpers for tests:
  - `sample_dataset.py` – small labelled spam/ham dataset used by the
    TF-IDF/model pipeline test.
  - `db_fixtures.py` – helper for creating `User` instances in the test
    database.

## Mocking strategies and assumptions

- **Spam model mocking**: `tests/test_predict.py` monkeypatches
  `app.spam.get_model_and_vectorizer` with a dummy model and vectorizer. This
  avoids loading real `model.pkl` / `vectorizer.pkl` files and keeps tests
  fast and deterministic.
- **In-memory database**: the `TestingConfig` uses `sqlite:///:memory:`. The
  `app` fixture in `conftest.py` creates and drops all tables around the test
  session, so no external database is required.
- **Session-based security**: protected routes such as `/index` and `/predict`
  require a `user_id` in the session. Tests use `client.session_transaction()`
  or the auth routes themselves to establish a logged-in session.
- **CSRF validation**: by default, tests run with `WTF_CSRF_ENABLED = False`
  (as configured in `TestingConfig`). The CSRF-specific test in
  `tests/test_security.py` temporarily enables CSRF and asserts that a POST
  request without a token receives a `400` response.
- **Coverage threshold**: the `pytest.ini` file configures pytest to run with
  `--cov=app` and `--cov-fail-under=75`, ensuring that backend coverage must be
  at least 75% for the test run to pass.

## Running tests and coverage locally

From the repository root:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Pytest will automatically:

- Collect tests under `tests/`.
- Run them with coverage enabled for the `app` package.
- Generate a terminal coverage summary and a `coverage.xml` file in the
  project root.

To see a more detailed HTML coverage report locally:

```bash
coverage html
# then open htmlcov/index.html in a browser
```

## Running the CI workflow locally

The GitHub Actions workflow is defined in `.github/workflows/ci.yml`. It
performs the following steps:

1. Install dependencies from `requirements.txt` and `requirements-dev.txt`.
2. Run `black --check .`.
3. Run `flake8`.
4. Run `pytest` (with coverage) and upload `coverage.xml` as an artifact.

To approximate the same checks locally without GitHub Actions, run:

```bash
pip install -r requirements.txt -r requirements-dev.txt
black --check .
flake8
pytest
```

If you use [`act`](https://github.com/nektos/act) to run GitHub Actions
workflows locally:

```bash
# From the repository root
act
```

`act` will execute the `CI` workflow using Docker and show the same steps that
run in GitHub Actions.
