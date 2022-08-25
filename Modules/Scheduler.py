import time
import os

from apscheduler.triggers.cron import CronTrigger
from colorama import Fore
from colorama import Style
from colorama import init
from apscheduler.schedulers.background import BackgroundScheduler

init(autoreset=True)


def my_schedule(job):
    scheduler = BackgroundScheduler({'apscheduler.timezone': 'Europe/Athens'})

    trigger = CronTrigger(
        year="*", month="*", day="*", hour="*", minute="10", second="0"
    )
    scheduler.add_job(job, trigger=trigger, name="daily pull data")
    scheduler.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
