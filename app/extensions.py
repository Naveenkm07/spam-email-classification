from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Shared Flask extensions

db: SQLAlchemy = SQLAlchemy()
csrf: CSRFProtect = CSRFProtect()
