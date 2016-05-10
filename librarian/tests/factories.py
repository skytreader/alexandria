# -*- coding: utf-8 -*-
from factory.fuzzy import FuzzyText
from faker import Faker
from librarian import models
from librarian.tests.fakers import BookFieldsProvider
from sqlalchemy import orm

import factory
import factory.alchemy
import librarian
import random
import sqlalchemy

fake = Faker()
fake.add_provider(BookFieldsProvider)

fuzzy_text = FuzzyText()

"""
Note: These factories lack the `last_modifier_id` field because they are creating
_new_ records so we expect the `last_modifier_id` to be the same as `creator_id`.
"""

class LibrarianFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Librarian
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda n: n)
    username = factory.LazyAttribute(lambda x: fake.user_name())
    password = factory.LazyAttribute(lambda x: fake.password())


class GenreFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Genre
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: "Genre%s" % n)
    creator_id = factory.LazyAttribute(lambda x: LibrarianFactory().id)


class BookCompanyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.BookCompany
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda x: fake.company())
    creator_id = factory.LazyAttribute(lambda x: LibrarianFactory().id)


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Book
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda n: n)
    isbn = factory.LazyAttribute(lambda x: fake.isbn())
    title = factory.LazyAttribute(lambda x: fake.title())
    genre_id = factory.LazyAttribute(lambda x: GenreFactory().id)
    publisher_id = factory.LazyAttribute(lambda x: BookCompanyFactory().id)
    publish_year = factory.LazyAttribute(lambda x: fake.year())
    creator_id = factory.LazyAttribute(lambda x: LibrarianFactory().id)


class ContributorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Contributor
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda x: x)
    lastname = factory.LazyAttribute(lambda x: fuzzy_text.fuzz())
    firstname = factory.LazyAttribute(lambda x:fuzzy_text.fuzz())
    creator_id = factory.LazyAttribute(lambda x: LibrarianFactory().id)


class PrinterFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Printer
        sqlalchemy_session = librarian.db.session

    company_id = factory.LazyAttribute(lambda x: BookCompanyFactory().id)
    book_id = factory.LazyAttribute(lambda x: BookFactory().id)
    creator_id = factory.LazyAttribute(lambda x: LibrarianFactory().id)
