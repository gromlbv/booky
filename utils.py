from flask import jsonify
from datetime import datetime

import mydb as db

import re

def json_response(type_=None, message=None, icon=None, redirect_to=None):
    return jsonify({
        'type': type_,  # 'error', 'warning', 'info', 'success'
        'message': message,
        'icon': icon,
        'redirect_to': redirect_to
    })


def format_time(time):
    return f"{time // 60:02d}:{time % 60:02d}"

def format_date(date):
    return date.strftime('%B %d, %Y')

def format_date_for_api(date):
    date = datetime.strptime(date, '%Y-%m-%d')
