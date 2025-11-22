from __future__ import annotations

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from .extensions import db
from .forms import LoginForm, PredictForm, RegistrationForm
from .models import User
from .spam import get_pipeline_and_metadata, predict_spam_label


main_bp = Blueprint("main", __name__)


def _require_login() -> bool:
    """Return True if the current session represents a logged-in user."""

    return bool(session.get("user_id"))


@main_bp.route("/")
def home() -> str:
    return render_template("home.html")


@main_bp.route("/about")
def about() -> str:
    return render_template("about.html")


@main_bp.route("/index", methods=["GET"])
def index() -> str:
    if not _require_login():
        return redirect(url_for("main.signin"))

    form = PredictForm()
    return render_template("index.html", form=form)


@main_bp.route("/predict", methods=["POST"])
def predict() -> str:
    if not _require_login():
        return redirect(url_for("main.signin"))

    form = PredictForm()
    if not form.validate_on_submit():
        flash("Please provide a valid message.", "error")
        return render_template("index.html", form=form), 400

    label = predict_spam_label(form.message.data)
    return render_template("result.html", prediction=label)


@main_bp.route("/signup", methods=["GET", "POST"])
def signup() -> str:
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please sign in.", "success")
        return redirect(url_for("main.signin"))

    return render_template("signup.html", form=form)


@main_bp.route("/signin", methods=["GET", "POST"])
def signin() -> str:
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            session["user_id"] = user.id
            session["user_email"] = user.email
            session["user_name"] = user.full_name
            if form.remember_me.data:
                # Rely on Flask's PERMANENT_SESSION_LIFETIME for duration.
                session.permanent = True
            flash("Signed in successfully.", "success")
            return redirect(url_for("main.index"))

        flash("Invalid email or password.", "error")

    return render_template("signin.html", form=form)


@main_bp.route("/logout")
def logout() -> str:
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))


@main_bp.route("/api/predict", methods=["POST"])
def api_predict():
    """JSON prediction endpoint.

    Expects a JSON body of the form ``{"text": "..."}`` and returns
    ``{"prediction": "spam"|"ham", "probability": float, "model_version": str}``.
    """

    data = request.get_json(silent=True) or {}
    text = data.get("text")

    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Field 'text' is required and must be a non-empty string."}), 400

    if len(text) > 10_000:
        return jsonify({"error": "Text too long. Maximum length is 10,000 characters."}), 400

    pipeline, metadata = get_pipeline_and_metadata()

    # Assume labels are encoded as 0 = ham, 1 = spam
    proba = float(pipeline.predict_proba([text])[0][1])
    prediction_label = "spam" if proba >= 0.5 else "ham"

    version = metadata.get("version", "unknown")

    return (
        jsonify(
            {
                "prediction": prediction_label,
                "probability": proba,
                "model_version": version,
            },
        ),
        200,
    )
