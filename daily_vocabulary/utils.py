import datetime
import re

from json import load
from random import choice, seed
from urllib.parse import urlparse

from .config import config

PATTERN_TIME = re.compile(r'(\d{2}):(\d{2})')


def select_word(rand=None):
    words_path = config['PATHS']['Words']
    with open(words_path, 'r') as json_file:
        json = load(json_file)

    if rand is None:
        rand = datetime.date.today()

    seed(rand)
    word = choice(json)
    return word


def build_message(word):
    title = word['title']
    meaning = word['meaning']
    href = word['href']
    hostname = urlparse(href).hostname

    message = "*{}*\n\n```\n{}\n```\n\n[{}]({})"

    return message.format(title, meaning, hostname, href)


def parse_user_time(time_raw):
    if type(time_raw) is not str:
        raise ValueError('time_raw must be of type str.')

    time_raw = time_raw.strip()
    match = re.fullmatch(PATTERN_TIME, time_raw)

    if match is None:
        raise ValueError('time_raw must match the pattern hh:mm.')

    hour = int(match.group(1))
    minute = int(match.group(2))
    time = datetime.time(hour, minute)

    return time
