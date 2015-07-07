import factory
import faker
import random

from librarian import models

fake = Faker()

class LibrarianFactory(factory.Factory):
    class Meta:
        model = models.Librarian

    username = fake.user_name()
    password = fake.password()

class GenreFactory(factory.Factory):
    class Meta:
        model = models.Genre

    genre_name = random.choice(("Horror", "Sci-Fi", "Fantasy", "Philosophy"))
