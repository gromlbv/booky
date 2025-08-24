import sys
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText

from env_service import getenv

SMTPserver =   'smtp.gmail.com'
PORT =         465
USERNAME =     'seniwave.agency@seniwave.com'
PASSWORD =     getenv('MAIL_PASSWORD')

SUBJECT =      'Your Meeting Code'
SENDER =       'noreply@seniwave.com'

text_subtype = 'html'

def send_code(destination, code):
    code = 5520
    send_mail(code, destination)

def send_mail(code, destination):
    msg = MIMEText(f"""\

    <h1>{SUBJECT}</h1>
    <p>This is a test message from SeniWave</p>
    <p>Your code is <b>{code}</b></p>
    <hr style="opacity: 0.2;">
    <a href="https://meet.seniwave.com/rooms/{code}" style="margin-top: 18px; color: #ffffff; text-decoration: none; background-color: #5f00ff; padding: 10px 20px; border-radius: 24px; display: inline-block;" font-size="18px">Join meeting</a>

    """, text_subtype)
    msg['Subject'] = SUBJECT
    msg['From']    = SENDER
    
    conn = SMTP(SMTPserver, PORT)
    conn.set_debuglevel(True)
    conn.login(USERNAME, PASSWORD)
    try:
        conn.sendmail(SENDER, destination, msg.as_string())
    except:
        print("mail failed; %s" % "CUSTOM_ERROR", sys.exc_info()[1])
    finally:
        conn.quit()
        print("mail sent")

send_code("me@lbvo.ru", 5520)