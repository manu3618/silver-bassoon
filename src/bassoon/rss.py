"""
rss and atom retrieval
"""

import requests
from bs4 import BeautifulSoup


class Feed:
    def __init__(self, url=""):
        self.url = url

    def retrieve(self):
        """
        Retrieve article from feed

        Args:
            url (str): feed url
        """
        resp = requests.get(self.url)
        if resp.ok:
            self.content = resp.content
        else:
            raise RuntimeWarning(resp.reason)

    def analyze(self):
        """analyze feed
        """
        soup = BeautifulSoup(self.content, features="html.parser")
        self.title = soup.title.text

    @property
    def articles(self):
        return list(self._articles())

    def article_iterator(self):
        """iterator over articles."""
        return self._articles()

    def _articles(self):
        """Return articles from feed content.
        """
        soup = BeautifulSoup(self.content, features="html.parser")
        for article in soup.find_all("entry"):
            yield {elt.name: elt.content for elt in article.children}


def opml_to_feeds(filename):
    """Get feeds from OPML file

    Args:
        filename (str): path to opml file
    Returns:
        (list): list of Feed
    """
    with open(filename, "r") as fd:
        soup = BeautifulSoup(fd.read())

    return [
        Feed(elt.attrs["xmlurl"])
        for elt in soup.find_all("outline")
        if "xmlurl" in elt.attrs
    ]
