from models import db, MeetingRequest, CalendarDay, TimeSpan
from datetime import date, timedelta
from flask import Flask
from os import getenv

def create_test_meetings():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv('DATABASE_URI', 'sqlite:///instance/database.db')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    with app.app_context():
        db.init_app(app)
        
        # Ищем следующую доступную дату в календаре
        today = date.today()
        calendar_day = CalendarDay.query.filter(CalendarDay.date >= today).first()
        
        if not calendar_day:
            print("Нет доступных дат в календаре!")
            return
        
        # Ищем доступный временной слот для этой даты
        time_span = TimeSpan.query.filter(
            TimeSpan.day_of_week_id == calendar_day.day_of_week_id,
            TimeSpan.is_working == True
        ).first()
        
        if not time_span:
            print("Нет доступных временных слотов!")
            return
        
        # Создаем тестовую встречу
        meeting = MeetingRequest(
            name="Тестовый пользователь",
            email="test@example.com",
            services="Тестовая услуга",
            message="Тестовое сообщение",
            time_span=time_span,
            calendar_day=calendar_day
        )
        meeting.set_meet_code()
        
        db.session.add(meeting)
        db.session.commit()
        
        start_hours = time_span.start // 60
        start_minutes = time_span.start % 60
        
        print(f"Создана тестовая встреча на {calendar_day.date} в {start_hours:02d}:{start_minutes:02d}")
        print(f"Код встречи: {meeting.meet_code}")

if __name__ == "__main__":
    create_test_meetings()
