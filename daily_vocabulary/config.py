import logging

from configparser import ConfigParser

CONFIG_FILENAME = 'data/config.ini'
config = ConfigParser(interpolation=None)
config.read(CONFIG_FILENAME)


def get_debug_level(level):
    levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET
    }

    if type(level) is not str:
        raise TypeError('Level must be of type str.')
    elif level not in levels:
        raise ValueError('Level must be a logging level.')

    return levels[level]
