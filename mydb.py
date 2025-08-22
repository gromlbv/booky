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

DEFAULT_TIME_SPAN_SIZE = 30
DEFAULT_BREAK_SIZE = 15

WORK_START = 0 * 60
WORK_END = 24 * 60
#WORK_START = 9 * 60
#WORK_END = 18 * 60


def clear_time_spans():
    TimeSpan.query.delete()
    db.session.commit()

def clear_days_of_week():
    DayOfWeek.query.delete()
    db.session.commit()

def generate_time_spans_for_day(day_of_week, span_size, break_size):
    start = WORK_START
    count = 0
    while start + span_size + break_size <= WORK_END:
        span = TimeSpan(start=start, end=start + span_size)
        span.day_of_week = day_of_week
        span.is_working = False
        db.session.add(span)
        start += span_size + break_size
        count += 1

def set_work_time(start, end, time_span_size, break_time):
    count = 0
    start = start
    while start < end:
        spans = TimeSpan.query.filter_by(start=start).all()
        for span in spans:
            span.is_working = True
        start += time_span_size + break_time
        print(f"set_work_time: set working for {start//60}:{start%60:02d}")
        count += 1
        
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

def init_days_of_week():
    clear_days_of_week()

    for i in range(7):
        is_working = i < 5
        day = DayOfWeek(is_working=is_working)
        db.session.add(day)

    db.session.commit()


def init_time_spans(span_size = DEFAULT_TIME_SPAN_SIZE, break_size = DEFAULT_BREAK_SIZE):
    clear_time_spans()

    days = DayOfWeek.query.all()
    for day in days:
        generate_time_spans_for_day(day, span_size, break_size)

    db.session.commit()


def init_all(span_size = DEFAULT_TIME_SPAN_SIZE):
    init_days_of_week()
    init_time_spans(span_size=span_size)




def get_available_time_spans(date):
    print(f"get_available_time_spans: date={date}")
    day_of_week = DayOfWeek.query.filter_by(id=date).first()
    if day_of_week is None:
        return []
    #if day_of_week.is_holiday:
        #return []
    if not day_of_week.is_working:
        return []
    return TimeSpan.query.filter_by(day_of_week=day_of_week, is_working=True).all()