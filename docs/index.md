# Spam Email Classifier Documentation

Welcome to the comprehensive documentation for the Spam Email Classifier project. This folder contains detailed, section-by-section breakdowns of the entire codebase, organized by domain.

## Table of Contents

1. **[Backend Application Logic (Flask)](backend.md)**
   - Covers the Application Factory (`__init__.py`).
   - Configuration and Environment variables (`config.py`).
   - Database Models (`models.py`).
   - WTForms validation (`forms.py`).
   - Security and hashing (`security.py`).
   - API and HTML Routing (`routes.py`).
   - Vercel Serverless setup (`api/index.py`).
   - ONNX Model Integration (`spam.py`).

2. **[Machine Learning Pipeline](machine_learning.md)**
   - Covers the `scikit-learn` pipeline definition (`ml/pipeline.py`).
   - The training, hyperparameter tuning, and export script (`ml/train.py`).
   - Evaluation and testing scripts (`ml/evaluate.py`, `ml/quick_test.py`).
   - Details about the exported artifacts in the `model/` directory.

3. **[Frontend Interface (React)](frontend.md)**
   - Covers the React SPA architecture (`src/App.jsx`).
   - State management for views and dark/light themes.
   - Breakdown of the Signin, Signup, and Classify components and their API interactions.

4. **[Utility Scripts](utilities.md)**
   - Covers the ONNX format conversion script (`scripts/convert_to_onnx.py`).
   - Covers the idempotent password hashing migration script (`scripts/migrate_passwords.py`).

5. **[Deployment and Setup](deployment_and_setup.md)**
   - Covers the multi-container Docker architecture (`Dockerfile`, `docker-compose.yml`).
   - Analyzes the container startup routine (`entrypoint.sh`).
   - Outlines Makefile commands and dependency definitions (`requirements.txt`).

6. **[Accessibility Report](accessibility_report.md)**
   - Summarizes the WCAG accessibility improvements applied to the frontend application (landmarks, semantic HTML, ARIA labels, focus states).
