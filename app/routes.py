from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, session, url_for

from .extensions import db
from .forms import LoginForm, PredictForm, RegistrationForm
from .models import User
from .spam import predict_spam_label


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home() -> str:
    return render_template("home.html")


@main_bp.route("/about")
def about() -> str:
    return render_template("about.html")


@main_bp.route("/index", methods=["GET"])
def index() -> str:
    form = PredictForm()
    return render_template("index.html", form=form)


@main_bp.route("/predict", methods=["POST"])
def predict() -> str:
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
