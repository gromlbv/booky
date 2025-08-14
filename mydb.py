from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from models import db, DayOfWeek, TimeSpan
from models import db

from mysecurity import myhash, verify, encode


def save_to_db(instance):
    db.session.add(instance)
    db.session.commit()


# config

TIME_SPAN_SIZE = 30
WORK_START = 9 * 60
WORK_END = 18 * 60



def clear_timespans():
    TimeSpan.query.delete()
    db.session.commit()

def clear_days_of_week():
    DayOfWeek.query.delete()
    db.session.commit()


def generate_time_spans_for_day(day_of_week, span_size):
    start = WORK_START
    while start + span_size <= WORK_END:
        span = TimeSpan(start=start, end=start + span_size)
        span.day_of_week = day_of_week
        db.session.add(span)
        start += span_size


def init_days_of_week():
    clear_days_of_week()

    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_names_short = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

    for i in range(7):
        is_working = i < 5
        day = DayOfWeek(name=day_names[i], name_short=day_names_short[i], is_working=is_working)
        db.session.add(day)

    db.session.commit()


def init_time_spans(span_size = TIME_SPAN_SIZE, start_time = WORK_START, end_time = WORK_END):
    clear_timespans()

    days = DayOfWeek.query.all()
    for day in days:
        generate_time_spans_for_day(day, span_size, start_time, end_time)

    db.session.commit()


def init_all(span_size = TIME_SPAN_SIZE):
    init_days_of_week()
    init_time_spans(span_size=span_size)