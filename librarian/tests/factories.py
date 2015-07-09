from faker import Faker
from librarian import models
from librarian.tests.fakers import BookFieldsProvider
from sqlalchemy import orm

import factory
import factory.alchemy
import random
import sqlalchemy

fake = Faker()
fake.add_provider(BookFieldsProvider)

engine = sqlalchemy.create_engine('mysql://root@127.0.0.1/alexandria_test')
session = orm.scoped_session(orm.sessionmaker())
session.configure(bind=engine)


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
    creator = LibrarianFactory()


class BookCompanyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.BookCompany
        sqlalchemy_session = session

    company_name = fake.company()
    creator = LibrarianFactory()


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
