import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, sender, recipients, html_body):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    msg.attach(MIMEText(html_body, 'html'))
    mail_server = smtplib.SMTP('smtp.gmail.com', 587)
    mail_server.starttls()
    mail_server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
    mail_server.sendmail(sender, recipients, msg.as_string())
    mail_server.quit()

def send_registration_request_email(email):
    subject = 'Demande d\'inscription en attente de validation'
    sender = f'NOM_DE_LA_PLATEFORME <{os.environ.get("MAIL_USERNAME")}>'
    recipients = email
    html_body = f'<p>Bonjour, votre demande d\'inscription est en attente de validation. Vous recevrez un email de confirmation dès que votre compte sera activé.</p>'
    send_email(subject, sender, recipients, html_body)

def send_registration_confirmation_email(email, password):
    subject = 'Inscription validée'
    sender = f'NOM_DE_LA_PLATEFORME <{os.environ.get("MAIL_USERNAME")}>'
    recipients = email
    html_body = f'<p>Bonjour, votre demande d\'inscription a été validée. Vous pouvez désormais vous connecter à la plateforme.</p><p>Votre mot de passe est: {password}</p>'
    send_email(subject, sender, recipients, html_body)

def send_registration_rejection_email(email):
    subject = 'Demande d\'inscription refusée'
    sender = f'NOM_DE_LA_PLATEFORME <{os.environ.get("MAIL_USERNAME")}>'
    recipients = email
    html_body = f'<p>Bonjour, votre demande d\'inscription a été refusée.</p>'
    send_email(subject, sender, recipients, html_body)

def send_reactivation_confirmation_email(email):
    subject = 'Réactivation de votre compte'
    sender = f'NOM_DE_LA_PLATEFORME <{os.environ.get("MAIL_USERNAME")}>'
    recipients = email
    html_body = f'<p>Bonjour, votre compte a été réactivé. Vous pouvez désormais vous connecter à la plateforme.</p>'
    send_email(subject, sender, recipients, html_body)

def send_reactivation_rejection_email(email):
    subject = 'Réactivation de votre compte refusée'
    sender = f'NOM_DE_LA_PLATEFORME <{os.environ.get("MAIL_USERNAME")}>'
    recipients = email
    html_body = f'<p>Bonjour, la réactivation de votre compte a été refusée.</p>'
    send_email(subject, sender, recipients, html_body)