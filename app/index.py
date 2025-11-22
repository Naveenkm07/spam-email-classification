from __future__ import annotations

from . import create_app

# Vercel Python runtime entrypoint: it will look for a Flask instance named
# `app` in this module when using the Flask integration.
app = create_app()
