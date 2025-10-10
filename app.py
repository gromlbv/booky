import os
import json
from os import getenv
from functools import wraps
from datetime import datetime, timedelta

import redis
from flask import Flask, render_template, session, request, redirect, url_for, send_from_directory, jsonify

import mydb as db
from utils import *
from mysecurity import verify
from models import create_app, create_tables, TimeSpan, CalendarDay
from mail_service import MailUser, MailReport
from ics_service.service import create_event


app = Flask(__name__)
create_app(app)

with app.app_context():
    create_tables()

app.secret_key = getenv('SECRET_KEY')
 
@app.template_global()
def format_time_tz(minutes):
    return format_time_with_timezone(minutes)

@app.template_global()
def format_date_localized_template(date, format_type='short'):
    lang = get_user_language()
    return format_date_localized(date, lang, format_type)

def get_user_language():
    if 'language' in session:
        return session['language']
    
    if request.headers.get('HX-Request'):
        return session.get('language', 'en')
    
    accept_lang = request.headers.get('Accept-Language', 'en')
    if accept_lang.startswith('ru'):
        return 'ru'
    return 'en'

def t(key, lang=None):
    if lang is None:
        lang = get_user_language()
    
    try:
        with open('static/translations/translations.json', 'r', encoding='utf-8') as f:
            translations = json.load(f)
        return translations.get(lang, {}).get(key, key)
    except:
        return key

@app.template_global()
def translate_key(key, lang=None):
    return t(key, lang)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=12)

r = redis.Redis()


class ReturnTemplate:
    def __init__(self, name=''):
        self.name = name
    def __call__(self, **kwds) -> str:
        return render_template(f"{self.name}.j2", **kwds, request=request)
    def __getattr__(self, name):
        return ReturnTemplate(self.name + '/' + name)
    
R = ReturnTemplate()


