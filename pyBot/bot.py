"""
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
"""
import logging

from common import LOGGER_NAME
from credentials import bot_token

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from musicServices.apple import AppleMusicManager
from musicServices.common import MusicService
from musicServices.yandex import YandexMusicManager
from utils import setup_logging


setup_logging()
logger = logging.getLogger(LOGGER_NAME)


def startCommand(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Please paste a link to the music you want to share.')


def helpCommand(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Use share menu in your music app to create a link. '
                              'Then paste it here to get links to other services.')


def send_reply(update: Update, text: str):
    logger.debug('Replying to request id {id}: {reply}'.format(id = update.update_id, reply = text))
    update.message.reply_text(text)


def processLink(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    logger.debug('Got new request with id {id}: {text}'.format(id = update.update_id, text = text))

    apple_media_object = AppleMusicManager().parseMediaFromLink(text)
    if not apple_media_object:
        send_reply(update, "Sorry, couldn't parse the link. We are working on this problem.")
        return

    YandexMusicManager().searchMediaByLink(apple_media_object)

    track = apple_media_object.track
    album = apple_media_object.album
    send_reply(update, 'This is a link to {track}{from_album}. Yandex Music link is {yandex_link}'.
                              format(track = track,
                                     from_album =' from album {album}'.format(album = album) if album is not None else '',
                                     yandex_link = apple_media_object.link[MusicService.YANDEX]))


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", startCommand))
    dispatcher.add_handler(CommandHandler("help", helpCommand))

    dispatcher.add_handler(MessageHandler(Filters.text, processLink))

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
