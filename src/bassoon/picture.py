"""Picture collector and diplayer"""

from collection import namedtuple
from PIL import Image

Picture = namedtuple(
    "Picture",
    [
        "url",
        "filename",  # local filename,
        "status",  # needs to be downloaded?
        "image",  # PIL
    ],
    defaults=[None, None, None, None],
)


class PictureGetter:
    def __init__(self):
        self._pictures = []  # list of Picture

    def add_by_url(self, url):
        urls = (getattr(im, "url") for im in self._pictures)
        if url in urls:
            return
        im = Picture(url=url)
        self._pictures.append(im)
