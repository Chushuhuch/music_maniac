"""
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
"""
import abc
import logging
import re
from collections import defaultdict
from enum import Enum
from http import HTTPStatus
from logging import DEBUG
from typing import Optional

import requests
import yandex_music

from credentials import bot_token

from telegram import Update, ParseMode
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


class MusicService(Enum):
    APPLE = 1
    YANDEX = 2


class MediaType(Enum):
    TRACK = 1


class MediaObject:

    def __init__(self, track: str = None, album: str = None, origin: MusicService = None, link: str = None, mediaType: MediaType = MediaType.TRACK):
        self.track = track
        self.album = album
        self.origin = origin
        self.link = defaultdict(str)
        self.link[origin] = link
        self.mediaType = mediaType
        if not origin or not link:
            logger.warning('Creating valid MediaObject without link or origin: {this}'.format(this = self))


class MusicServiceManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parseMediaFromLink(self, link: str) -> Optional['MediaObject']:
        raise NotImplementedError

    @abc.abstractmethod
    def searchMediaByLink(self, mediaObject: MediaObject):
        # Populates mediaObject with link in a corresponding music service
        raise NotImplementedError


class AppleMusicManager(MusicServiceManager):

    LINK_PREFIX = 'https://music.apple.com/ru/album/'
    GET_INFO_BY_ID_REQUEST = 'https://itunes.apple.com/lookup?id={id}'
    IDS_REGEX = re.compile(r'(\d+)\?i=(\d+)&ls')

    def parseMediaFromLink(self, link: str) -> Optional['MediaObject']:
        if not link.startswith(self.LINK_PREFIX):
            return None
        parts = link[len(self.LINK_PREFIX):].split('/')
        if not len(parts) == 2:
            return None
        _, ids = parts
        # ids == 'albumID?i=trackID&ls'
        match = re.match(self.IDS_REGEX, ids)
        if not match:
            return None

        # collection_id = match.group(1)
        track_id = match.group(2)

        response = requests.get(self.GET_INFO_BY_ID_REQUEST.format(id = track_id))
        if response.status_code != HTTPStatus.OK:
            return None
        response_json = response.json()
        if response_json['resultCount'] != 1 or 'trackName' not in response_json['results'][0]:
            return None
        track_name = response_json['results'][0]['trackName']
        collection_name = response_json['results'][0]['collectionName']

        return MediaObject(track = track_name, album = collection_name, origin = MusicService.APPLE, link = link)

    def searchMediaByLink(self, mediaObject: MediaObject):
        raise NotImplementedError


class YandexMusicManager(MusicServiceManager):

    def __init__(self):
        self.client = yandex_music.Client()

    def parseMediaFromLink(self, link: str) -> Optional['MediaObject']:
        raise NotImplementedError

    def searchMediaByLink(self, mediaObject: MediaObject):
        if mediaObject.mediaType != MediaType.TRACK:
            raise NotImplementedError

        search_result = self.client.search(text = '{album}{track}'.format(album = mediaObject.album + ' ' if mediaObject.album else '', track = mediaObject.track), nocorrect = True, type_ = 'track')
        track_results = search_result.tracks
        if not track_results:
            logger.debug('Not found any tracks by the request')
            return
        tracks = track_results.results
        matching_tracks = [track for track in tracks if (not mediaObject.album or len([album for album in track.albums if album.title == mediaObject.album]) > 0) and track.title == mediaObject.track]
        if len(matching_tracks) != 1:
            logger.debug('Found bad amount of tracks in Yandex.Music: {matching_tracks}'.format(matching_tracks = matching_tracks))
        if matching_tracks:
            mediaObject.link[MusicService.YANDEX] = 'https://music.yandex.ru/track/{track_id}'.format(track_id = matching_tracks[0].id)


def send_reply(update: Update, text: str):
    logger.debug(update.message.text + ' ' + text)
    update.message.reply_text(text)


def processLink(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    logger.debug(text)

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
