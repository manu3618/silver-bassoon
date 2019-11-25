import os
import random
from datetime import timedelta

import pytest
from faker import Faker

from .article import Article, Corpus


@pytest.fixture
def article_iterator(nb_article=10):
    factory = Faker()
    for _ in range(nb_article):
        published = factory.date_time()
        modified = factory.date_time_between(published, published + timedelta(days=30))
        author = []
        if random.choice([True, False]):
            author.append(factory.name())
        if random.choice([True, False]) or not author:
            author.append("<" + factory.email() + ">")
        yield Article(
            {
                "title": factory.text(),
                "link": factory.uri(),
                "published": published,
                "updated": published if random.randint(0, 9) == 0 else modified,
                "author": " ".join(author),
                "summary": factory.text() if random.randint(0, 3) == 0 else "",
                "content": "\n".join(factory.texts()),
            }
        )


@pytest.fixture
def corpus(article_iterator):
    # set up
    docs = Corpus()
    for article in article_iterator:
        docs.add_article(article)

    yield docs

    # tear down
    os.remove(docs.db_filename)
