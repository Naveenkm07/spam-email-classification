# Backend Documentation (`app/` and `api/`)

This document provides a detailed, section-by-section breakdown of the backend logic powering the Spam Email Classifier application. The backend is built using Flask, SQLAlchemy (for ORM), Flask-WTF (for forms and CSRF protection), and bcrypt (for password hashing).

---

## 1. `app/__init__.py` (Application Factory)

This file serves as the entry point for configuring and creating the Flask application instance using the Application Factory pattern.

### Code Sections:

- **Imports:** Imports Flask, configuration handlers (`Config`, `get_config`), and initialized extensions (`csrf`, `db`).
- **`create_app(config_class)`:**
  - **Initialization:** Instantiates `app = Flask(__name__)`.
  - **Configuration:** Loads the appropriate configuration class. If `config_class` is not passed, it relies on `get_config()` which looks at the `FLASK_ENV` environment variable.
  - **Extension Registration:** Binds the application instance to the SQLAlchemy database (`db.init_app(app)`) and the CSRF protector (`csrf.init_app(app)`).
  - **Blueprint Registration:** Imports `main_bp` from `.routes` and registers it (`app.register_blueprint(main_bp)`). This maps the URL routes defined in `routes.py` to the application.
  - **App Context Operations:** Uses `with app.app_context():` to safely import `models` (ensuring SQLAlchemy recognizes the schemas) and runs `db.create_all()` to create tables in the database if they don't already exist.
  - **Returns:** The configured `app` instance.

---

## 2. `app/config.py` (Configuration)

Manages all environment variables and configuration settings.

### Code Sections:

- **Environment Loading:** Uses `python-dotenv` (`load_dotenv`) to load variables from the root `.env` file into the OS environment. Defines `BASE_DIR`.
- **`Config` (Base Class):**
  - `SECRET_KEY`: Used for session signing. Falls back to a random 32-byte string if `FLASK_SECRET_KEY` is not set (useful for local dev, but not production-safe if restarting often).
  - `SQLALCHEMY_DATABASE_URI`: Falls back to a local SQLite database (`spam_classifier.db`) if `DATABASE_URL` is not provided.
  - `SESSION_COOKIE_*`: Security settings for cookies (Secure, HttpOnly, SameSite).
  - `MODEL_DIR`: Defines where the machine learning models are stored, defaulting to `BASE_DIR / "model"`.
- **`TestingConfig`:** Overrides `Config` for unit tests. Sets `TESTING=True`, uses an in-memory SQLite database (`sqlite:///:memory:`), and disables CSRF protection for easier test requests.
- **`get_config()`:** A helper function that inspects `FLASK_ENV` and returns `TestingConfig` if the environment is "testing"; otherwise, it returns `Config`.

---

## 3. `app/extensions.py` (Extensions)

### Code Sections:

- **Instantiations:** Creates instances of `SQLAlchemy` (`db`) and `CSRFProtect` (`csrf`).
- **Purpose:** These are defined in a separate file to prevent circular import issues between `models.py` (which needs `db`), `__init__.py` (which binds `db` to the app), and `routes.py`.

---

## 4. `app/models.py` (Database Schemas)

Defines the structure of the database tables using SQLAlchemy ORM.

### Code Sections:

- **`User` Model:** Inherits from `db.Model`.
  - **Columns:**
    - `id`: Primary key integer.
    - `full_name`: String, required.
    - `username`: String, unique, indexed for fast lookups.
    - `email`: String, unique, indexed.
    - `phone`: String.
    - `password`: String (128 chars) to store the bcrypt hash.
    - `created_at`: DateTime, defaults to `datetime.utcnow`.
  - **Methods:**
    - `set_password(raw_password)`: Wraps `security.hash_password` to safely hash and store the password.
    - `check_password(raw_password)`: Wraps `security.verify_password` to validate a login attempt.

---

## 5. `app/forms.py` (Web Forms)

Uses `Flask-WTF` and `WTForms` to define form fields and server-side validation logic.

### Code Sections:

