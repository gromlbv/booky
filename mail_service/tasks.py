from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from .config import SMTP_CONFIG

def send_email(destination, subject, content, content_type='html'):
    print(f"Sending {content_type} email to {destination} with subject: {subject}")
    
    msg = MIMEText(content, content_type)
    msg['Subject'] = subject
    msg['From'] = SMTP_CONFIG['sender']
    
    conn = SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'], timeout=30)
    conn.set_debuglevel(False)
    conn.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
    
    try:
        conn.sendmail(SMTP_CONFIG['sender'], destination, msg.as_string())
        print(f"Email sent successfully to {destination}")
        return True
    except Exception as e:
        print(f"Email failed to {destination}: {e}")
        return False
    finally:
        conn.quit()