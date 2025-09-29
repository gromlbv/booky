from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from models import db, DayOfWeek, TimeSpan, CalendarDay, MeetingRequest
from models import db

from mysecurity import myhash, verify, encode


def save_to_db(instance):
    db.session.add(instance)
    db.session.commit()


# config

DEFAULT_TIME_SPAN_SIZE = 30
DEFAULT_BREAK_SIZE = 15

WORK_START = 9 * 60
WORK_END = 19 * 60


def clear_time_spans():
    TimeSpan.query.delete()
    db.session.commit()

def clear_days_of_week():
    DayOfWeek.query.delete()
    db.session.commit()

def generate_time_spans_for_day(day_of_week, span_size, break_size):
    start = WORK_START
    while start + span_size + break_size <= WORK_END:
        span = TimeSpan(start=start, end=start + span_size)
        span.day_of_week = day_of_week
        span.is_working = False
        db.session.add(span)
        start += span_size + break_size

def set_work_time(start, end, time_span_size, break_size):
    current = start
    while current < end:
        spans = TimeSpan.query.filter(TimeSpan.start >= current, TimeSpan.start < current + time_span_size).all()
        for span in spans:
            span.is_working = True
        current += time_span_size + break_size
        print(f"set_work_time: set working for {current//60}:{current%60:02d}")
        
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
    calendar_day = CalendarDay.query.filter_by(day_of_week=day_of_week).first()
    #if calendar_day.is_holiday:
        #return []
    if not day_of_week.is_working:
        return []
    return TimeSpan.query.filter_by(day_of_week=day_of_week, is_working=True).all()



def get_meeting_request(id):
    return MeetingRequest.query.filter_by(id=id).first()