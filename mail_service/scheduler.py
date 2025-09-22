from celery import current_app
from mail_service.utils import calculate_time_until_meeting
import sqlite3
import os

@current_app.task
def check_and_send_reminders():
    try:
        db_path = os.path.join('instance', 'database.db')
        if not os.path.exists(db_path):
            print("Database not found")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT email, name, services, message, date, start_time, end_time, code
            FROM meetings 
            WHERE date >= date('now') 
            AND date <= date('now', '+1 day')
            ORDER BY date, start_time
        """)
        
        meetings = cursor.fetchall()
        
        for meeting in meetings:
            user_data = {
                'email': meeting[0],
                'name': meeting[1], 
                'services': meeting[2],
                'message': meeting[3],
                'date': meeting[4],
                'start_time': meeting[5],
                'end_time': meeting[6],
                'code': meeting[7]
            }
            
            time_until = calculate_time_until_meeting(user_data['date'], user_data['start_time'])
            total_hours = time_until['days'] * 24 + time_until['hours']
            
            if 23 <= total_hours <= 25:
                from mail_service.main import send_code
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
                send_code(user)
                print(f"24h reminder sent to {user_data['email']}")
            
            if 0 <= total_hours <= 2:
                from mail_service.main import send_code
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
                send_code(user)
                print(f"1h reminder sent to {user_data['email']}")
            
        conn.close()
        print(f"Checked {len(meetings)} meetings for reminders")
        
    except Exception as e:
        print(f"Error in reminder scheduler: {e}")

