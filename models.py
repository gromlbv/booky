import random
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from sqlalchemy.orm import Mapped, relationship


db = SQLAlchemy()

def migrate(app, db):
    Migrate(app, db)

def create_app(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
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
    
    def set_to_working(self):
        self.is_working = True

    def set_to_not_working(self):
        self.is_working = False

class Day(db.Model):
    __tablename__ = 'days'
    id = db.Column(db.Integer, primary_key=True)

    is_holiday = db.Column(db.Boolean, default=True, nullable=False)

    day_of_week_id = db.Column(db.Integer, db.ForeignKey('days_of_week.id'), nullable=False)
    day_of_week = relationship("DayOfWeek", backref="days")

    def __init__(self, is_holiday, day_of_week):
        self.is_holiday = is_holiday
        self.day_of_week = day_of_week

    def set_to_holiday(self):
        self.is_holiday = True
     
    def remove_holiday(self):
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

    def set_to_working(self):
        self.is_working = True


class MeetingRequest(db.Model):
    __tablename__ = 'meeting_requests'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    text_problem = db.Column(db.String)

    timespan_id = db.Column(db.Integer, db.ForeignKey('time_spans.id'), nullable=False)
    time_span = relationship('TimeSpan', backref='meeting_requests')

    meet_code = db.Column(db.Integer)

    def __init__(self, name, email, text_problem, time_span):
        self.name = name
        self.email = email
        self.text_problem = text_problem
        self.time_span = time_span

    def set_meet_code(self):
        self.meet_code = random.randint(0000, 9999)

    def cancel(self):
        db.session.delete(self)
        db.session.commit()