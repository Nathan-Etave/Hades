from app.register import bp
from flask import render_template, redirect, url_for, flash
from app.forms.registration_form import RegistrationForm
from app.models.utilisateur import UTILISATEUR
from app.models.notification import NOTIFICATION

@bp.route('/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if UTILISATEUR.query.filter_by(email_Utilisateur=form.email.data).first():
            flash('Email déjà utilisé.', 'danger')
        else:
            flash('Demande d\'inscription envoyée avec succès.', 'success')
        return redirect(url_for('register.register'))
    return render_template('register/index.html', form=form)
