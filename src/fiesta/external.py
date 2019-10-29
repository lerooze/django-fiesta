# external.py
import requests

from dataclasses import dataclass
from django.utils.translation import gettext_lazy as _
from tempfile import SpooledTemporaryFile
from typing import Dict, Any 

from .core.exceptions import ExternalError

@dataclass
class Request:
    headers: Dict[str, Any] = None 


    def get(self, location):
        try:
            stream = self.get_stream_from_location(location)
        except requests.exceptions.MissingSchema:
            # Load data from local file
            # json files must be opened in text mode, all others in binary as
            # they may be zip files or xml.
            try:
                if location.endswith('.json'):
                    mode_str = 'r'
                else:
                    mode_str = 'rb'
                stream = open(location, mode_str)
            except FileNotFoundError:
                stream = location 
        return self.parse(stream)

    def get_stream_from_location(self, location):
        cfg = self.create_configuration(location)
        response = requests.get(location, **cfg, headers=self.headers) 
        if response.status_code == requests.codes.OK:
            source = SpooledTemporaryFile(max_size=2**24, mode='w+b')
            for c in response.iter_content(chunk_size=1000000):
                source.write(c)
        else:
            source = None
        code = int(response.status_code)
        if 400 <= code <= 499:
            raise ExternalError(
                _('Error occured while extracting {} resource').format(location),
                code=f'{code}_external_error'
            )
        return source

    def create_configuration(self, location):
        cfg = dict(stream=True, timeout=30.1)
        cfg = self.extend_cfg(cfg)
        return cfg

    def extend_cfg(self, cfg):
        return cfg

