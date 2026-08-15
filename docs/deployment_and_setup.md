# Deployment and Setup Documentation

This document outlines the infrastructure, containerization, and dependency management files located at the root of the project.

---

## 1. `Dockerfile`

Defines the environment and build instructions to package the Flask application into a Docker container.

### Code Sections:

- **`FROM python:3.11-slim`**: Uses a lightweight Debian-based Python image to keep the overall container size small.
- **Environment Variables**:
  - `PYTHONDONTWRITEBYTECODE=1`: Prevents Python from writing `.pyc` files, which are unnecessary inside an immutable container.
  - `PYTHONUNBUFFERED=1`: Ensures stdout/stderr are immediately flushed to the Docker logs, preventing delayed logging.
- **Dependency Installation**:
  - Copies `requirements.txt` and `requirements-dev.txt`.
  - Runs `pip install --no-cache-dir` to install production dependencies and the `gunicorn` WSGI server, avoiding the retention of temporary pip cache files.
- **File Copying**:
  - `COPY . .` copies the entire application context into the `/app` working directory.
- **Directory Setup & Permissions**:
  - `RUN mkdir -p /app/model`: Ensures the model directory exists, even if empty in source control.
  - `chmod +x /app/entrypoint.sh`: Ensures the startup script has execution permissions.
- **Network & Entrypoint**:
  - `EXPOSE 8000`: Documents that the container will listen on port 8000.
  - `ENV MODEL_DIR=/app/model`: Explicitly sets the environment variable expected by the application logic (`app/config.py`).
  - `ENTRYPOINT ["./entrypoint.sh"]`: Delegates container startup logic to the bash script.

---

## 2. `docker-compose.yml`

Orchestrates the multi-container environment for local development and deployment.

### Code Sections:

- **`app` Service (The Flask Application)**:
  - `build: .`: Builds the image from the local `Dockerfile`.
  - `env_file: [.env]`: Passes environment variables to the container.
  - `depends_on: [db]`: Ensures the `app` container doesn't start until the `db` container passes its health check (`condition: service_healthy`).
  - `ports: ["8000:8000"]`: Maps the host port to the container port.
  - `volumes: [./model:/app/model]`: A critical bind mount. It ensures that if the container downloads or generates new ML models, they persist on the host machine in the `model/` directory, rather than being destroyed when the container stops.
- **`db` Service (MySQL Database)**:
  - `image: mysql:8.0`: Uses the official MySQL 8 image.
  - `environment`: Sets database credentials (`MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`) using variable substitution with fallback defaults.
  - `volumes`: Mounts a named volume (`db_data`) to `/var/lib/mysql` to persist database records. Mounts `docker/mysql/init` to `/docker-entrypoint-initdb.d` (allowing custom SQL scripts to run on database initialization).
  - `healthcheck`: Pings the database every 10 seconds to verify it is ready to accept connections.
- **`adminer` Service (Database UI)**:
  - Runs a lightweight database administration tool accessible on port 8080.
- **`volumes: [db_data]`**: Declares the persistent Docker volume used by the database.

---

## 3. `entrypoint.sh`

The shell script executed inside the container when it starts up.

### Code Sections:

- **`set -e`**: Ensures the script exits immediately if any command fails.
- **Environment Fallback**: Sets `FLASK_ENV=production` if it is not already defined.
- **Database Initialization**:
  - Uses a "Here Document" (`<< 'PYCODE'`) to run a small inline Python script.
  - The script creates the Flask app context and runs `db.create_all()`. This ensures all SQLAlchemy tables defined in `app/models.py` are created in the MySQL database before the server starts handling requests.
- **Password Migration Guard**:
  - Checks if `scripts/migrate_passwords.py` exists.
  - If so, it runs the script to ensure legacy plaintext passwords are automatically hashed using bcrypt upon startup.
- **Starting the Server**:
  - Uses `exec` to replace the shell process with the `gunicorn` process.
  - Starts Gunicorn bound to `0.0.0.0` on port `8000`, using the WSGI application object defined in `wsgi:app` (which imports `create_app()`).

---

## 4. `Makefile`

Provides simple CLI shortcuts for managing the Docker environment.

### Code Sections:

- `make build`: Shortcut for `docker compose build`.
- `make up`: Shortcut for `docker compose up --build`. Starts the cluster in the foreground.
- `make test`: Shortcut for `docker compose run --rm app pytest`. It spins up a temporary container based on the `app` image, runs the test suite, and then automatically removes the container (`--rm`).
- `make stop`: Shortcut for `docker compose down`. Stops and removes the containers and networks, but preserves the persistent volumes (`db_data`).

---

## 5. Dependencies (`requirements.txt`)

Lists the core Python libraries needed in production.

- **Web Framework**: `Flask`, `Flask-WTF`, `email-validator` (used by WTForms).
- **Database**: `Flask-SQLAlchemy`, `SQLAlchemy`, `mysql-connector-python`.
- **Security & Config**: `bcrypt`, `python-dotenv`.
- **Machine Learning**: `nltk` (for stemming), `numpy`, `onnxruntime` (for inference without scikit-learn).
