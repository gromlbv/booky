import sys
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText

from env_service import getenv

SMTPserver =   'smtp.gmail.com'
PORT =         465
USERNAME =     'seniwave.agency@seniwave.com'
PASSWORD =     getenv('EMAIL_PASSWORD')
SENDER =       'noreply@seniwave.com'

text_subtype = 'html'


def send_mail(destination, msg, sub):
    msg = MIMEText(msg, text_subtype)
    msg['Subject'] = sub
    msg['From']    = SENDER
    
    conn = SMTP(SMTPserver, PORT)
    conn.set_debuglevel(True)
    conn.login(USERNAME, PASSWORD or 'nopass')
    try:
        conn.sendmail(SENDER, destination, msg.as_string())
    except:
        print("mail failed; %s" % "CUSTOM_ERROR", sys.exc_info()[1])
    finally:
        conn.quit()
        print("mail sent")


def send_code(destination, code, name, service, message, slot_id):
    subject = 'Your Meeting Code'
    letter = f"""\
    <h1>Hello, {name}!</h1>
    <p>This is a test message from SeniWave</p>
    <p>Your code is <b>{code}</b></p>
    <hr style="opacity: 0.2;">
    <a href="https://meet.seniwave.com/rooms/{code}" style="margin-top: 18px; color: #ffffff; text-decoration: none; background-color: #5f00ff; padding: 10px 20px; border-radius: 24px; display: inline-block;" font-size="18px">Join meeting</a>
    """

    send_mail(destination, letter, subject)

def send_report_copy(name, email, message):
    destination = email
    subject = 'Thank you for your report! (book.seniwave.com)'
    letter = f"""\
    <h1>Thank you for your report!</h1>
    <p>We will look into it as soon as possible.</p>
    <p>If you have any questions, please contact us at <a href="mailto:support@seniwave.com">support@seniwave.com</a></p>
    <p>Thank you for your understanding.</p>
    <hr style="opacity: 0.2;">
    <p>This is an automated message. Please do not reply to this email.</p>
    """

    send_mail(destination, letter, subject)

def send_report(name, email, message):
    destination = 'me@lbvo.ru'
    subject = 'New report (book.seniwave.com)'
    letter = f"""\
    <h1>New report (book.seniwave.com)</h1>
    <p>Name: {name}</p>
    <p>Email: {email}</p>
    <p>Message: {message}</p>
    """

    send_mail(destination, letter, subject)
    send_report_copy(name, email, message)