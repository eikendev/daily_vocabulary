import logging
import random

from sqlalchemy.orm.exc import NoResultFound
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from ..database.models import Receiver
from ..decorators import session_request
from ..utils import select_word, build_message, parse_user_time

logger = logging.getLogger('daily_vocabulary')


def command_unknown(update: Update, context: CallbackContext):
    update.message.reply_text('Unknown command.')


@session_request
def command_start(update: Update, context: CallbackContext, session):
    chat_id = update.message.chat_id

    update.message.reply_text('Hello there.')

    try:
        Receiver.query.filter_by(chat_id=chat_id).one()
    except NoResultFound:
        receiver = Receiver(chat_id)
        session.add(receiver)
        session.commit()


def command_help(update: Update, context: CallbackContext):
    update.message.reply_text("I'm here to help.")


def command_ping(update: Update, context: CallbackContext):
    update.message.reply_text('Pong!')


@session_request
def command_subscribe(update: Update, context: CallbackContext, session):
    chat_id = update.message.chat_id

    try:
        receiver = Receiver.query.filter_by(chat_id=chat_id).one()
        if receiver.is_subscribed:
            update.message.reply_text('You already subscribed.')
            return
        else:
            receiver.set_subscribed(messaged=True)
    except NoResultFound:
        receiver = Receiver(chat_id, subscribed=True, messaged=True)
        session.add(receiver)

    session.commit()
    update.message.reply_text('You successfully subscribed.')

    word = select_word()
    message = build_message(word)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


@session_request
def command_unsubscribe(update: Update, context: CallbackContext, session):
    chat_id = update.message.chat_id

    try:
        receiver = Receiver.query.filter_by(chat_id=chat_id,
                                            is_subscribed=True).one()
    except NoResultFound:
        update.message.reply_text('You are currently not subscribed.')

    receiver.set_unsubscribed()
    session.commit()

    update.message.reply_text('You successfully unsubscribed.')


@session_request
def command_settime(update: Update, context: CallbackContext, session, args):
    chat_id = update.message.chat_id

    if type(args) is not list:
        logger.debug('args must be of type list.')
        update.message.reply_text('An error occured.')
        return
    elif len(args) != 1:
        logger.debug('args must not be empty.')
        msg = ('I was not able to handle your request. '
               'Use as follows: /settime hh:mm')
        update.message.reply_text(msg)
        return

    try:
        receiver = Receiver.query.filter_by(chat_id=chat_id,
                                            is_subscribed=True).one()
    except NoResultFound:
        update.message.reply_text('You are currently not subscribed.')
        return

    try:
        time = parse_user_time(args[0])
    except ValueError:
        logger.debug('Could not parse args.')
        msg = ('I was not able to handle your request. '
               'Use as follows: /settime hh:mm')
        update.message.reply_text(msg)
        return

    receiver.notification_time = time
    receiver.last_messaged = None
    session.commit()

    time_s = time.strftime('%H:%M')
    message = 'Your new notification time is {}.'
    update.message.reply_text(message.format(time_s))


@session_request
def command_status(update: Update, context: CallbackContext, session):
    chat_id = update.message.chat_id

    try:
        receiver = Receiver.query.filter_by(chat_id=chat_id).one()
    except NoResultFound:
        update.message.reply_text("I don't know you.")
        return

    if receiver.is_subscribed:
        message = 'You are currently subscribed.'
    else:
        message = 'You are currently not subscribed.'

    message += "\nYou were notified {} times."
    message = message.format(receiver.times_messaged)

    if receiver.notification_time is not None:
        ts = receiver.notification_time.strftime('%H:%M')
        message += "\nYour automatic notification time is set to {}."
        message = message.format(ts)

    if receiver.last_messaged is not None:
        ts = receiver.last_messaged.strftime('%Y-%m-%d %H:%M')
        message += "\nThe last automatic notification was sent on {}."
        message = message.format(ts)

    update.message.reply_text(message)


def send_word(update: Update, context: CallbackContext, session, word):
    chat_id = update.message.chat_id

    try:
        receiver = Receiver.query.filter_by(chat_id=chat_id).one()
        receiver.set_messaged()
    except NoResultFound:
        receiver = Receiver(chat_id, messaged=True)
        session.add(receiver)

    session.commit()

    message = build_message(word)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


@session_request
def command_peek(update: Update, context: CallbackContext, session):
    word = select_word()
    send_word(update, context, session, word)


@session_request
def command_random(update: Update, context: CallbackContext, session):
    word = select_word(random.SystemRandom().random())
    send_word(update, context, session, word)
