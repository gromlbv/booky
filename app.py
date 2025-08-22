from flask import Flask
from flask import render_template, session, request, flash, redirect, jsonify, url_for, send_from_directory

import utils
from utils import json_response

import mydb as db

from mysecurity import verify, decode
from models import create_app, create_tables
from upload import upload_image, upload_file, upload_unity_build

import redis

from functools import wraps


app = Flask(__name__)
create_app(app)

app.secret_key = 'localtesting'

r = redis.Redis()



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


@app.route('/')
def index():
    return render_template("index.html")


@app.get('/admin')
def admin():
    return render_template("admin.html")

@app.post("/api/init/all",)
def init_all():
    db.init_all()
    return "<span class='post-result' id='init-status'>DONE</span>"

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
            print(f"init_days: set {day.id} to working")
            day.set_to_working()
        else:
            print(f"init_days: set {day.id} to not working")
            day.set_to_not_working()

    database.session.commit()

    return "<span class='post-result' id='span-status'>DONE</span>"

from models import DayOfWeek, TimeSpan
from datetime import datetime

@app.route("/api/available")
def available_slots():
    date_str = request.args.get("date")  # format 2025-08-05
    if date_str is not None:
        dow = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    else:
        return "<p>Choose a date</p>"
    
    day_of_week = DayOfWeek.query.get(dow + 1)
    if not day_of_week or not day_of_week.is_working:
        return "<p>No working slots this day</p>"

    time_spans = db.get_available_time_spans(dow)

    if not time_spans:
        return "<p>No available slots</p>"

    html = "<ul>"
    for span in time_spans:
        start_h = span.start // 60
        start_m = span.start % 60
        end_h = span.end // 60
        end_m = span.end % 60
        html += f"<li>{start_h:02}:{start_m:02} – {end_h:02}:{end_m:02}</li>"
    html += "</ul>"

    return html


if __name__ == "__main__":
    with app.app_context():
        create_tables()
    app.run(debug=True, port=5200, host='0.0.0.0')