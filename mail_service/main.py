def get_celery_app():
    from celery_config import celery_app
    return celery_app
    
from mail_service.config import ADMIN_EMAIL
from mail_service.template_processor import process_mjml_template

def send_code(user):
    user_data = user.to_dict()
    email = user.email
    subject = 'Meeting with SeniWave'
    content = None
    content = process_mjml_template('mjml_code', user_data)
    
    if not content:
        send_fallback_email(user_data)
        return
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])
    send_admin(user)

def send_cancel(user):
    user_data = user.to_dict()
    email = user.email
    subject = 'Meeting with SeniWave Canceled'
    content = process_mjml_template('mjml_cancel', user_data)
    if not content:
        return
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])
    send_admin_cancel(user)

def send_reminder_24h(user):
    user_data = user.to_dict()
    email = user.email
    subject = 'Reminding you of your meeting with SeniWave'
    content = process_mjml_template('mjml_reminder_24h', user_data)
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])

def send_reminder_1h(user):
    user_data = user.to_dict()
    email = user.email
    subject = 'Meeting with SeniWave — Starts soon!'
    content = process_mjml_template('mjml_reminder_1h', user_data)
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])


def send_fallback_email(user_data):
    email = user_data['email']
    subject = 'Meeting with SeniWave'
    content = f"""
    <h1>Hello, {user_data['name']}!</h1>
    <p>Your meeting code is: <b>{user_data['code']}</b></p>
    <p>Date: {user_data['date']}</p>
    <p>Time: {user_data['start_time']} - {user_data['end_time']}</p>
    <p>Services: {user_data['services']}</p>
    <p>Message: {user_data['message']}</p>
    <a href="https://meet.seniwave.com/rooms/{user_data['code']}">Join meeting</a>
    """
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])

def send_report(user):
    email = user.email
    subject = 'Thank you for your report! (book.seniwave.com)'
    content = f"""\
    <h1>Thank you for your report!</h1>
    <p>We will look into it as soon as possible.</p>    
    <p>If you have any questions, please contact us at <a href="mailto:support@seniwave.com">support@seniwave.com</a></p>
    <p>Thank you for your understanding.</p>
    <hr style="opacity: 0.2;">
    <p>This is an automated message. Please do not reply to this email.</p>
    """
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])
    send_report_admin(user)



def send_admin(user):
    user_data = user.to_dict()
    email = ADMIN_EMAIL
    subject = 'New Meeting booked'
    content = process_mjml_template('mjml_admin', user_data)
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])

def send_admin_cancel(user):
    user_data = user.to_dict()
    email = ADMIN_EMAIL
    subject = f'Meeting {user.code} Canceled'
    content = process_mjml_template('mjml_admin_cancel', user_data)
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])

def send_report_admin(user):
    email = ADMIN_EMAIL
    subject = 'New report (book.seniwave.com)'
    content = f"""\
    <h1>New report (book.seniwave.com)</h1>
    <p>Name: {user.name}</p>
    <p>Email: {user.email}</p>
    <p>Message: {user.message}</p>
    """
    
    get_celery_app().send_task('send_email', args=[
        email, subject, content
    ])