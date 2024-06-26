import smtplib
import os
from config import Config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(subject, sender, recipients, html_body):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipients
    msg.attach(MIMEText(html_body, "html"))
    mail_server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
    mail_server.starttls()
    mail_server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
    mail_server.sendmail(sender, recipients, msg.as_string())
    mail_server.quit()


def send_registration_request_email(email):
    subject = "Demande d'inscription en attente de validation"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = "<p>Bonjour, votre demande d'inscription est en attente de validation. Vous recevrez un email de confirmation dès que votre compte sera activé.</p>"
    send_email(subject, sender, recipients, html_body)


def send_registration_confirmation_email(email):
    subject = "Inscription validée"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = f"<p>Bonjour, votre demande d'inscription a été validée. Vous pouvez désormais vous connecter à la plateforme.</p>"
    send_email(subject, sender, recipients, html_body)


def send_registration_rejection_email(email):
    subject = "Demande d'inscription refusée"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = "<p>Bonjour, votre demande d'inscription a été refusée.</p>"
    send_email(subject, sender, recipients, html_body)


def send_reactivation_confirmation_email(email):
    subject = "Réactivation de votre compte"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = "<p>Bonjour, votre compte a été réactivé. Vous pouvez désormais vous connecter à la plateforme.</p>"
    send_email(subject, sender, recipients, html_body)


def send_reactivation_rejection_email(email):
    subject = "Réactivation de votre compte refusée"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = f"<p>Bonjour, la réactivation de votre compte a été refusée.</p>"
    send_email(subject, sender, recipients, html_body)


def send_forgotten_password_email(email, uuid):
    """Sends a forgotten password email to the specified email address.

    Parameters:
    - email (str): The recipient's email address.
    - new_password (str): The new password to be included in the email.

    Returns: None
    """
    subject = "Réinitialisation de votre mot de passe"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = f"<p>Bonjour, une demande de réinitialisation de mot de passe a été faite sur votre compte. \n Pour la valider, cliquez sur le lien suivant :</p> <a href='http://127.0.0.1:5000/reinitialisation/{uuid}'>Réinitialisation du mot de passe</a><p>Ce lien est valide pour une durée de 10 minutes.</p>"
    send_email(subject, sender, recipients, html_body)

def send_deactivation_email(email):
    """
    Sends a deactivation email to the specified email address.

    Args:
        email (str): The email address to send the deactivation email to.

    Returns:
        None
    """
    subject = "Désactivation de votre compte"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = "<p>Bonjour, votre compte a été désactivé. Pour plus d'informations, veuillez contacter le support technique.</p> <p>Vous pouvez demander la réactivation de votre compte depuis la page de connexion sur le lien suivant :</p> <a href='http://127.0.0.1:5000/connexion/'>Réactivation du compte</a>"
    send_email(subject, sender, recipients, html_body)

def send_delete_email(email):
    """
    Sends a delete email to the specified email address.

    Args:
        email (str): The email address to send the delete email to.

    Returns:
        None
    """
    subject = "Suppression de votre compte"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = "<p>Bonjour, votre compte a été supprimé. Pour plus d'informations, veuillez contacter le support technique.</p>"
    send_email(subject, sender, recipients, html_body)

def send_reset_password_confirmation(email):
    """
    Sends a reset password confirmation email to the specified email address.

    Args:
        email (str): The email address to send the reset password confirmation email to.

    Returns:
        None
    """
    subject = "Réinitialisation de votre mot de passe"
    sender = f'Hadès <{Config.MAIL_USERNAME}>'
    recipients = email
    html_body = "<p>Bonjour, votre mot de passe a bien été réinitialisé.</p>"
    send_email(subject, sender, recipients, html_body)
