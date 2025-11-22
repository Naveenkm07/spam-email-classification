from __future__ import annotations

from flask import Flask

from .config import Config, get_config
from .extensions import csrf, db


def create_app(config_class: type[Config] | None = None) -> Flask:
    """Application factory.

    If *config_class* is not provided, configuration is chosen based on FLASK_ENV.
    """
    app = Flask(__name__)

    cfg: type[Config] = config_class or get_config()
    app.config.from_object(cfg)

    db.init_app(app)
    csrf.init_app(app)

    from .routes import main_bp  # noqa: WPS433 (import within function)

    app.register_blueprint(main_bp)

    with app.app_context():
        # Ensure models are imported so that SQLAlchemy sees them
        from . import models  # noqa: F401,WPS433

        # Create tables if they do not yet exist (useful for local/dev setups).
        db.create_all()

    return app
