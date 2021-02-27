import abc
from typing import Optional

from bot import MediaObject


class MusicServiceManager(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parseMediaFromLink(self, link: str) -> Optional['MediaObject']:
        raise NotImplementedError

    @abc.abstractmethod
    def searchMediaByLink(self, mediaObject: MediaObject):
        # Populates mediaObject with link in a corresponding music service
        raise NotImplementedError