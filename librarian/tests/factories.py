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

    username = fake.user_name()
    password = fake.password()


class GenreFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Genre
        sqlalchemy_session = librarian.db.session

    genre_name = random.choice(("Horror", "Sci-Fi", "Fantasy", "Philosophy"))
    creator = factory.SubFactory(LibrarianFactory)


class BookCompanyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.BookCompany
        sqlalchemy_session = librarian.db.session

    company_name = fake.company()
    creator = factory.SubFactory(LibrarianFactory)


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Book
        sqlalchemy_session = librarian.db.session

    isbn = fake.isbn()
    title = fake.title()
    genre = factory.SubFactory(GenreFactory)
    printer = factory.SubFactory(BookCompanyFactory)
    publisher = factory.SubFactory(BookCompanyFactory)
    publish_year = fake.year()
    creator = factory.SubFactory(LibrarianFactory)
