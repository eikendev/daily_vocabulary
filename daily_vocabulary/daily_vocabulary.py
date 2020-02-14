import logging
import sys

from telegram.ext import Updater

from .config import config, get_debug_level
from .database import init_db
from .handlers import add_handlers
from .jobs import register_jobs

logger = logging.getLogger('daily_vocabulary')


def main():
    fmt = config['LOGGING']['Format']
    datefmt = config['LOGGING']['DateFormat']
    level = get_debug_level(config['LOGGING']['Level'])

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)

    app_name = config['GENERAL']['ApplicationName']
    logger.setLevel(level)
    logger.addHandler(sh)
    logger.info('Starting %s.', app_name)

    init_db()

    token = config['KEYS']['ApiToken']
    updater = Updater(token=token, workers=1, use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    add_handlers(dispatcher)
    register_jobs(job_queue)

    poll_interval = config.getfloat('NETWORK', 'PollInterval')
    timeout = config.getint('NETWORK', 'Timeout')

    updater.start_polling(poll_interval=poll_interval, timeout=timeout)
    updater.idle()

    logger.info('Stopping %s.', app_name)
