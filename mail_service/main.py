def get_celery_app():
    from celery_config import celery_app
    return celery_app
from mail_service.config import TEMPLATE_PATHS
from mail_service.utils import load_mjml_template
from mail_service.template_processor import process_template
from models import MeetingRequest
import mjml

def send_code(user):
    user_data = {
        'email': user.email,
        'name': user.name,
        'services': user.services,
        'message': user.message,
        'date': user.date,
        'start_time': user.start_time,
        'end_time': user.end_time,
        'code': user.code
    }
    
    meeting_request = MeetingRequest.query.filter_by(meet_code=user.code).first()
    if not meeting_request:
        send_fallback_email(user_data)
        return
    
    template_path = TEMPLATE_PATHS['mjml_code']
    mjml_template = load_mjml_template(template_path)
    
    if not mjml_template:
        send_fallback_email(user_data)
        return
    
    template_data = process_template(user_data, meeting_request)
    mjml_template = mjml_template.format(**template_data)
    result = mjml.mjml_to_html(mjml_template)
    content = result['html']
    
    get_celery_app().send_task('send_email', args=[
        user.email, 'Meeting with SeniWave', content, 'html'
    ])

def send_fallback_email(user_data):
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
        user_data['email'], subject, content, 'html'
    ])

def send_report_copy(user):
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
        user.email, subject, content, 'html'
    ])

def send_report(user):
    subject = 'New report (book.seniwave.com)'
    content = f"""\
    <h1>New report (book.seniwave.com)</h1>
    <p>Name: {user.name}</p>
    <p>Email: {user.email}</p>
    <p>Message: {user.message}</p>
    """
    
    get_celery_app().send_task('send_email', args=[
        'me@lbvo.ru', 
        subject, 
        content, 
        'html'
    ])
    send_report_copy(user)

def send_reminder(user):
    user_data = {
        'email': user.email,
        'name': user.name,
        'services': user.services,
        'message': user.message,
        'date': user.date,
        'start_time': user.start_time,
        'end_time': user.end_time,
        'code': user.code
    }
    
    meeting_request = MeetingRequest.query.filter_by(meet_code=user.code).first()
    if not meeting_request:
        send_fallback_email(user_data)
        return
    
    template_path = TEMPLATE_PATHS['mjml_reminder']
    mjml_template = load_mjml_template(template_path)
    
    if not mjml_template:
        send_fallback_email(user_data)
        return
    
    template_data = process_template(user_data, meeting_request)
    mjml_template = mjml_template.format(**template_data)
    result = mjml.mjml_to_html(mjml_template)
    content = result['html']
    
    get_celery_app().send_task('send_email', args=[
        user.email, 'Reminding you of your meeting with SeniWave', content, 'html'
    ])