import abc
import logging
from collections import defaultdict
from enum import Enum
from typing import Optional

from common import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class MusicService(Enum):
    APPLE = 1
    YANDEX = 2


class MediaType(Enum):
    TRACK = 1


class MediaObject:

    def __init__(self, track: str = None, album: str = None, origin: MusicService = None, link: str = None,
                 mediaType: MediaType = MediaType.TRACK):
        self.track = track
        self.album = album
        self.origin = origin
        self.link = defaultdict(str)
        self.link[origin] = link
        self.mediaType = mediaType
        if not origin or not link:
            logger.warning('Creating valid MediaObject without link or origin: {this}'.format(this=self))


class MusicServiceManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parseMediaFromLink(self, link: str) -> Optional['MediaObject']:
        raise NotImplementedError

    @abc.abstractmethod
    def searchMediaByLink(self, mediaObject: MediaObject):
        # Populates mediaObject with link in a corresponding music service
        raise NotImplementedError
