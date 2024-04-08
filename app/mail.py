import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def mail_inscription(destinataire, mdp):
    msg = MIMEMultipart()
    msg['From'] = 'pinpinpinponponpon45@gmail.com'
    msg['To'] = destinataire
    msg['Subject'] = 'Bienvenue sur PinPon45'

    message = """
    <html>
        <head>
            <style>
                img {
                    width: 100px;
                }

            </style>
        </head>
        <body>
            <p>Bonjour,</p>
            <p>L'équipe de PinPon45 vous souhaite la bienvenue !</p>
            <p>Vous pouvez dès à présent vous connecter à votre compte.</p>
            <p>connectez-vous à l'aide du mot de passe suivant : """ + mdp + """</p>
            <p>Cordialement,<br>L'équipe de PinPon45</p>
            <img src="https://sdis45.com/wp-content/themes/sdis45/assets/img/logo/logo-loiret.png">
    """

    msg.attach(MIMEText(message, 'html'))
    mailserver = smtplib.SMTP('smtp.gmail.com', 587)
    mailserver.starttls()
    mailserver.login('pinpinpinponponpon45@gmail.com', 'leoawgejhmmlhwyy')
    mailserver.sendmail('pinpinpinponponpon45@gmail.com', destinataire, msg.as_string())
    mailserver.quit()


def mail_oublie(destinataire, mdp):
    msg = MIMEMultipart()
    msg['From'] = 'pinpinpinponponpon45@gmail.com'
    msg['To'] = destinataire
    msg['Subject'] = 'Mot de passe oublié'

    message = """
    <html>
        <head>
            <style>
                img {
                    width: 100px;
                }

            </style>
        </head>
    <body>
        <p>Bonjour,</p>
        <p>Vous avez perdu votre mot de passe le voici :</p>
        <p>connectez-vous à l'aide du mot de passe suivant : """ + mdp + """</p>
        <p>La prochaine fois, n'oubliez pas votre mot de passe !</p>
        <p>Cordialement,<br>L'équipe de PinPon45</p>
        <img src="https://sdis45.com/wp-content/themes/sdis45/assets/img/logo/logo-loiret.png">
    </body>
    </html>
    """

    msg.attach(MIMEText(message, 'html'))
    mailserver = smtplib.SMTP('smtp.gmail.com', 587)
    mailserver.starttls()
    mailserver.login('pinpinpinponponpon45@gmail.com', 'leoawgejhmmlhwyy')
    mailserver.sendmail('pinpinpinponponpon45@gmail.com', destinataire,
                        msg.as_string())
    mailserver.quit()

def mail_refuse(destinataire):
    msg = MIMEMultipart()
    msg['From'] = 'pinpinpinponponpon45@gmail.com'
    msg['To'] = destinataire
    msg['Subject'] = 'Votre demande a été refusée'

    message = """
    <html>
        <head>
            <style>
                img {
                    width: 100px;
                }

            </style>
        </head>
    <body>
        <p>Bonjour,</p>
        <p>Votre demande a été refusée.</p>
        <p>Nous vous invitons à réessayer ultérieurement.</p>
        <p>Cordialement,<br>L'équipe de PinPon45</p>
        <img src="https://sdis45.com/wp-content/themes/sdis45/assets/img/logo/logo-loiret.png">
    </body>
    </html>
    """

    msg.attach(MIMEText(message, 'html'))
    mailserver = smtplib.SMTP('smtp.gmail.com', 587)
    mailserver.starttls()
    mailserver.login('pinpinpinponponpon45@gmail.com', 'leoawgejhmmlhwyy')
    mailserver.sendmail('pinpinpinponponpon45@gmail.com', destinataire,
                        msg.as_string())
    mailserver.quit()
