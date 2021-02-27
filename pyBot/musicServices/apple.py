import re
from http import HTTPStatus
from typing import Optional

import requests

from bot import MediaObject, MusicService
from musicServices.common import MusicServiceManager


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