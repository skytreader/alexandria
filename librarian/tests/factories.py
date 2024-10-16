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
    creator = factory.SubFactory(LibrarianFactory)


class BookCompanyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.BookCompany
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda x: fake.company())
    creator = factory.SubFactory(LibrarianFactory)


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Book
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda n: n)
    isbn = factory.LazyAttribute(lambda x: fake.isbn())
    title = factory.LazyAttribute(lambda x: fake.title())
    genre = factory.SubFactory(GenreFactory)
    publisher = factory.SubFactory(BookCompanyFactory)
    publish_year = factory.LazyAttribute(lambda x: fake.year())
    creator = factory.SubFactory(LibrarianFactory)


class ContributorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Contributor
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda x: x)
    lastname = factory.LazyAttribute(lambda x: fuzzy_text.fuzz())
    firstname = factory.LazyAttribute(lambda x: fuzzy_text.fuzz())
    active = factory.LazyAttribute(lambda x: True)
    creator = factory.SubFactory(LibrarianFactory)


class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Role
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda x: x)
    name = factory.LazyAttribute(lambda x: fuzzy_text.fuzz())
    display_text = factory.LazyAttribute(lambda x: fuzzy_text.fuzz())


class BookContributionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.BookContribution
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda x: x)
    book = factory.SubFactory(BookFactory)
    contributor = factory.SubFactory(ContributorFactory)
    role = factory.SubFactory(RoleFactory)
    active = factory.LazyAttribute(lambda x: True)
    creator = factory.SubFactory(LibrarianFactory)


class PrinterFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Printer
        sqlalchemy_session = librarian.db.session

    company_id = factory.LazyAttribute(lambda x: BookCompanyFactory().id)
    book_id = factory.LazyAttribute(lambda x: BookFactory().id)
    creator_id = factory.LazyAttribute(lambda x: LibrarianFactory().id)
