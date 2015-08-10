from base import AppTestCase
from factories import *
from librarian.errors import ConstraintError
from librarian.models import Genre, get_or_create, ISBN_START

import librarian
import unittest

class ModelsTest(AppTestCase):
    
    def test_book_errors(self):
        with self.assertRaises(ConstraintError):
            BookFactory(publish_year = ISBN_START - 1)

        with self.assertRaises(ConstraintError):
            # This is an invalid ISBN. It should be 978-3-16-148410-0
            BookFactory(isbn="9783161484105")

    def test_get_and_create_commit(self):
        graphic_novels = (librarian.db.session.query(Genre)
          .filter(Genre.name=="Graphic Novel").all())
        self.assertEqual([], graphic_novels)
        
        gn_genre = get_or_create(Genre, will_commit=True, name="Graphic Novel",
          creator=self.admin_user.id)

        templar = (librarian.db.session.query(Genre)
          .filter(Genre.name=="Graphic Novel").all())

        self.assertEqual(1, len(templar))
