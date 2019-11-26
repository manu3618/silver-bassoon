"""
article storage and retrieval
"""
import os.path
import uuid
import warnings
from collections import Counter
from datetime import datetime
from fractions import Fraction

import dateutil.parser
import pandas as pd

import tinydb

from .rss import Feed


class Article:
    """article representation
    """

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id", str(uuid.uuid1()))
        self.title = kwargs.get("title", "")
        self.link = kwargs.get("link", "")
        try:
            self.published = dateutil.parser.parse(kwargs["published"])
        except KeyError:
            self.published = datetime.now()
        try:
            self.updated = dateutil.parser.parse(kwargs["updated"])
        except KeyError:
            self.updated = self.published
        self.author = kwargs.get("author", "")
        self.summary = kwargs.get("summary", "")
        self.content = kwargs.get("content", "")

    def to_dict(self):
        """Return JSON serializable document.
        """
        doc = vars(self)
        for key in "published", "updated":
            doc[key] = doc[key].isoformat()
        return doc

    def bow(self, stop_words=None):
        """Bag of word representation.

        normalize by lowercasing ad removing ponctuation.

        Args:
            stop_words (list): words  to exclude
        """
        if stop_words is None:
            stop_words = []

        content = self.content.lower()
        for char in ",.:!?":
            content = content.replace(char, " ")

        bag = Counter(content.split())
        for key in stop_words:
            try:
                del bag[key]
            except KeyError:
                pass
        return bag

    def term_frequency(self, stop_words=None):
        """Normalized version of BoW.
       """
        terms = self.bow(stop_words)
        wordcount = sum(terms.values())
        return {word: Fraction(count / wordcount) for word, count in terms.items()}


class Corpus:
    """
    article corpus
    """

    def __init__(self, db_name="collection", filename=None, use_db=True):
        self.db_name = db_name
        if filename is None:
            filename = os.path.join(*["/var", "tmp", db_name])
        self.db_filename = filename
        self.use_db = use_db
        if self.use_db:
            self.db = tinydb.TinyDB(filename)
        self.stop_words = []
        self.articles = []

    def add_article(self, article):
        """insert article into db
        """
        ids = [elt.id for elt in self.articles]
        if article.id in ids:
            warnings.warn("article %s already in corpus" % article.id)
            return

        if self.use_db:
            self.db.insert(article.to_dict())

        self.articles.append(article)

    def from_feed(self, url):
        """Add article from feed
        """
        rss_feed = Feed(url)
        rss_feed.analyze()
        for art in rss_feed.article_iterator():
            article = Article(art)
            self.add_article(article)

    def document_term_matrix(self):
        """Return document term matrix.
        """
        return self.term_documet_matrix().transpose()

    def term_document_matrix(self):
        """Return documen term matrix.
        """
        tm = pd.DataFrame(
            {doc.id: doc.term_frequency(self.stop_words) for doc in self.articles}
        )
        return tm.fillna(0)

    def document_by_document(self):
        """Return document by document matrix.
        """
        dt = self.document_term_matrix()
        return dt.dot(dt.transpose())

    def term_by_term(self):
        """Return term by term matrix.
        """
        td = self.term_document_matrix()
        return td.dot(td.transpose())
