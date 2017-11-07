# -*- coding: utf-8 -*-
from faker import Faker
from faker.providers import BaseProvider

from librarian.utils import compute_isbn10_checkdigit, compute_isbn13_checkdigit

import random
import string

fake = Faker()

class BookFieldsProvider(BaseProvider):
    ADJECTIVES = ("beautiful", "wonderful", "abstruse", "astute", "bad", "good",
      "austere", "sinister", "jolly", "helpful", "ersatz", "slippery", "penultimate",
      "unyielding", "intimidating", "wistful", "vile", "carnivorous", "miserable")
    NOUNS = ("computer", "formula", "equation", "waters", "rain", "fight",
      "hope", "dream", "love", "library", "book", "elevator", "hospital",
      "village", "academy", "goblet", "chamber", "carnival", "hero")

    def isbn(self, thirteen=True):
        if thirteen:
            isbn = "".join([random.choice(string.digits) for _ in range(12)])

            return isbn + compute_isbn13_checkdigit(isbn)
        else:
            isbn = "".join([random.choice(string.digits) for _ in range(9)])
            return isbn + compute_isbn10_checkdigit(isbn)

    def title(self):
        return " ".join(("The",
          random.choice(BookFieldsProvider.ADJECTIVES).capitalize(),
          random.choice(BookFieldsProvider.NOUNS).capitalize()))
