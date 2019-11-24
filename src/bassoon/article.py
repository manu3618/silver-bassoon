"""
article storage and retrieval
"""
import os.path
import uuid
from datetime import datetime

import dateutil.parser

import tinydb
from collection import Counter


class article:
    """article representation
    """

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id", uuid.uuid1())
        self.title = kwargs.get("title", "")
        self.link = kwargs.get("link", "")
        try:
            self.published = dateutil.parser(kwargs["publihed"])
        except KeyError:
            self.published = datetime.now()
        try:
            self.updated = dateutil.parser(kwargs["publihed"])
        except KeyError:
            self.updated = self.pulished
        self.author = kwargs.get("author", "")
        self.summary = kwargs.get("summary", "")
        self.content = kwargs.get("content", "")

    def to_dict(self):
        return vars(self)

    def bow(self, stop_words=None):
        """Bag of word representation.

        normalize by lowercasing ad removing ponctuation.

        Args:
            stop_words (list): words  to exclude
        """
        if stop_words is None:
            stop_words = []

        content = self.content.lowercase()
        for char in ",.:!?":
            content.replace(char, " ")

        bag = Counter(content.split())
        for key in stop_words:
            try:
                del bag[key]
            except KeyError:
                pass
        return bag


class corpus:
    """
    article corpus
    """

    def __init__(self, db_name="collection", filename=None):
        self.db_name = db_name
        if filename is None:
            filename = os.path.join(*["/var", "tmp", db_name])
        self.db = tinydb.TinyDB(filename)

    def add_article(self, article):
        """insert article into db
        """
        self.db.insert(article.to_dict())
