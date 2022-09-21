import time
import os

from apscheduler.triggers.cron import CronTrigger
from colorama import Fore
from colorama import Style
from colorama import init
from apscheduler.schedulers.background import BackgroundScheduler

init(autoreset=True)


def my_schedule(job1, job2, job3):
    scheduler = BackgroundScheduler({'apscheduler.timezone': 'Europe/Athens'})

    trigger_job1 = CronTrigger(
        year="*", month="*", day="*", hour="0", minute="5", second="0"
    )
    trigger_job2 = CronTrigger(
        year="*", month="*", day="*", hour="0", minute="5", second="0"
    )
    trigger_job3_a = CronTrigger(
        year="*", month="*", day="*", hour="23", minute="55", second="0"
    )
    trigger_job3_b = CronTrigger(
        year="*", month="*", day="*", hour="11", minute="55", second="0"
    )
    scheduler.add_job(job1, trigger=trigger_job1, name="daily pull sensor data")
    scheduler.add_job(job2, trigger=trigger_job2, name="daily pull openweather data")
    scheduler.add_job(job2, trigger=trigger_job3_a, name="night pull accuweather data")
    scheduler.add_job(job2, trigger=trigger_job3_b, name="day pull accuweather data")
    scheduler.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
