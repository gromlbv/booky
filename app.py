from flask import Flask
from flask import render_template, session, request, flash, redirect, jsonify, url_for, send_from_directory

import utils
from utils import json_response

from mysecurity import verify, decode
from models import create_app, create_tables
from upload import upload_image, upload_file, upload_unity_build

import redis

from functools import wraps

from datetime import datetime

from filters import init_filters


app = Flask(__name__)
create_app(app)

app.secret_key = 'localtesting'

init_filters(app)

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
                    'message': 'Слишком много запросов!'
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
@rate_limit()
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    with app.app_context():
        create_tables()
    app.run(debug=True, port=5200, host='0.0.0.0')