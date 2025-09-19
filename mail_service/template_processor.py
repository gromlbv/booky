from mail_service.utils import calculate_time_until_meeting, mask_email, calculate_duration
from utils import format_date
from datetime import datetime

def process_template(user_data, meeting_request):
    time_until = calculate_time_until_meeting(user_data['date'], user_data['start_time'])
    
    date_str = user_data['date']
    if '-' in date_str:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
    
    date = format_date(date_obj)
    
    return {
        'name': user_data['name'],
        'email_masked': mask_email(user_data['email']),
        'date': date,
        'start_time': user_data['start_time'],
        'end_time': user_data['end_time'], 
        'duration': calculate_duration(user_data['start_time'], user_data['end_time']),
        'meeting_code': user_data['code'],
        'meeting_id': meeting_request.id,
        'services': user_data['services'],
        'message': user_data['message'],
        'days': f"{time_until['days']:02d}",
        'hours': f"{time_until['hours']:02d}",
        'minutes': f"{time_until['minutes']:02d}"
    }
