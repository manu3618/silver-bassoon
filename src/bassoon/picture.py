"""Picture collector and diplayer"""

import asyncio
import logging
import tempfile

import requests
from PIL import Image

DL_SIMULT_SEM = asyncio.Semaphore(3)


class Picture:
    def __init__(
        self,
        url=None,
        filename=None,
    ):
        self.url = url
        self.filename = filename
        self.image = None  # PIL

    def get_image(self):
        if self.image:
            return self.image
        if self.filename:
            self.image = Image(self.filename)
            return self.image
        if self.url:
            self.filename = tempfile.mktemp()
            dl_file(self.url, self.filename)
            self.image = Image(self.filename)
        return self.image


class PictureGetter:
    def __init__(self):
        self._pictures = []  # list of Picture

    def add_by_url(self, url):
        urls = (getattr(im, "url") for im in self._pictures)
        if url in urls:
            return
        im = Picture(url=url)
        self._pictures.append(im)


def dl_file(url, filename, nb_try=5, wait_time=10, logger=None):
    """Write file from url to filename.

    Args:
        url (str)
        filename (path-like)
        nb_try (int): number of download try
        wait_time (int): base number of seconds to wait brefore each attempt
    """
    if logger is None:
        logger = logging.getLogger()
    for attempt in range(nb_try):
        try:
            content = _dl_file(url)
            break
        except Exception as exn:
            logger.warning(exn)
            await asyncio.sleep(nb_try * wait_time)
    else:
        raise RuntimeError
    with open(filename, "wb") as fd:
        fd.write(content)


def _dl_file(url):
    async with DL_SIMULT_SEM:
        req = requests.get(url)
        if req.status_code != 200 or not req.content:
            raise RuntimeError
        return req.content
