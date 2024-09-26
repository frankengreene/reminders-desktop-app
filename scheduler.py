# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from notifier import send_notification
from datetime import datetime

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def schedule_task(self, task_id, title, reminder_time):
        try:
            reminder_datetime = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
            trigger = DateTrigger(run_date=reminder_datetime)
            self.scheduler.add_job(
                send_notification,
                trigger=trigger,
                args=[f"Reminder: {title}", "It's time to complete your task!"],
                id=str(task_id),
                replace_existing=True  # This ensures existing jobs with the same ID are replaced
            )
        except ValueError as e:
            print(f"Error scheduling task {task_id}: {e}")

    def remove_task(self, task_id):
        job_id = str(task_id)
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
