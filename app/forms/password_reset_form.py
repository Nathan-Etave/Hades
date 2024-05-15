from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from app.utils import PasswordComplexity

class PasswordResetForm(FlaskForm):
    password = PasswordField('Mot de passe', validators=[DataRequired(), PasswordComplexity()])
    confirm_password = PasswordField('Confirmation', validators=[DataRequired(), EqualTo('password', message='Les mots de passe ne correspondent pas'), PasswordComplexity()])
    submit = SubmitField('Request Password Reset')