from faker import Faker
from librarian import models
from librarian.tests.fakers import BookFieldsProvider

import factory
import random

fake = Faker()
fake.add_provider(BookFieldsProvider)


class LibrarianFactory(factory.Factory):
    class Meta:
        model = models.Librarian

    username = fake.user_name()
    password = fake.password()


class GenreFactory(factory.Factory):
    class Meta:
        model = models.Genre

    genre_name = random.choice(("Horror", "Sci-Fi", "Fantasy", "Philosophy"))


class BookCompanyFactory(factory.Factory):
    class Meta:
        model = models.BookCompany

    company_name = fake.company()


class BookFactory(factory.Factory):
    class Meta:
        model = models.Book

    isbn = fake.isbn()
    title = fake.title()
    genre = factory.SubFactory(GenreFactory)
    printer = factory.SubFactory(BookCompanyFactory)
    publisher = factory.SubFactory(BookCompanyFactory)
    publish_year = fake.year()
