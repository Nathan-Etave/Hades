from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo

class PasswordComplexity(object):
    def __init__(self, message=None):
        if not message:
            message = u'Le mot de passe doit contenir au moins une lettre majuscule, une lettre minuscule et un chiffre, et doit avoir une longueur minimale de 6 caractères.'
        self.message = message

    def __call__(self, form, field):
        password = field.data
        if not (any(x.isupper() for x in password) and any(x.islower() for x in password) and any(x.isdigit() for x in password)) or len(password) < 6:
            raise ValidationError(self.message)

class PasswordResetForm(FlaskForm):
    password = PasswordField('Mot de passe', validators=[DataRequired(), PasswordComplexity()])
    confirm_password = PasswordField('Confirmation', validators=[DataRequired(), EqualTo('password', message='Les mots de passe ne correspondent pas'), PasswordComplexity()])
    submit = SubmitField('Request Password Reset')