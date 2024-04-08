from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, FileField
from wtforms.validators import DataRequired,Email, Regexp



class LoginForm(FlaskForm):
    mail = StringField(validators=[DataRequired()], render_kw={"placeholder": "Email"})
    mdp = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Mot de passe"})
    submit = SubmitField('Se connecter')

class InscriptionForm(FlaskForm):
    id = HiddenField('id')
    nom = StringField(validators=[DataRequired()], render_kw={"placeholder": "Nom"})
    prenom = StringField(validators=[DataRequired()], render_kw={"placeholder": "Prénom"})
    mail = StringField(validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    telephone = StringField(validators=[DataRequired(), Regexp(r'^\+?(?:[0-9] ?){6,14}[0-9]$',message="Numéro de téléphone invalide")],render_kw={"placeholder": "Téléphone"})
    submit = SubmitField('Ajouter')
    
class MdpOublieForm(FlaskForm):
    mail = StringField(validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    submit = SubmitField('Récupérer')