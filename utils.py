from flask import jsonify, session
from datetime import datetime, timedelta

def json_response(type_=None, message=None, icon=None, redirect_to=None):
    return jsonify({
        'type': type_,  # 'error', 'warning', 'info', 'success'
        'message': message,
        'icon': icon,
        'redirect_to': redirect_to
    })

# 10:00
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

def format_date_timezone_localized(date, start_time, end_time, lang='en', timezone='+00:00'):
    user_timezone = timezone
    
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
        return format_date_short_localized(date, lang)
    elif start_day + 1 == end_day:
        next_day = date + timedelta(days=1)
        return f"{format_date_short_localized(date, lang)}-{format_date_short_localized(next_day, lang)}"
    else:
        return f"{format_date_short_localized(date, lang)}-{format_date_short_localized(date + timedelta(days=end_day), lang)}"

# 10:00
def format_time_timezone(minutes, timezone=None):
    user_timezone = timezone or session.get('timezone', '+00:00')
    
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

# September 29, 2025
def format_date(date):
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    return date.strftime('%B %d, %Y')

# Sep 29, 2025
def format_date_short(date):
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    return date.strftime('%b %d, %Y')

# Sep 29, 2025
def format_date_localized(date, lang='en', format_type='short'):
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    if lang == 'ru':
        if format_type == 'full':
            months_ru = {
                1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
                5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
                9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
            }
            return f"{date.day} {months_ru[date.month]} {date.year}"
        else:  # short
            months_ru_short = {
                1: 'янв', 2: 'фев', 3: 'мар', 4: 'апр',
                5: 'мая', 6: 'июн', 7: 'июл', 8: 'авг',
                9: 'сен', 10: 'окт', 11: 'ноя', 12: 'дек'
            }
            return f"{date.day} {months_ru_short[date.month]} {date.year}"
    else:
        if format_type == 'full':
            return date.strftime('%B %d, %Y')
        else:  # short
            return date.strftime('%b %d, %Y')

# 2025-09-29
def format_date_for_api(date):
    date = datetime.strptime(date, '%Y-%m-%d')