- **`RegistrationForm`:**
  - **Fields:** `full_name`, `username`, `email`, `phone`, `password`, `confirm_password`, `submit`.
  - **Validators:** Enforces constraints like `DataRequired`, `Length`, `Email`, and `EqualTo` (for password confirmation).
  - **Custom Validation Methods:**
    - `validate_full_name`: Ensures no digits are in the name.
    - `validate_username`: Ensures no spaces and checks the database to ensure the username isn't taken.
    - `validate_email`: Checks the database to ensure the email isn't already registered.
    - `validate_phone`: Ensures only digits are present.
    - `validate_password`: Enforces complexity (at least one letter and one digit).
- **`LoginForm`:**
  - **Fields:** `email`, `password`, `remember_me` (boolean checkbox), `submit`.
- **`PredictForm`:**
  - **Fields:** `message` (TextAreaField, min length 1, max length 5000) and `submit`.

---

## 6. `app/security.py` (Authentication Utilities)

Handles password hashing and verification to ensure no plaintext passwords are saved or compared.

### Code Sections:

- **`_BCRYPT_PREFIXES`:** Defines valid bcrypt prefixes (`$2a$`, `$2b$`, `$2y$`).
- **`is_bcrypt_hash(value)`:** Checks if a given string starts with a valid bcrypt prefix. Used by the migration script.
- **`hash_password(password)`:** Generates a random salt (`bcrypt.gensalt()`) and hashes the UTF-8 encoded password. Returns the decoded string.
- **`verify_password(password, password_hash)`:** Compares a plaintext password against the stored hash using `bcrypt.checkpw()`. Handles `ValueError` if the hash is malformed.

---

## 7. `app/spam.py` (Machine Learning Integration)

Acts as the bridge between the Flask application and the exported ONNX machine learning model.

### Code Sections:

- **Globals:** Uses `_SESSION` and `_PIPELINE_METADATA` to cache the loaded model in memory, avoiding disk I/O on every request.
- **`get_pipeline_and_metadata()`:**
  - Checks if the model is cached.
  - If not, locates `model.onnx` and `metadata.json` in `MODEL_DIR`.
  - Instantiates `onnxruntime.InferenceSession`.
  - Loads and parses `metadata.json`.
  - Caches and returns both.
- **`transform_text(text)`:**
  - Preprocesses the text identically to the training pipeline.
  - Lowercases the text.
  - Extracts tokens using a regex (`\b\w+\b`).
  - Stems tokens (using `nltk`'s `PorterStemmer`) and removes punctuation.
- **`predict_spam_label(text)`:**
  - Retrieves the model session.
  - Preprocesses the input using `transform_text`.
  - Maps inputs to the ONNX session requirements.
  - Runs inference (`session.run`).
  - Extracts the probability for class 1 (Spam).
  - Returns the label ("Spam" if probability > 0.5, else "Not Spam") and the probability score.

---

## 8. `app/routes.py` (Routing and Views)

Defines the core web endpoints and the REST API endpoint.

### Code Sections:

- **`main_bp`:** Defines the Blueprint for routing.
- **`_require_login()`:** Helper that checks if `session.get("user_id")` exists.
- **HTML Views (Frontend):**
  - `/`, `/about`: Renders static templates.
  - `/index`: Protected route. Renders the main classification form (`PredictForm`).
  - `/predict`: Protected route. Validates the `PredictForm`, calls `predict_spam_label`, and renders the result.
  - `/signup`: Validates `RegistrationForm`. Creates a new `User`, hashes the password, commits to DB, and redirects to signin.
  - `/signin`: Validates `LoginForm`. Checks the database for the user, verifies the password, sets session variables (`user_id`, `user_email`, `user_name`, `permanent`), and redirects to `/index`.
  - `/logout`: Clears the session.
- **API Endpoint:**
  - `/api/predict`: A JSON endpoint that accepts POST requests. It is decorated with `@csrf.exempt` so it can be called programmatically from other clients (like a separate React frontend) without needing a CSRF token.
  - Validates the incoming JSON (`text` field required, < 10,000 chars).
  - Attempts to load the model (returning 503 if unavailable).
  - Returns a JSON payload with `prediction`, `probability`, and `model_version`.

---

## 9. `api/index.py` (Vercel Serverless Entrypoint)

### Code Sections:

- **Path Modification:** `sys.path.append(...)` adds the parent directory to the Python module search path. This is necessary in serverless environments (like Vercel) so that `from app import create_app` resolves correctly.
- **Initialization:** Calls `create_app()` and assigns it to `app`. The Vercel runtime looks for an object named `app` to handle incoming HTTP requests.
