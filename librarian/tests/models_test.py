# -*- coding: utf-8 -*-
from base import AppTestCase
from factories import *
from librarian.errors import ConstraintError
from librarian.models import Book, Contributor, Genre, get_or_create, ISBN_START

import librarian
import unittest

class ModelsTest(AppTestCase):
    
    def setUp(self):
        super(ModelsTest, self).setUp()
        self.gn_query = (librarian.db.session.query(Genre)
          .filter(Genre.name=="Graphic Novel"))
    
    def test_book_errors(self):
        with self.assertRaises(ConstraintError):
            # This is an invalid ISBN. It should be 978-3-16-148410-0
            BookFactory(isbn="9783161484105")

    def test_get_or_create_commit(self):
        other_librarian = LibrarianFactory()
        librarian.db.session.flush()
        graphic_novels = self.gn_query.all()
        self.assertEqual([], graphic_novels)
        
        gn_genre = get_or_create(Genre, will_commit=True, name="Graphic Novel",
          creator=other_librarian)

        self.assertEqual("Graphic Novel", gn_genre.name)

        graphic_novels = self.gn_query.all()

        self.assertEqual(1, len(graphic_novels))
        self.assertEqual(gn_genre, graphic_novels[0])

    def test_get_or_create_nocommit(self):
        graphic_novels = self.gn_query.all()
        self.assertEqual([], graphic_novels)

        gn_genre = get_or_create(Genre, will_commit=False, name="Graphic Novel",
          creator = self.admin_user)

        self.assertEqual("Graphic Novel", gn_genre.name)

        graphic_novels = self.gn_query.all()

        self.assertEqual([], graphic_novels)

    def test_get_or_create_preexisting(self):
        other_librarian = LibrarianFactory()
        horror = Genre(name="Horror", creator=self.admin_user)
        librarian.db.session.add(horror)
        librarian.db.session.flush()

        horror_genre = (librarian.db.session.query(Genre)
          .filter(Genre.name=="Horror").all())

        self.assertEqual(1, len(horror_genre))

        horror_goc = get_or_create(Genre, name="Horror")
        self.assertEqual("Horror", horror_goc.name)

        # Test that creator should be ignored when getting via get_or_create
        horror_other = get_or_create(Genre, name="Horror",
          creator=other_librarian)
        self.assertEqual(horror_goc, horror_other)

    def test_get_or_create_contributors_dne(self):
        contrib = get_or_create(Contributor, will_commit=True, firstname="David", lastname="Tennant", creator=self.admin_user)

        self.assertTrue(contrib is not None)

    def test_get_or_create_casing(self):
        milo = (
            librarian.db.session.query(Contributor)
            .filter(Contributor.lastname=="Manara")
            .first()
        )
        self.assertTrue(milo is None)
        ContributorFactory(firstname="MIlo", lastname="Manara", creator=self.admin_user)
        librarian.db.session.flush()

        milo = (
            librarian.db.session.query(Contributor)
            .filter(Contributor.lastname=="Manara")
            .first()
        )
        self.assertTrue(milo is not None)

        milo_clone = get_or_create(
            Contributor, will_commit=True, firstname="Milo", lastname="Marana",
            creator=self.admin_user
        )

        self.assertEqual("Milo", milo_clone.firstname)
        self.assertNotEqual("MIlo", milo_clone.firstname)
    
    def test_get_or_create_insuff(self):
        templar = (librarian.db.session.query(Book)
          .filter(Book.title=="Templar").all())

        self.assertEqual([], templar)

        self.assertRaises(KeyError, get_or_create, Book, will_commit=True,
          title="Templar")
