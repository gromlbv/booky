from celery import current_app
from mail_service.utils import calculate_time_until_meeting
from models import db, MeetingRequest, CalendarDay, TimeSpan
from datetime import date, timedelta
from flask import Flask
from os import getenv

@current_app.task(name='check_and_send_reminders')
def check_and_send_reminders():
    try:
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = getenv('DATABASE_URI', 'sqlite:///instance/database.db')
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        with app.app_context():
            db.init_app(app)
            
            tomorrow = date.today() + timedelta(days=1)
            meetings = db.session.query(MeetingRequest).join(CalendarDay).join(TimeSpan).filter(
                CalendarDay.date >= date.today(),
                CalendarDay.date <= tomorrow
            ).order_by(CalendarDay.date, TimeSpan.start).all()
            
            for meeting in meetings:
                start_hours = meeting.time_span.start // 60
                start_minutes = meeting.time_span.start % 60
                end_hours = meeting.time_span.end // 60
                end_minutes = meeting.time_span.end % 60
                
                start_time = f"{start_hours:02d}:{start_minutes:02d}"
                end_time = f"{end_hours:02d}:{end_minutes:02d}"
                
                user_data = {
                    'email': meeting.email,
                    'name': meeting.name, 
                    'services': meeting.services,
                    'message': meeting.message,
                    'date': meeting.calendar_day.date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'code': meeting.meet_code
                }
                
                time_until = calculate_time_until_meeting(user_data['date'].strftime('%Y-%m-%d'), user_data['start_time'])
                total_hours = time_until['days'] * 24 + time_until['hours']
                print(f"Встреча {user_data['email']}: {total_hours} часов до начала")
                
                if 23 <= total_hours <= 25:
                    from mail_service.main import send_reminder_24h
                    from mail_service.models import MailUser
                    
                    user = MailUser(
                        email=user_data['email'],
                        name=user_data['name'],
                        services=user_data['services'],
                        message=user_data['message'],
                        date=user_data['date'],
                        start_time=user_data['start_time'],
                        end_time=user_data['end_time'],
                        code=user_data['code']
                    )
                    send_reminder_24h(user)
                    print(f"24h reminder sent to {user_data['email']}")
                
                if 0 <= total_hours <= 2:
                    from mail_service.main import send_reminder_1h
                    from mail_service.models import MailUser
                    
                    user = MailUser(
                        email=user_data['email'],
                        name=user_data['name'],
                        services=user_data['services'],
                        message=user_data['message'],
                        date=user_data['date'],
                        start_time=user_data['start_time'],
                        end_time=user_data['end_time'],
                        code=user_data['code']
                    )
                    send_reminder_1h(user)
                    print(f"1h reminder sent to {user_data['email']}")
            
            print(f"Checked {len(meetings)} meetings for reminders")
        
    except Exception as e:
        print(f"Error in reminder scheduler: {e}")

