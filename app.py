from flask import Flask
from flask import render_template, session, request, flash, redirect, jsonify, url_for, send_from_directory
import os

import mydb as db

from utils import json_response, format_time, format_date
from mysecurity import verify, decode
from models import create_app, create_tables, TimeSpan, CalendarDay, MeetingRequest
from mail_service import send_code, send_report

import redis
import random

from functools import wraps
from datetime import datetime
from env_service import getenv

from ics_service.service import create_event


app = Flask(__name__)
create_app(app)

with app.app_context():
    create_tables()


app.secret_key = getenv('SECRET_KEY')

r = redis.Redis()


class ReturnTemplate:
    def __init__(self, name=''):
        self.name = name
    def __call__(self, **kwds) -> str:
        return render_template(f"{self.name}.j2", **kwds, request=request)
    def __getattr__(self, name):
        return ReturnTemplate(self.name + '/' + name)
    
R = ReturnTemplate()


def rate_limit(timeout=1, max_attempts=5):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_ip = request.remote_addr
            if not user_ip:
                return json_response({
                    'type': 'error',
                    'message': 'Что-то пошло не так <a href="https://lbv_dev.t.me">Поддержка</a>'
                })

            counter_key = f"rl_counter:{user_ip}"

            attempts = r.incr(counter_key)
            attempts_int = int(str(attempts))

            if attempts == 1:
                r.expire(counter_key, timeout)
            if attempts_int > max_attempts:
                return json_response({
                    'type': 'warning',
                    'message': 'TOO MUCH REQUESTS!'
                })

            r.setex(user_ip, timeout, "blocked")
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
    if 'meeting_request_id' in session:
        return redirect(url_for('confirmed', id=session['meeting_request_id']))

    now = datetime.now()
    return R.index(year=now.year, month=now.month)

@app.route('/debug')
def debug():
    return R.debug()

@app.get('/admin')
def admin():
    return R.admin()

@app.get('/report')
def report():
    return R.report()

@app.post('/report')
def report_post():
    send_report(name=request.form.get('name'), email=request.form.get('email'), message=request.form.get('message'))
    return 'OK'


@app.post('/submit')
def submit_post():
    email = request.form.get('email')
    name = request.form.get('name')
    service = request.form.get('service')
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

    meeting_request = MeetingRequest(
        name=name, 
        email=email,
        service=service,
        message=message,
        time_span=time_span,
        calendar_day=calendar_day
    )

    code = meeting_request.set_meet_code()
    database.session.add(meeting_request)
    database.session.commit()

    
    start_time = format_time(time_span.start)
    end_time = format_time(time_span.end)

    session['meeting_request_id'] = meeting_request.id

    send_code(
        destination=email,
        name=name,
        service=service,
        message=message,
        date=date,
        start_time=start_time,
        end_time=end_time,
        code=code)
    
    return redirect(url_for('confirmed', id=meeting_request.id))


@app.route('/meet/<id>')
def confirmed(id):
    meeting_request = MeetingRequest.query.filter_by(id=id).first()
    if not meeting_request:
        session_meeting_request_id = session.get('meeting_request_id', None)
        if session_meeting_request_id == id:
            session.pop('meeting_request_id', None)
        return 'Meeting request not found'

    date = meeting_request.calendar_day.date
    start_time = meeting_request.time_span.start
    end_time = meeting_request.time_span.end

    date = format_date(date)
    start_time = format_time(start_time)
    end_time = format_time(end_time)

    return R.confirmed(meeting_request=meeting_request, date=date, start_time=start_time, end_time=end_time)


# API

from models import DayOfWeek, TimeSpan
from datetime import datetime
import calendar


@app.route("/api/cancel/<id>")
def cancel_meeting(id):
    meeting_request = MeetingRequest.query.filter_by(id=id).first()
    if not meeting_request:
        return 'Meeting request not found', 400
    meeting_request.cancel()
    session.pop('meeting_request_id', None)
    return 'Meeting cancelled! Redirecting...'

