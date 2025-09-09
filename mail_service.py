import sys
import asyncio

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from env_service import getenv
from celery import Celery
from celery_config import CELERY_CONFIG


celery_app = Celery('mail_service', broker='redis://localhost:6379/0')
celery_app.conf.update(CELERY_CONFIG)


SMTPserver =   'smtp.gmail.com'
PORT =         465
USERNAME =     'seniwave.agency@seniwave.com'
PASSWORD =     getenv('EMAIL_PASSWORD')
SENDER =       'noreply@seniwave.com'

text_subtype = 'html'


@celery_app.task
def send_mail(destination, msg_content, sub):
    print(f"Sending mail to {destination} with subject {sub}")
    msg = MIMEText(msg_content, text_subtype)
    msg['Subject'] = sub
    msg['From'] = SENDER
    
    conn = SMTP(SMTPserver, PORT, timeout=30)
    conn.set_debuglevel(False)
    conn.login(USERNAME, PASSWORD or 'nopass')
    try:
        conn.sendmail(SENDER, destination, msg.as_string())
        print("mail sent successfully")
        return True
    except Exception as e:
        print(f"mail failed: {e}")
        return False
    finally:
        conn.quit()


class MailUser:
    name = ''
    email = ''
    service = ''
    message = ''
    date = ''
    start_time = ''
    end_time = ''
    code = ''

    def __init__(self, email, name, service, message, date, start_time, end_time, code):
        self.name = name
        self.email = email
        self.service = service
        self.message = message
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.code = code

    def send_code(self):
        send_code(MailUser)


class MailReport:
    name = ''
    email = ''
    message = ''

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

    def send_report(self):
        send_report(MailReport)



def send_code(user):
    destination = user.email
    subject = 'Your Meeting Code'
    letter = f"""\
    <h1>Hello, {user.name}!</h1>
    <p>This is a test message from SeniWave</p>
    <p>Date: {user.date}</p>
    <p>Time: {user.start_time} - {user.end_time}</p>
    <p>Service: {user.service}</p>
    <p>Message: {user.message}</p>
    <p>Your code is <b>{user.code}</b></p>
    <hr style="opacity: 0.2;">
    <a href="https://meet.seniwave.com/rooms/{user.code}" style="margin-top: 18px; color: #ffffff; text-decoration: none; background-color: #5f00ff; padding: 10px 20px; border-radius: 24px; display: inline-block;" font-size="18px">Join meeting</a>
    """

    send_mail.delay(destination, letter, subject) # type: ignore

def send_report_copy(user):
    destination = user.email
    subject = 'Thank you for your report! (book.seniwave.com)'
    letter = f"""\
    <h1>Thank you for your report!</h1>
    <p>We will look into it as soon as possible.</p>    
    <p>If you have any questions, please contact us at <a href="mailto:support@seniwave.com">support@seniwave.com</a></p>
    <p>Thank you for your understanding.</p>
    <hr style="opacity: 0.2;">
    <p>This is an automated message. Please do not reply to this email.</p>
    """

    send_mail.delay(destination, letter, subject) # type: ignore

def send_report(user):
    destination = 'me@lbvo.ru'
    subject = 'New report (book.seniwave.com)'
    letter = f"""\
    <h1>New report (book.seniwave.com)</h1>
    <p>Name: {user.name}</p>
    <p>Email: {user.email}</p>
    <p>Message: {user.message}</p>
    """

    send_mail.delay(destination, letter, subject) # type: ignore
    send_report_copy(user)