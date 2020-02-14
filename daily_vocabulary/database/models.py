from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Time
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import extract

from . import Base


class Receiver(Base):
    __tablename__ = 'receivers'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    first_seen = Column(DateTime, nullable=False)
    datetime_subscribed = Column(DateTime)
    times_subscribed = Column(Integer, nullable=False)
    last_messaged = Column(DateTime)
    times_messaged = Column(Integer, nullable=False)
    notification_time = Column(Time)

    def __init__(self, chat_id, subscribed=False, messaged=False):
        now = datetime.now()

        self.chat_id = chat_id
        self.first_seen = now
        self.datetime_subscribed = None
        self.times_subscribed = 0
        self.last_messaged = None
        self.times_messaged = 0
        self.notification_time = None

        if subscribed:
            self.set_subscribed(timestamp=now, messaged=messaged)
        elif messaged:
            self.set_messaged()

    def __str__(self):
        return '<Receiver with chat id {}>'.format(self.chat_id)

    @hybrid_property
    def is_subscribed(self):
        return self.datetime_subscribed is not None

    @is_subscribed.expression
    def is_subscribed(cls):
        return cls.datetime_subscribed.isnot(None)

    def set_subscribed(self, timestamp=None, messaged=False):
        if not timestamp:
            timestamp = datetime.now()
        elif type(timestamp) is not datetime:
            raise TypeError('timestamp must be of type datetime.datetime.')

        self.datetime_subscribed = timestamp
        self.notification_time = timestamp.time()
        self.times_subscribed += 1

        if messaged:
            self.set_messaged(timestamp)

    def set_unsubscribed(self):
        self.datetime_subscribed = None
        self.notification_time = None

    def set_messaged(self, timestamp=None):
        """
        :param timestamp: New ``last_messaged`` timestamp for this receiver.
        If omitted, ``last_messaged`` remains unchanged.
        """
        if timestamp is not None:
            if type(timestamp) is datetime:
                self.last_messaged = timestamp
            else:
                raise TypeError('timestamp must be of type datetime.datetime.')

        self.times_messaged += 1

    @hybrid_method
    def aligned_notification_time(self, date):
        return datetime.datetime.combine(date, self.notification_time)

    @aligned_notification_time.expression
    def aligned_notification_time(cls, date):
        hour = extract('hour', cls.notification_time)
        minute = extract('minute', cls.notification_time)
        add_hours = func.printf('+%d hours', hour)
        add_minutes = func.printf('+%d minutes', minute)
        return func.datetime(date, add_hours, add_minutes)
