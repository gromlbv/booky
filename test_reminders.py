from celery_config import celery_app
from mail_service.scheduler import check_and_send_reminders

# Запуск задачи напрямую
if __name__ == "__main__":
    print("Запуск тестирования напоминаний...")
    result = check_and_send_reminders()
    print("Результат:", result)
