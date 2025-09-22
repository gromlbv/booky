from flask import jsonify, session
from datetime import datetime, timedelta

def json_response(type_=None, message=None, icon=None, redirect_to=None):
    return jsonify({
        'type': type_,  # 'error', 'warning', 'info', 'success'
        'message': message,
        'icon': icon,
        'redirect_to': redirect_to
    })

def format_time(time):
    return f"{time // 60:02d}:{time % 60:02d}"

def format_time_with_timezone(minutes, timezone_offset=None):
    if timezone_offset is None:
        from flask import session
        timezone_offset = session.get('timezone', '+00:00')
    
    offset_hours = int(timezone_offset[1:3]) if timezone_offset.startswith('+') else -int(timezone_offset[1:3])
    offset_minutes = int(timezone_offset[4:6]) if len(timezone_offset) > 4 else 0
    
    total_offset = offset_hours * 60 + offset_minutes
    if timezone_offset.startswith('-'):
        total_offset = -total_offset
    
    adjusted_minutes = minutes + total_offset
    
    if adjusted_minutes < 0:
        adjusted_minutes += 24 * 60
    elif adjusted_minutes >= 24 * 60:
        adjusted_minutes -= 24 * 60
    
    hours = adjusted_minutes // 60
    mins = adjusted_minutes % 60
    return f"{hours:02d}:{mins:02d}"

def format_date_timezone(date, start_time, end_time):
    user_timezone = session.get('timezone', '+00:00')
    
    offset_hours = int(user_timezone[1:3]) if user_timezone.startswith('+') else -int(user_timezone[1:3])
    offset_minutes = int(user_timezone[4:6]) if len(user_timezone) > 4 else 0
    total_offset = offset_hours * 60 + offset_minutes
    if user_timezone.startswith('-'):
        total_offset = -total_offset
    
    start_adjusted = start_time + total_offset
    end_adjusted = end_time + total_offset
    
    start_day = start_adjusted // (24 * 60)
    end_day = end_adjusted // (24 * 60)
    
    if start_day == end_day:
        return date.strftime('%b %d, %Y')
    elif start_day + 1 == end_day:
        next_day = date + timedelta(days=1)
        return f"{date.strftime('%b %d')}-{next_day.strftime('%b %d, %Y')}"
    else:
        return date.strftime('%b %d, %Y')

def format_time_timezone(minutes):
    user_timezone = session.get('timezone', '+00:00')
    
    offset_hours = int(user_timezone[1:3]) if user_timezone.startswith('+') else -int(user_timezone[1:3])
    offset_minutes = int(user_timezone[4:6]) if len(user_timezone) > 4 else 0
    total_offset = offset_hours * 60 + offset_minutes
    if user_timezone.startswith('-'):
        total_offset = -total_offset
    
    adjusted_minutes = minutes + total_offset
    adjusted_minutes = adjusted_minutes % (24 * 60)
    
    hours = adjusted_minutes // 60
    mins = adjusted_minutes % 60
    return f"{hours:02d}:{mins:02d}"

def format_date(date):
    return date.strftime('%B %d, %Y')

def format_date_short(date):
    return date.strftime('%b %d, %Y')

def format_date_for_api(date):
    date = datetime.strptime(date, '%Y-%m-%d')