import os
import random
from datetime import timedelta

import numpy as np
import pytest
from faker import Faker

from bassoon.article import Article, Corpus


def article_iterator(nb_article=10):
    factory = Faker()
    for _ in range(nb_article):
        art_dict = {
            "title": factory.text(),
            "link": factory.uri(),
            "content": "\n".join(factory.texts()),
        }
        published = factory.date_time()
        modified = factory.date_time_between(published, published + timedelta(days=30))
        if random.choice([True, False]):
            art_dict["published"] = published.isoformat()
        if random.randint(0, 9) == 0:
            art_dict["updated"] = modified.isoformat()
        author = []
        if random.choice([True, False]):
            author.append(factory.name())
        if random.choice([True, False]) or not author:
            author.append("<" + factory.email() + ">")
        art_dict["author"] = (" ".join(author),)
        if random.randint(0, 3) == 0:
            art_dict["summary"] = factory.text()
        yield Article(**art_dict)


@pytest.fixture
def corpus():
    # set up
    docs = Corpus()
    articles = article_iterator()
    for article in articles:
        docs.add_article(article)

    yield docs

    # tear down
    os.remove(docs.db_filename)


def test_ddmatrix(corpus):
    """Check properties of document by document matrix.
    """
    mat = corpus.document_by_document().applymap(float)
    assert np.all(mat == mat.transpose())
    assert any(
        [
            # definite positive
            np.all(np.linalg.eigvals(mat) > 0),
            # semi-definite positive
            np.isclose([np.min(np.linalg.eigvals(mat))], [0]),
        ]
    )
