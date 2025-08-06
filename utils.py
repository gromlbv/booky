from flask import jsonify

import mydb as db

import re

def json_response(type_=None, message=None, icon=None, redirect_to=None):
    return jsonify({
        'type': type_,  # 'error', 'warning', 'info', 'success'
        'message': message,
        'icon': icon,  # upcoming, None to use from 'type'
        'redirect_to': redirect_to
    })
