# Security Hardening Overview

This project is a hardened refactor of a Spam Email Classification Flask app. It focuses on:

- Eliminating plaintext password storage
- Removing hard-coded secrets
- Enforcing input validation
- Enabling CSRF protection for all forms
- Using secure session cookie settings
- Adding tests and static-analysis tooling

## 1. Password storage (bcrypt)

- User passwords are **never stored in plaintext**.
- The `users.password` column stores **bcrypt salted hashes**.
- Hashing logic lives in `app/security.py` and `app/models.py::User.set_password`.
- Password verification uses `bcrypt.checkpw` via `verify_password`.

## 2. Database access (SQLAlchemy ORM)

- All database access goes through **SQLAlchemy ORM** (`app/extensions.py`, `app/models.py`).
- There is **no raw SQL string concatenation**.
- ORM queries automatically use **parameterized statements**.

## 3. Input validation

Server-side validation is implemented via **Flask-WTF forms** in `app/forms.py`:

- **RegistrationForm** (`/signup`):
  - `full_name`: required, max 100 chars, no digits.
  - `username`: required, 3–50 chars, no spaces.
  - `email`: required, RFC-compliant email, max 254 chars.
  - `phone`: required, digits only, length 7–15.
  - `password` and `confirm_password`:
    - Required, 8–128 chars.
    - Must contain both letters and digits.
    - Must match.
- **LoginForm** (`/signin`):
  - `email`: required, valid email, max 254 chars.
  - `password`: required, max 128 chars.
- **PredictForm** (`/predict`):
  - `message`: required, 1–5000 characters.

The text-preprocessing helper `transform_text` in `app/spam.py` is also unit-tested.

## 4. CSRF protection and secure sessions

- CSRF protection is enabled globally via `Flask-WTF` (`app/extensions.py`, `app/__init__.py`).
- All HTML forms rendered from templates include `{{ form.hidden_tag() }}` to embed a CSRF token.
- In tests, CSRF is disabled via `TestingConfig` for convenience only.

Session cookies are hardened in `app/config.py`:

- `SESSION_COOKIE_SECURE` (default: `true`, overridable via env)
- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SAMESITE` (default: `Lax`)

## 5. Secrets via environment variables

No secrets are hard-coded in the repository. Configuration is driven by env vars:

- `FLASK_SECRET_KEY` – required in production.
- `DATABASE_URL` – SQLAlchemy database URL (SQLite/MySQL/etc.).
- `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_SAMESITE` – session cookie behavior.
- `MODEL_DIR` – directory containing `model.pkl` and `vectorizer.pkl`.

An `.env.example` file is provided; create a `.env` file based on it.

## 6. Static code analysis and formatting

Config files at the repo root:

- `.flake8` – flake8 configuration.
- `pyproject.toml` – black configuration.
- `mypy.ini` – mypy configuration (basic type checking, `ignore_missing_imports = True`).

### Run tools

```bash
# Format code
black .

# Lint
flake8 .

# Type-check
mypy app scripts
```

## 7. Tests

Pytest tests cover:

- Auth flows (register/login): `tests/test_auth.py`.
- Text preprocessing (`transform_text`): `tests/test_spam.py`.
- Prediction route with a **mock classifier**: `tests/test_predict.py`.

Run tests with:

```bash
pytest
```

## 8. Password-migration script

A short migration script is provided at `scripts/migrate_passwords.py`.

### What it does

- Connects to the same database used by the app (via `DATABASE_URL`).
- Iterates over all rows in the `users` table.
- Detects passwords that are **not yet bcrypt hashes**.
- Re-hashes plaintext passwords with bcrypt and updates the `password` column.

### How to run

> **Important:** Back up your database before running any migration.

```bash
# Ensure DATABASE_URL points to the database with existing users
cp .env.example .env
# edit .env to point to your existing DB (MySQL, etc.)

python scripts/migrate_passwords.py
```

The script is **idempotent**: if a password already looks like a bcrypt hash (starts with `$2`), it is left unchanged.

## 9. Threat-model notes

This refactor mitigates the following issues from the original codebase:

- Plaintext password storage
- Hard-coded secrets and DB credentials
- Lack of CSRF protection
- Weak or missing server-side validation
- Ad-hoc SQL queries without an ORM

Remaining responsibilities are **deployment-specific**:

- Enforce HTTPS in production (e.g., via reverse proxy).
- Protect `.env` and database credentials via infrastructure secrets.
- Keep dependencies up to date (see `requirements*.txt`).
