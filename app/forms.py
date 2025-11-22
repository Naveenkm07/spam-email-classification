from __future__ import annotations

from typing import Any

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from .models import User


class RegistrationForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=100)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=254)])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=7, max=15)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
        ],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Register")

    def validate_full_name(self, field: StringField) -> None:  # type: ignore[override]
        if any(ch.isdigit() for ch in field.data or ""):
            raise ValidationError("Name must not contain digits.")

    def validate_username(self, field: StringField) -> None:  # type: ignore[override]
        value = (field.data or "").strip()
        if " " in value:
            raise ValidationError("Username cannot contain spaces.")
        existing = User.query.filter_by(username=value).first()
        if existing is not None:
            raise ValidationError("This username is already taken.")

    def validate_email(self, field: StringField) -> None:  # type: ignore[override]
        value = (field.data or "").strip().lower()
        existing = User.query.filter_by(email=value).first()
        if existing is not None:
            raise ValidationError("An account with this email already exists.")

    def validate_phone(self, field: StringField) -> None:  # type: ignore[override]
        value = (field.data or "").strip()
        if not value.isdigit():
            raise ValidationError("Phone number must contain digits only.")

    def validate_password(self, field: PasswordField) -> None:  # type: ignore[override]
        value = field.data or ""
        if not any(ch.isalpha() for ch in value) or not any(ch.isdigit() for ch in value):
            raise ValidationError(
                "Password must contain at least one letter and one digit.",
            )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=254)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class PredictForm(FlaskForm):
    message = TextAreaField(
        "Message",
        validators=[DataRequired(), Length(min=1, max=5000)],
    )
    submit = SubmitField("Predict")
