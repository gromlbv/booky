import random
import uuid

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from env_service import getenv


db = SQLAlchemy()

def migrate(app, db):
    Migrate(app, db)

def create_app(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv('DATABASE_URI')
    app.config ["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate(app, db)
    return app

def create_tables():
    db.create_all()



class DayOfWeek(db.Model):
    __tablename__ = 'days_of_week'
    id = db.Column(db.Integer, primary_key=True)

    is_working = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, is_working):
        self.is_working = is_working
    
    def set_working(self):
        self.is_working = True

    def set_not_working(self):
        self.is_working = False

class CalendarDay(db.Model):
    __tablename__ = 'calendar_days'
    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date, nullable=False)
    is_holiday = db.Column(db.Boolean, default=False, nullable=False)

    day_of_week_id = db.Column(db.Integer, db.ForeignKey('days_of_week.id'))
    day_of_week = relationship("DayOfWeek", backref="calendar_days")

    def __init__(self, date):
        self.date = date

    def set_holiday(self):
        self.is_holiday = True

    def set_not_holiday(self):
        self.is_holiday = False


class TimeSpan(db.Model):
    __tablename__ = 'time_spans'
    id = db.Column(db.Integer, primary_key=True)

    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)

    is_working = db.Column(db.Boolean, default=True, nullable=False)

    day_of_week_id = db.Column(db.Integer, db.ForeignKey('days_of_week.id'), nullable=False)
    day_of_week = relationship("DayOfWeek", backref="time_spans")

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def set_working(self):
        self.is_working = True

    def set_not_working(self):
        self.is_working = False


class MeetingRequest(db.Model):
    __tablename__ = 'meeting_requests'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))

    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    services = db.Column(db.String)
    message = db.Column(db.String)

    timespan_id = db.Column(db.Integer, db.ForeignKey('time_spans.id'), nullable=False)
    time_span = relationship('TimeSpan', backref='meeting_requests')

    calendar_day_id = db.Column(db.Integer, db.ForeignKey('calendar_days.id'), nullable=False)
    calendar_day = relationship('CalendarDay', backref='meeting_requests')

    meet_code = db.Column(db.Integer)

    def __init__(self, name, email, services, message, time_span, calendar_day):
        self.name = name
        self.email = email
        self.services = services
        self.message = message
        self.time_span = time_span
        self.calendar_day = calendar_day

    def set_meet_code(self):
        self.meet_code = random.randint(0000, 9999)
        return self.meet_code

    def cancel(self):
        db.session.delete(self)
        db.session.commit()