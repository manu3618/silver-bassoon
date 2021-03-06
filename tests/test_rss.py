import os.path
from pathlib import Path

import pytest

from bassoon import rss

TEST_DIR = os.path.dirname("__file__")
RSS_DIR = os.path.join(TEST_DIR, "rss")


@pytest.mark.parametrize("filename", Path(RSS_DIR).glob("*"))
def test_feed_analyze(filename):
    feed = rss.Feed()
    with open(filename) as fd:
        feed.content = fd.read()

    feed.analyze()
    assert len(feed.articles) > 0


@pytest.mark.parametrize("filename", Path(TEST_DIR).glob("*opml"))
def test_opml(filename):
    feeds = rss.opml_to_feeds(filename)
    for feed in feeds:
        feed.retrieve()
        assert len(feed.articles) > 0
