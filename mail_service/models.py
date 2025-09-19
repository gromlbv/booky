from mail_service.service import send_code, send_report, send_reminder

class MailUser:
    def __init__(self, email, name, services, message, date, start_time, end_time, code):
        self.name = name
        self.email = email
        self.services = services
        self.message = message
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.code = code

    def send_code(self):
        send_code(self)

    def send_reminder(self):
        send_reminder(self)
class MailReport:
    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

    def send_report(self):
        send_report(self)