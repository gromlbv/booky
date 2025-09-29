from mail_service.utils import calculate_time_until_meeting, mask_email, calculate_duration
from utils import format_date
from datetime import datetime
from mail_service.config import TEMPLATE_PATHS
from mail_service.utils import load_mjml_template
import mjml

def process_template(user_data):
    date_str = str(user_data['date'])
    
    if '-' in date_str:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
    
    date_for_calc = date_obj.strftime('%Y-%m-%d')
    time_until = calculate_time_until_meeting(date_for_calc, user_data['start_time'])
    
    date = format_date(date_obj)
    
    return {
        'name': user_data['name'],
        'email': user_data['email'],
        'email_masked': mask_email(user_data['email']),
        'date': date,
        'start_time': user_data['start_time'],
        'end_time': user_data['end_time'], 
        'duration': calculate_duration(user_data['start_time'], user_data['end_time']),
        'meeting_code': user_data['code'],
        'meeting_id': user_data['meeting_id'],
        'services': user_data['services'],
        'message': user_data['message'],
        'user_timezone': user_data['user_timezone'],
        'days': f"{time_until['days']:02d}",
        'hours': f"{time_until['hours']:02d}",
        'minutes': f"{time_until['minutes']:02d}"
    }

def process_mjml_template(template_name, user_data):
    template_path = TEMPLATE_PATHS[template_name]
    mjml_template = load_mjml_template(template_path)
    
    if not mjml_template:
        return None
    
    template_data = process_template(user_data)
    mjml_template = mjml_template.format(**template_data)
    result = mjml.mjml_to_html(mjml_template)
    return result['html']
