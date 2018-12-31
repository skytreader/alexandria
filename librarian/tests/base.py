# -*- coding: utf-8 -*-
from flask_testing import TestCase
from librarian.models import get_or_create, Librarian, Role
from librarian.tests.factories import LibrarianFactory
import librarian
import logging
import unittest

librarian.app.config["TESTING"] = True
librarian.init_db()
librarian.init_blueprints()

class AppTestCase(TestCase):
    
    def create_app(self):
        return librarian.app
    
    def setUp(self):
        self.app = self.create_app()
        self.ORIGINAL_LOG_LEVEL = self.app.logger.level
        self.ROLE_IDS = {}
        self.admin_user = get_or_create(Librarian, will_commit=True, username="admin", password="admin", is_user_active=True, can_read=True, can_write=True, can_exec=True)
        roles = ("Author", "Illustrator", "Editor", "Translator")
        
        for r in roles:
            _r = get_or_create(Role, will_commit=True, name=r,
              display_text="%s(s)" % r, creator_id=self.admin_user.id)
            self.ROLE_IDS[r] = _r.id
        librarian.db.session.commit()

    def make_current_user(self):
        """
        Create a random current user (other than the default admin user).

        Returns the random user which is now "current user". Note that some tests
        may opt not to catch this return value and just call this method for the
        side effects.
        """
        _user = LibrarianFactory()
        librarian.db.session.add(_user)
        librarian.db.session.flush()
        self.set_current_user(_user)
        return _user

    def set_current_user(self, user):
        with self.client.session_transaction() as sesh:
            sesh["user_id"] = user.id
            sesh["_fresh"] = True

    def verify_inserted(self, model, **kwargs):
        """
        Verify that the record described by **kwargs is inserted into the table
        represented by the given model. Returns the inserted record (if the
        assert succeeds.
        """
        record = librarian.db.session.query(model).filter_by(**kwargs).first()
        self.assertTrue(record is not None)
        return record

    def session_add_all(self, records):
        for r in records:
            librarian.db.session.add(r)

    def verify_does_not_exist(self, model, **kwargs):
        """
        Verify that the record described by **kwargs is not yet in the table
        represented by the given model.
        """
        record = librarian.db.session.query(model).filter_by(**kwargs).first()
        self.assertTrue(record is None)

    def tearDown(self):
        """
        Rollback any pending transactions and delete the contents of the tables.

        This is done directly on DB level. Note that the "proper" SQLAlchemy
        way to do this would be https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything
        but it is unsuitable for unit testing since we drop _everything_.

        (Or it _might_ work but we will have to call `create_all` on setUp which
        is going to be a waste of time.)
        """
        librarian.db.session.rollback()
        librarian.db.engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
        librarian.db.engine.execute("DELETE FROM librarians;")
        librarian.db.engine.execute("DELETE FROM roles;")
        librarian.db.engine.execute("DELETE FROM genres;")
        librarian.db.engine.execute("DELETE FROM books;")
        librarian.db.engine.execute("DELETE FROM book_companies;")
        librarian.db.engine.execute("DELETE FROM imprints;")
        librarian.db.engine.execute("DELETE FROM contributors;")
        librarian.db.engine.execute("DELETE FROM book_contributions;")
        librarian.db.engine.execute("DELETE FROM printers;")
        librarian.db.engine.execute("DELETE FROM pseudonyms;")
        librarian.db.engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
        librarian.db.session.commit()

        with librarian.app.app_context():
            librarian.cache.clear()

        self.app.logger.setLevel(self.ORIGINAL_LOG_LEVEL)
