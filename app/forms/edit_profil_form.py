from flask_wtf import FlaskForm
from wtforms import SubmitField, EmailField, StringField, PasswordField
from wtforms.validators import DataRequired, Email


class Edit_profil_form(FlaskForm):
    """
    Form class for editing user profile information.

    Attributes:
        last_name (StringField): Field for entering the last name of the user.
        first_name (StringField): Field for entering the first name of the user.
        email (EmailField): Field for entering the email address of the user.
        telephone (StringField): Field for entering the telephone number of the user.
        password (PasswordField): Field for entering the password of the user.
        submit (SubmitField): Button for submitting the form.
    """

    last_name = StringField("Nom", validators=[DataRequired()])
    first_name = StringField("Prénom", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    telephone = StringField("Téléphone")
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Modifier")