@app.route("/api/resend/<id>")
def resend_code(id):
    meeting_request = MeetingRequest.query.filter_by(id=id).first()
    if not meeting_request:
        return 'Meeting request not found', 400

    date = format_date(meeting_request.calendar_day.date)
    start_time = format_time(meeting_request.time_span.start)
    end_time = format_time(meeting_request.time_span.end)

    send_code(meeting_request.email, meeting_request.meet_code, meeting_request.name, meeting_request.service, meeting_request.message, date, start_time, end_time)
    return 'Mail resent!'

@app.route("/api/available")
def available_slots():
    date_str = request.args.get("date")  # format 2025-08-05
    if date_str is not None:
        dow = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    else:
        return "<p>Choose a date</p>"
    
    day_of_week = DayOfWeek.query.filter_by(id=dow + 1).first()
    if not day_of_week or not day_of_week.is_working:
        return "<p>No working slots this day</p>"

    time_spans = db.get_available_time_spans(dow)

    if not time_spans:
        return "<p>No available slots</p>"

    html = "<ul>"
    for span in time_spans:
        start_time = format_time(span.start)
        end_time = format_time(span.end)
        html += f"<li>{start_time} – {end_time}</li>"
    html += "</ul>"

    return html

@app.route("/api/time-slots/<date>")
def get_time_slots(date):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        dow = date_obj.weekday()
        
        day_of_week = DayOfWeek.query.filter_by(id=dow + 1).first()
        if not day_of_week or not day_of_week.is_working:
            return f'''
                <p>Then, select a time period for <span>{date}</span></p>
                <p class="no-slots">No available time slots for this date</p>
            '''
        
        time_spans = TimeSpan.query.filter_by(
            day_of_week_id=dow + 1,
            is_working=True
        ).all()
        
        slots = []
        for span in time_spans:
            start_h = span.start // 60
            start_m = span.start % 60
            end_h = span.end // 60
            end_m = span.end % 60
            slots.append({
                'id': span.id,
                'start': f"{start_h:02}:{start_m:02}",
                'end': f"{end_h:02}:{end_m:02}",
                'start_minutes': span.start,
                'end_minutes': span.end
            })
        
        if not slots:
            return f'''
                <p>Then, select a time period for <span>{date}</span></p>
                <p class="no-slots">No available time slots for this date</p>
            '''
        
        html = f'''
            <p>Then, select a time period for <span>{date}</span></p>
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
        return "<p>Select date to continue</p>"

@app.route("/api/calendar/<int:year>/<int:month>")
def get_calendar(year, month):    
    print(f"get_calendar called with year={year}, month={month}")
    
    cal = calendar.monthcalendar(year, month)
    
    today = datetime.now()
    is_current_month = today.year == year and today.month == month
    
    html = ""

    print(f"Calendar data: {cal}")
    
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
                
                classes = ["day"]
                if is_available:
                    classes.append("available")
                if is_today:
                    classes.append("today")
                
                class_str = " ".join(classes)
                disabled = "" if is_available else "disabled"
                
                if is_today:
                    description = "Today"
                elif is_available:
                    description = "Available for booking"
                else:
                    description = "Not available"
                
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



# ADMIN

@app.post("/api/init/all",)
def init_all():
    db.init_all()
    return "DONE"

from models import DayOfWeek
from models import db as database

@app.post("/api/init/spans")
def init_spans():
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



# CALENDAR

@app.get('/meet/<id>/get_event')
def get_event(id):
    meeting_request = MeetingRequest.query.filter_by(id=id).first()
    if not meeting_request:
        return 'Meeting request not found', 400
    
    file_path = f'ics_service/events/{id}.ics'
    if not os.path.exists(file_path):
        create_event(meeting_request)
    
    return send_from_directory(
        directory='ics_service/events',
        path=f'{id}.ics'
    )



if __name__ == "__main__":
    with app.app_context():
        create_tables()
    app.run(debug=True, port=5200, host='0.0.0.0')