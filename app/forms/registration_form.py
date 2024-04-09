from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email

class RegistrationForm(FlaskForm):
    first_name = StringField('Prénom', validators=[DataRequired()])
    last_name = StringField('Nom', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Demande l\'inscription')
