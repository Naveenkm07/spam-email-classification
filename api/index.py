from __future__ import annotations

# Vercel Serverless Function entrypoint for Flask
from app import create_app

flask_app = create_app()

def app(environ, start_response):
    """WSGI middleware to fix PATH_INFO in Vercel."""
    path_info = environ.get("PATH_INFO", "")
    if path_info.startswith("/api/index.py"):
        environ["PATH_INFO"] = path_info[len("/api/index.py"):] or "/"
    elif path_info.startswith("/api/index"):
        environ["PATH_INFO"] = path_info[len("/api/index"):] or "/"
    
    return flask_app(environ, start_response)
