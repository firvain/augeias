import time
import os
from colorama import Fore
from colorama import Style
from colorama import init
from apscheduler.schedulers.background import BackgroundScheduler

init(autoreset=True)


def my_schedule(job):
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', minutes=5)
    scheduler.start()
    print(f'{Fore.GREEN} Press Ctrl+C to exit')
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
