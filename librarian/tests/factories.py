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
    creator = factory.LazyAttribute(lambda x: LibrarianFactory().id)


class BookCompanyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.BookCompany
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda x: fake.company())
    creator = factory.LazyAttribute(lambda x: LibrarianFactory().id)


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Book
        sqlalchemy_session = librarian.db.session

    id = factory.Sequence(lambda n: n)
    isbn = factory.LazyAttribute(lambda x: fake.isbn())
    title = factory.LazyAttribute(lambda x: fake.title())
    genre = factory.LazyAttribute(lambda x: GenreFactory().id)
    printer = factory.LazyAttribute(lambda x: BookCompanyFactory().id)
    publisher = factory.LazyAttribute(lambda x: BookCompanyFactory().id)
    publish_year = factory.LazyAttribute(lambda x: fake.year())
    creator = factory.LazyAttribute(lambda x: LibrarianFactory().id)
