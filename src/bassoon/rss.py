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
        soup = BeautifulSoup(self.content)
        self.title = soup.title.text
        self.articles = list(self._articles())

    def _articles(self):
        """Return articles from feed content.
        """
        soup = BeautifulSoup(self.content)
        for article in soup.find_all("entry"):
            yield {elt.name: elt.content for elt in article.children}
