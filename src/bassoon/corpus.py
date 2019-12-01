"""
article storage and retrieval
"""
import os.path
import uuid
import warnings
from collections import Counter, OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta

import dateutil.parser
import numpy as np
import pandas as pd

import tinydb

from .rss import Feed


@dataclass(init=False)
class Article:
    """article representation
    """

    id: str
    published: datetime
    updated: datetime
    title: str
    link: str
    author: str
    summary: str
    content: str

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
        return self.normalize_bow(stop_words, 1)

    def normalize_bow(self, stop_words=None, norm=2):
        """normalized version of bow, with norm choice.
        """
        terms = self.bow(stop_words)

        # values are greater than zero, no abs needed
        size = np.power(sum(np.power(list(terms.values()), norm)), 1 / norm)
        return {word: count / size for word, count in terms.items()}


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
        self.stop_words = set()
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
        return self.term_document_matrix().transpose()

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

    def autodetect_stopwords(self):
        """Return possible stopwords in corpus.

        Returns:
            (set) stopwords
        """
        td = self.term_document_matrix()
        for term, row in td.iterrows():
            if any(
                [
                    all(row != 0),  # word present in all article, not usefull
                    len(term) < 3,
                    len(row[row > 0]) < 2,  # present in too few article to be usefull
                ]
            ):
                self.stop_words.add(term)
        return self.stop_words

    def inverse_doc_freq(self, term, articles=None):
        """Return term relevance.

        Args:
            term (str)
            articles (list) if None, use self.articles
        """
        if articles is None:
            articles = self.articles
            td = pd.DataFrame(
                {doc.id: doc.term_frequency(self.stop_words) for doc in articles}
            )
        else:
            td = self.term_document_matrix()
        row = td.loc[term, :]
        related_articles = row[row > 0]
        return np.log(len(articles) / len(related_articles))

    def terms_weighting(self, terms=None, articles=None):
        """Return terms relevance.
        """
        if terms is None:
            td = self.term_document_matrix()
            terms = td.index
        if articles is None:
            articles = self.articles
        return {term: self.inverse_doc_freq(term, articles) for term in terms}

    def most_relevant_terms(self, nb_terms=10):
        """Return most relevant terms
        """
        return [
            term for term, _ in Counter(self.terms_weighting()).most_common(nb_terms)
        ]

    def get_article(self, id):
        """Get article by id
        """
        return next((art for art in self.articles if art.id == id))

    def find_articles(self, terms):
        """find articles havng those terms.

        Args:
            terms (list)

        Returns:
            (list) : ordered list of articles containing at least one term.
        """
        partial_td = self.term_document_matrix().loc[terms, :]
        art_ids = partial_td.sum().sort_values(ascending=False).index
        return [self.get_article(artid) for artid in art_ids]

    def date_words(self, date, delta=timedelta(days=10), nb_words=10):
        """Return relevant words around this date
        """
        articles = [
            art
            for art in self.articles
            if any(
                [
                    art.published < date + delta and art.published > date - delta,
                    art.updated < date + delta and art.updated > date - delta,
                ]
            )
        ]
        term_weights = self.terms_weighting(articles=articles)
        return OrderedDict(Counter(term_weights).most_common(nb_words))

    def hot_term_matrix(self, start=None, end=None):
        """Return terms over time.
        """
        art_dates = set.union(*[{art.published, art.updated} for art in self.articles])
        dates_delta = max(art_dates) - min(art_dates)
        if start is None:
            start = min(art_dates) - dates_delta / 10
        if end is None:
            end = max(art_dates) + dates_delta / 10

        df = pd.DataFrame(
            {
                date: self.date_words(date, (end - start) / 10)
                for date in pd.date_range(start=start, end=end, periods=60)
            }
        )
        df.fillna(0)
        return df
