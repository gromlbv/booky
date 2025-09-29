from mail_service.main import send_code, send_report, send_reminder_24h, send_reminder_1h, send_cancel

class MailUser:
    def __init__(self, email, name, services, message, date, start_time, end_time, code, meeting_id, user_timezone='UTC'):
        self.name = name
        self.email = email
        self.services = services
        self.message = message
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.code = code
        self.meeting_id = meeting_id
        self.user_timezone = user_timezone

    def to_dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'services': self.services,
            'message': self.message,
            'date': self.date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'code': self.code,
            'meeting_id': self.meeting_id,
            'user_timezone': self.user_timezone
        }

    def send_code(self):
        send_code(self)
    
    def send_cancel(self):
        send_cancel(self)

    def send_reminder_24h(self):
        send_reminder_24h(self)

    def send_reminder_1h(self):
        send_reminder_1h(self)

class MailReport:
    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

    def send_report(self):
        send_report(self)