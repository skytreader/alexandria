from faker import Faker
from librarian import models
from librarian.tests.fakers import BookFieldsProvider
from sqlalchemy import orm

import factory
import factory.alchemy
import random

fake = Faker()
fake.add_provider(BookFieldsProvider)

session = orm.scoped_session(orm.sessionmaker())


class LibrarianFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Librarian
        sqlalchemy_session = session

    username = fake.user_name()
    password = fake.password()


class GenreFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Genre
        sqlalchemy_session = session

    genre_name = random.choice(("Horror", "Sci-Fi", "Fantasy", "Philosophy"))


class BookCompanyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.BookCompany
        sqlalchemy_session = session

    company_name = fake.company()


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Book
        sqlalchemy_session = session

    isbn = fake.isbn()
    title = fake.title()
    genre = factory.SubFactory(GenreFactory)
    printer = factory.SubFactory(BookCompanyFactory)
    publisher = factory.SubFactory(BookCompanyFactory)
    publish_year = fake.year()
    creator = LibrarianFactory(can_write = True)
