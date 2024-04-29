from flask_wtf import FlaskForm
from wtforms import SubmitField, EmailField, StringField, PasswordField
from wtforms.validators import DataRequired, Email

class Edit_profil_form(FlaskForm) :

    last_name = StringField("Nom", validators=[DataRequired()])
    first_name = StringField("Prénom", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    telephone = StringField("Téléphone")
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Modifier")