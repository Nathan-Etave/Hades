from flask_wtf import FlaskForm
from wtforms import SubmitField, EmailField
from wtforms.validators import DataRequired, Email

class ForgottenPasswordForm(FlaskForm):
    """
    Represents a forgotten password form.

    Attributes:
        email (EmailField): The email field for the forgotten password form.
        submit (SubmitField): The submit button for the forgotten password form.
    """

    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Envoyer")