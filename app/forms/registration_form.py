from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email
from app.utils import PasswordComplexity


class RegistrationForm(FlaskForm):
    """
    Represents a registration form for users.

    Attributes:
        first_name (StringField): Field for entering the first name of the user.
        last_name (StringField): Field for entering the last name of the user.
        email (EmailField): Field for entering the email address of the user.
        submit (SubmitField): Button for submitting the registration form.
    """

    first_name = StringField("Prénom", validators=[DataRequired()])
    last_name = StringField("Nom", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), PasswordComplexity()])
    submit = SubmitField("Demande l'inscription")
