FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application source
COPY . .

# Ensure model directory exists and entrypoint is executable
RUN mkdir -p /app/model && chmod +x /app/entrypoint.sh

EXPOSE 8000

# Default model directory inside the container
ENV MODEL_DIR=/app/model

ENTRYPOINT ["./entrypoint.sh"]
