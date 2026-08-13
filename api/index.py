from __future__ import annotations
import os
import sys

# Add the root directory to sys.path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Vercel Serverless Function entrypoint for Flask
from app import create_app

app = create_app()
