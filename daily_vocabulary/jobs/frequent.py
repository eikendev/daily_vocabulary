import logging

from datetime import datetime, timedelta

from sqlalchemy.sql import func
from telegram import ParseMode
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from ..database.models import Receiver
from ..decorators import session_request
from ..utils import select_word, build_message

logger = logging.getLogger('daily_vocabulary')


@session_request
def job_subscription(context: CallbackContext, session):

    now = datetime.now()
    today = now.date()
    later = now + timedelta(minutes=2)
    time_guard = now - timedelta(minutes=2)

    receivers = Receiver.query.filter_by(is_subscribed=True) \
        .filter(func.datetime(now) <= Receiver.aligned_notification_time(today)) \
        .filter(func.datetime(later) > Receiver.aligned_notification_time(today)) \
        .filter((Receiver.last_messaged == None) | (Receiver.last_messaged < time_guard))  # noqa: E711
    receivers = receivers.all()
    logger.debug('Query returned %d receivers.', len(receivers))

    word = select_word()
    message = build_message(word)

    for r in receivers:
        try:
            context.bot.send_message(chat_id=r.chat_id,
                                     text=message,
                                     parse_mode=ParseMode.MARKDOWN)
            r.set_messaged(timestamp=now)
        except TelegramError:
            # TODO: Handle Unauthorized, ChatMigrated.
            pass

    session.commit()
