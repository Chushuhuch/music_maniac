"""
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
"""
import abc
import logging
import re
from http import HTTPStatus
from logging import DEBUG

import requests

from credentials import bot_token

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.level = DEBUG


def startCommand(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Please paste a link to the music you want to share.')


def helpCommand(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Use share menu in your music app to create a link. '
                              'Then paste it here to get links to other services.')


class MediaObject:

    def __init__(self, track: str = None, album: str = None, invalid: bool = False):
        self.track = track
        self.album = album
        self.invalid = invalid


MediaObject.INVALID_MEDIA_OBJECT = MediaObject(invalid = True)


class MusicServiceManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parseMediaFromLink(self, link: str):
        raise NotImplementedError


class AppleMusicManager(MusicServiceManager):

    LINK_PREFIX = 'https://music.apple.com/ru/album/'
    GET_INFO_BY_ID_REQUEST = 'https://itunes.apple.com/lookup?id={id}'
    IDS_REGEX = re.compile(r'(\d+)\?i=(\d+)&ls')

    def parseMediaFromLink(self, link: str) -> MediaObject:
        if not link.startswith(self.LINK_PREFIX):
            return MediaObject.INVALID_MEDIA_OBJECT
        parts = link[len(self.LINK_PREFIX):].split('/')
        if not len(parts) == 2:
            return MediaObject.INVALID_MEDIA_OBJECT
        _, ids = parts
        # ids == 'albumID?i=trackID&ls'
        match = re.match(self.IDS_REGEX, ids)
        if not match:
            return MediaObject.INVALID_MEDIA_OBJECT

        # collection_id = match.group(1)
        track_id = match.group(2)

        response = requests.get(self.GET_INFO_BY_ID_REQUEST.format(id = track_id))
        if response.status_code != HTTPStatus.OK:
            return MediaObject.INVALID_MEDIA_OBJECT
        response_json = response.json()
        if response_json['resultCount'] != 1 or 'trackName' not in response_json['results'][0]:
            return MediaObject.INVALID_MEDIA_OBJECT
        track_name = response_json['results'][0]['trackName']
        collection_name = response_json['results'][0]['collectionName']

        return MediaObject(track = track_name, album = collection_name)


def send_reply(update: Update, text: str):
    logger.debug(update.message.text + ' ' + text)
    update.message.reply_text(text)


def processLink(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    logger.debug(text)

    apple_media_object = AppleMusicManager().parseMediaFromLink(text)
    if apple_media_object == MediaObject.INVALID_MEDIA_OBJECT:
        send_reply(update, "Sorry, couldn't parse the link. We are working on this problem.")
        return

    track = apple_media_object.track
    album = apple_media_object.album
    send_reply(update, 'This is a link to {track}{from_album}.'.
                              format(track = track, from_album =' from album {album}'.format(album = album) if album is not None else ''))


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
