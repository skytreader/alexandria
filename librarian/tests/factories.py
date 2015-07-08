import factory
import faker
import random

from librarian import models
from librarian.tests.fakers import BookFieldsProvider

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
    genre = GenreFactory().record_id
    printer = BookCompanyFactory().record_id
    publisher = BookCompanyFactory().record_id
    publish_year = fake.year()
