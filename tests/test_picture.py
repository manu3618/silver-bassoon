import pytest
from bassoon.picture import PictureGetter


def get_urls(filename="picts_urls.txt"):
    with open(filename) as fd:
        return fd.read().splitlines()


def get_pictures():
    getter = PictureGetter()
    for url in get_urls():
        getter.add_by_url(url)
    return getter


@pytest.mark.asyncio
async def test_image_dl():
    getter = get_pictures()
    await getter.dl_all_pictures()
