import os
from datetime import datetime

def load_mjml_template(template_path):
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"template not found: {template_path}")
        return None
    except Exception as e:
        print(f"error loading template: {e}")
        return None

def calculate_time_until_meeting(meeting_date, meeting_time):
    try:
        meeting_datetime = datetime.strptime(f"{meeting_date} {meeting_time}", "%Y-%m-%d %H:%M")
        now = datetime.now()
        time_diff = meeting_datetime - now
        
        if time_diff.total_seconds() < 0:
            return {"days": 0, "hours": 0, "minutes": 0}
        
        total_seconds = int(time_diff.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        
        return {
            "days": days,
            "hours": hours, 
            "minutes": minutes
        }
    except Exception as e:
        print(f"Error calculating time until meeting: {e}")
        return {"days": 0, "hours": 0, "minutes": 0}

def mask_email(email):
    email_parts = email.split('@')
    if len(email_parts) != 2:
        return email
    
    username = email_parts[0]
    domain = email_parts[1]
    
    if len(username) > 2:
        masked_username = username[:2] + '*' * (len(username) - 2)
    else:
        masked_username = username
    
    if len(domain) > 4:
        masked_domain = domain[:2] + '*' * (len(domain) - 4) + domain[-2:]
    else:
        masked_domain = domain
    
    return f"{masked_username}@{masked_domain}"

def calculate_duration(start_time, end_time):
    try:
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))
        duration_minutes = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
        return f"{duration_minutes} minutes"
    except (ValueError, AttributeError):
        return "30 minutes"

