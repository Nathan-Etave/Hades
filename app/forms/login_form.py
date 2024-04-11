from flask_wtf import FlaskForm
from wtforms import SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    """
    Represents a login form.

    Attributes:
        email (EmailField): The email field for the login form.
        password (StringField): The password field for the login form.
        submit (SubmitField): The submit button for the login form.
    """

    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")
