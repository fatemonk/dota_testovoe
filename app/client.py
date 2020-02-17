import os

import requests
from sanic.log import logger


class ClientError(Exception):
    """Error when using a client to Dota API."""

    def __init__(self, status_code: int):
        self.status_code = status_code


class Client:
    """Dota API client."""
    URL = 'http://api.steampowered.com/IDOTA2Match_{dota_version}/GetMatchDetails/v1'

    def __init__(self):
        self.url = self.URL.format(dota_version=os.environ.get('DOTA_VERSION', '570'))
        with open('keys') as keys:
            self.key = keys.readline().strip()

    def fetch(self, match_id: int) -> dict:
        """Fetch match metadata."""
        try:
            resp = requests.get(
                self.url,
                params={'key': self.key, 'match_id': match_id},
                timeout=os.environ.get('TIMEOUT', 3))
            resp.raise_for_status()
            return resp.json()['result']
        except (requests.Timeout, requests.ConnectionError):
            raise ClientError(503)
        except Exception as exc:
            logger.exception('Error while fetching data from Dota API', exc_info=exc)
            raise ClientError(500)