def rate_limit(timeout=1, max_attempts=5, reply='', reply_func=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_ip = request.remote_addr
            if not user_ip:
                return json_response({
                    'type': 'error',
                    'message': f'{t("something_wrong")} <a href="https://seniwave.t.me">{t("support_link")}</a>'
                })

            counter_key = f"rl_counter:{user_ip}"
            block_key = f"rl_block:{user_ip}"

            if r.exists(block_key):
                if reply_func:
                    return reply_func()
                elif reply:
                    return reply
                return json_response({
                    'type': 'warning',
                    'message': t('too_much_requests')
                })

            attempts = r.incr(counter_key)
            attempts_int = int(str(attempts))

            if attempts == 1:
                r.expire(counter_key, timeout)
            if attempts_int > max_attempts:
                r.setex(block_key, timeout, "blocked")
                if reply_func:
                    return reply_func()
                elif reply:
                    return reply
                return json_response({
                    'type': 'warning',
                    'message': t('too_much_requests')
                })
            return f(*args, **kwargs)
        return wrapper
    return decorator

def is_loggined():
    if 'token' in session:
        user_token = session['token']
        if verify(user_token) == False:
            session.pop('token', None)
        else:
            return True
    return False



# MAIN

@app.route('/')
def index():
    get_referrer()
    if 'meeting_request_id' in session:
        return redirect(url_for('confirmed', id=session['meeting_request_id']))

    user_timezone = get_user_timezone()
    now = datetime.now()
    
    # if last month day > show next month
    tomorrow = now + timedelta(days=1)
    if tomorrow.month != now.month:
        display_date = tomorrow
    else:
        display_date = now
    
    return R.index(year=display_date.year, month=display_date.month, user_timezone=user_timezone)

@app.route('/debug')
def debug():
    return R.debug()

@app.get('/report')
def report():
    return R.report()

@app.post('/report')
def report_post():
    mail_report = MailReport(name=request.form.get('name'), email=request.form.get('email'), message=request.form.get('message'))
    mail_report.send_report()
    return 'OK'

@app.get('/support')
def support():
    return redirect('https://seniwave.com/contact')


def get_user_timezone():
    return session.get('timezone', '+00:00')

def set_user_timezone(timezone):
    if not timezone:
        return False, "Timezone is required"
    session['timezone'] = timezone
    return True, f"Timezone set to {timezone}"

@app.post('/set-timezone')
def set_timezone():
    timezone = request.form.get("timezone")
    success, message = set_user_timezone(timezone)
    
    if not success:
        if request.headers.get('HX-Request'):
            return f'<div class="error">{message}</div>', 400
        return message, 400
    
    if request.headers.get('HX-Request'):
        return f'''
        <div class="success-message">{message}</div>
        <script>
            setTimeout(() => {{
                window.location.reload();
            }}, 500);
        </script>
        '''
    
    return message

@app.post('/set-language')
def set_language():
    language = request.form.get("language")
    if language in ['ru', 'en']:
        session['language'] = language
        return 'OK'
    return 'Invalid language', 400

@app.get('/go-back')
def go_back():
    if referrer := session.get('referrer'):
        return redirect(referrer)
    if session.get('language') == 'ru':
        return redirect('https://seniwave.ru')
    return redirect('https://seniwave.com')

def get_referrer():
    referrer = request.referrer
    print(referrer, session.get('referrer', None))
    if not referrer:
        return
    
    referrer_domain = referrer.split('/')[2]
    clean_referrer = referrer.split(referrer_domain)[0] + referrer_domain

    allowed_domains = [
        'seniwave.com',
        'seniwave.ru',
        'seniwave.ae',
        'exposhow.ru',
    ]

    for domain in allowed_domains:
        if domain in clean_referrer:
            session['referrer'] = clean_referrer
            break
    
@app.post('/submit')
def submit_post():
    email = request.form.get('email')
    name = request.form.get('name')
    services = request.form.getlist('services')
    services_str = ', '.join(services) if services else ''
    message = request.form.get('message')
    date = request.form.get('date')
    slot_id = request.form.get('slot_id')
    
    if not email or not name or not date or not slot_id:
        return 'Not all fields are filled or something went wrong'

    time_span = TimeSpan.query.filter_by(id=int(slot_id)).first()
    if not time_span:
        return 'Time slot not found'

    date_obj = datetime.strptime(date, "%Y-%m-%d")
    calendar_day = CalendarDay.query.filter_by(date=date_obj).first()
    if not calendar_day:
        calendar_day = CalendarDay(date=date_obj)
        database.session.add(calendar_day)

    from models import MeetingRequest
    m = MeetingRequest(
        name=name, 
        email=email,
        services=services_str,
        message=message,
        time_span=time_span,
        calendar_day=calendar_day,
        user_timezone=get_user_timezone()
    )

    code = m.set_meet_code()
    database.session.add(m)
    database.session.commit()
    start_time = format_time(time_span.start)
    end_time = format_time(time_span.end)
    session['meeting_request_id'] = m.id
    
    mail_user = MailUser(
        email=email,
        name=name,
        services=services_str,
        message=message,
        date=date,
        start_time=start_time,
        end_time=end_time,
        code=code,
        meeting_id=m.id
    )

    mail_user.send_code()
    
    return redirect(url_for('confirmed', id=m.id))


@app.route('/meet/<id>')
def confirmed(id):
    m = db.get_meeting_request(id)
    if not m:
        session_meeting_request_id = session.get('meeting_request_id', None)
        if session_meeting_request_id == id:
            session.pop('meeting_request_id', None)
            return redirect(url_for('index'))
        return redirect(url_for('meeting_not_found'))

    date = m.calendar_day.date
    start_time = m.time_span.start
    end_time = m.time_span.end

    timezone = m.user_timezone
    adjusted_start_time = format_time_timezone(start_time, timezone)
    adjusted_end_time = format_time_timezone(end_time, timezone)
    start_time = adjusted_start_time
    end_time = adjusted_end_time

    return R.confirmed(meeting_request=m, date=date, start_time=start_time, end_time=end_time)


# API

from models import DayOfWeek, TimeSpan
from datetime import datetime
import calendar

@app.route("/api/cancel/<id>")
@rate_limit(timeout=5, max_attempts=1, reply_func=lambda: t('too_much_requests'))
def cancel_meeting(id):
    m = db.get_meeting_request(id)
    if not m:
        return redirect(url_for('meeting_not_found'))

    mail_user = MailUser(
        email=m.email,
        name=m.name,
        services=m.services,
        message=m.message,
        date=m.calendar_day.date,
        start_time=m.time_span.start,
        end_time=m.time_span.end,
        code=m.meet_code,
        meeting_id=m.id
    )
    mail_user.send_cancel()
    m.cancel()
    session.pop('meeting_request_id', None)

    return t('meeting_canceled')

@app.route("/api/resend/<id>")
@rate_limit(timeout=60, max_attempts=1, reply_func=lambda: t('every_60_seconds'))
def resend_code(id):
    m = db.get_meeting_request(id)
    if not m:
        return redirect(url_for('meeting_not_found'))

    date = format_date(m.calendar_day.date)
    start_time = format_time(m.time_span.start)
    end_time = format_time(m.time_span.end)

    mail_user = MailUser(
        email=m.email,
        name=m.name,
        services=m.services,
        message=m.message,
        date=date,
        start_time=start_time,
        end_time=end_time,
        code=m.meet_code,
        meeting_id=m.id
    )
    mail_user.send_code()

    return t('mail_resent')


@app.route("/api/reminder/<id>")
def reminder(id):
    m = db.get_meeting_request(id)
    if not m:
        return redirect(url_for('meeting_not_found'))

    date = format_date(m.calendar_day.date)
    start_time = format_time(m.time_span.start)
    end_time = format_time(m.time_span.end)

    mail_user = MailUser(
        email=m.email,
        name=m.name,
        services=m.services,
        message=m.message,
        date=date,
        start_time=start_time,
        end_time=end_time,
        code=m.meet_code,
        meeting_id=m.id
    )
    mail_user.send_reminder_24h()

    return t('reminder_sent')

@app.route("/api/available")
def available_slots():
    date_str = request.args.get("date")
    if date_str is not None:
        dow = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    else:
        return f"<p>{t('choose_date_htmx')}</p>"
    
    day_of_week = DayOfWeek.query.filter_by(id=dow + 1).first()
    if not day_of_week or not day_of_week.is_working:
        return f"<p>{t('no_working_slots')}</p>"

    time_spans = db.get_available_time_spans(dow)

    if not time_spans:
        return f"<p>{t('no_available_slots')}</p>"

    html = "<ul>"
    for span in time_spans:
        start_time = format_time(span.start)
        end_time = format_time(span.end)
        html += f"<li>{start_time} – {end_time}</li>"
    html += "</ul>"

    return html

@app.route("/api/time-slots/<date>")
def get_time_slots(date):
    if not date or date == 'None' or date == 'null':
        return f"<p>{t('select_date_htmx')}</p>"
    
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        dow = date_obj.weekday()
        
        day_of_week = DayOfWeek.query.filter_by(id=dow + 1).first()
        if not day_of_week or not day_of_week.is_working:
            return f'''
                <p>{t('select_time_period_htmx')} <span>{date}</span></p>
                <p class="no-slots">{t('no_slots_date')}</p>
            '''
        
        time_spans = TimeSpan.query.filter_by(
            day_of_week_id=dow + 1,
            is_working=True
        ).all()
        
        slots = []
        for span in time_spans:
            slots.append({
                'id': span.id,
                'start': format_time_with_timezone(span.start),
                'end': format_time_with_timezone(span.end),
                'start_minutes': span.start,
                'end_minutes': span.end
            })
        
        if not slots:
            return f'''
                <p>{t('select_time_period_htmx')} <span>{date}</span></p>
                <p class="no-slots">{t('no_slots_date')}</p>
            '''

        is_day_off = DayOfWeek.query.filter_by(id=dow + 1).first().is_working == False
        if is_day_off:
            return f'''
                <p>{t('select_time_period_htmx')} <span>{format_date_localized(date_obj, get_user_language(), 'short')}</span></p>
                <p class="no-slots">{t('day_off')}</p>
            '''
        
        html = f'''
            <p>{t('select_time_period_htmx')} <span>{format_date_localized(date_obj, get_user_language(), 'short')}</span></p>
            <div class="time-slots">'''
        
        for slot in slots:
            html += f'''<button class="time-slot" 
                    data-slot-id="{slot['id']}"
                    data-start="{slot['start']}"
                    data-end="{slot['end']}"
                    data-start-minutes="{slot['start_minutes']}"
                    data-end-minutes="{slot['end_minutes']}">
                {slot['start']}
            </button>'''
        
        html += '''</div>'''
        
        return html
        
    except ValueError:
        return f"<p>{t('select_date_htmx')}</p>"


@app.route("/calendar/<int:year>/<int:month>")
def calendar_page(year, month):
    return render_template("calendar_only.j2", year=year, month=month)

@app.route("/api/calendar/<int:year>/<int:month>")
def get_calendar(year, month):        
    cal = calendar.monthcalendar(year, month)
    
    today = datetime.now()
    is_current_month = today.year == year and today.month == month
    
    html = ""
    
    for week in cal:
        for day in week:
            if day == 0:
                html += '<button class="day empty" tabindex="-1" disabled></button>'
            else:
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                date_obj = datetime(year, month, day)
                dow = date_obj.weekday()
                
                day_of_week = DayOfWeek.query.filter_by(id=dow + 1).first()
                is_available = day_of_week and day_of_week.is_working
                is_today = is_current_month and today.day == day
                is_past = date_obj.date() < today.date() and is_available

                if date_obj.date() < today.date():
                    is_available = False
                if is_today:
                    is_available = False
                
                classes = ["day"]
                if is_available:
                    classes.append("available")
                if is_today:
                    classes.append("today")
                
                class_str = " ".join(classes)
                disabled = "" if is_available else "disabled"
                
                if is_today:
                    description = t("today")
                elif is_available:
                    description = t("available_booking")
                elif is_past:
                    description = t("past_day")
                else:
                    description = t("is_day_off")
                
                html += f'''<button 
                    class="{class_str}" 
                    data-date="{date_str}"
                    data-description="{description}"
                    {disabled}>
                    {day}
                </button>'''
    
    return html


def get_date_availabiltiy(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    dow = date.weekday()
    day_of_week = DayOfWeek.query.get(dow + 1)
    if not day_of_week or not day_of_week.is_working:
        return False
    return True



# CALENDAR


@app.get('/meet/<id>/get_event')
def get_event(id):
    m = db.get_meeting_request(id)
    if not m:
        return redirect(url_for('meeting_not_found'))
    
    file_path = f'ics_service/events/{id}.ics'
    if not os.path.exists(file_path):
        create_event(m)
    
    return send_from_directory(
        directory='ics_service/events',
        path=f'{id}.ics'
    )

@app.route('/api/translations')
def get_translations():
    try:
        with open('static/translations/translations.json', 'r', encoding='utf-8') as f:
            translations = json.load(f)
        return jsonify(translations)
    except Exception as e:
        return jsonify({'error': 'Failed to load translations'}), 500



# ADMIN

admin_key = getenv('ADMIN_KEY')
admin_session_key = getenv('ADMIN_SESSION_KEY')

@app.get('/admin/<key>')
def admin(key):
    if key != admin_key:
        return 'Access denied', 403
    
    session['admin_session_key'] = admin_session_key

    return R.admin()


@app.post("/api/init/all")
def init_all():
    if 'admin_session_key' not in session:
        return "ADMIN KEY ERROR"
    
    db.init_all()
    return "DONE"

from models import DayOfWeek
from models import db as database

@app.post("/api/init/spans")
def init_spans():
    if 'admin_session_key' not in session:
        return "ADMIN KEY ERROR"
    
    size = int(request.form.get("span_size", 30))
    start = int(request.form.get("start_time", 0))
    end = int(request.form.get("end_time", 24))
    break_size = int(request.form.get("break_size", 15))
    start_minutes = start * 60
    end_minutes = end * 60

    db.init_time_spans(span_size=size, break_size=break_size)
    db.set_work_time(start_minutes, end_minutes, size, break_size)

    days = DayOfWeek.query.all()
    
    for day in days:
        if f"{day.id}" in request.form:
            day.set_working()
        else:
            day.set_not_working()

    database.session.commit()

    return "<span class='post-result' id='span-status'>DONE</span>"
    

@app.route(f'/meet/<string:meet_id>/api/countdown')
@rate_limit(timeout=1, max_attempts=10)
def api_countdown(meet_id):
    cache_key = f"countdown:{meet_id}"
    cached_result = r.get(cache_key)
    
    if cached_result:
        return cached_result
    
    m = db.get_meeting_request(meet_id)
    if not m:
        result = json.dumps({'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0})
        r.setex(cache_key, 1, result)
        return result

    meeting_date = m.calendar_day.date
    start_minutes = m.time_span.start
    meeting_time = datetime.min.time().replace(
        hour=start_minutes // 60,
        minute=start_minutes % 60
    )
    
    event_date = datetime.combine(meeting_date, meeting_time)
    now = datetime.now()
    time_diff = event_date - now
    
    if time_diff.total_seconds() <= 0:
        days = hours = minutes = seconds = 0
    else:
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
    
    result = json.dumps({
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    })
    
    r.setex(cache_key, 1, result)
    return result


# service pages

@app.errorhandler(400)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('service/page_not_found.j2')

@app.route('/meet/canceled')
def meeting_cancelled():
    return render_template('service/meeting_canceled.j2')

@app.route('/meet/not-found')
def meeting_not_found():
    return render_template('service/meeting_not_found.j2')

if __name__ == "__main__":
    app.run(debug=True, port=5300, host='0.0.0.0', threaded=True)