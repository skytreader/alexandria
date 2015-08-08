from flask.ext.testing import TestCase
from librarian.models import get_or_create, Librarian, Role
import librarian
import logging
import unittest

librarian.app.config["TESTING"] = True
librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])
librarian.init_blueprints()

class AppTestCase(TestCase):
    
    def create_app(self):
        return librarian.app
    
    def setUp(self):
        self.app = self.create_app()
        """
        admin_user = Librarian(username="admin", password="admin",
          is_user_active=True, can_read=True, can_write=True, can_exec=True)
        librarian.db.session.add(admin_user)
        roles = ("Author", "Illustrator", "Editor", "Translator")
        for r in roles:
            librarian.db.session.add(Role(role_name=r, role_display="%s(s)"%r,
              creator=admin_user.record_id))

        logging.info("#######CHAD########## flushing stuff")
        librarian.db.session.flush()
        """
        self.admin_user = get_or_create(Librarian, will_commit=True, username="admin", password="admin", is_user_active=True, can_read=True, can_write=True, can_exec=True)
        roles = ("Author", "Illustrator", "Editor", "Translator")
        
        for r in roles:
            get_or_create(Role, will_commit=True, name=r, display_text="%s(s)" % r,
              creator=self.admin_user.id)
        librarian.db.session.flush()

    def tearDown(self):
        librarian.db.session.rollback()
        # Delete the contents of the tables.
        librarian.db.engine.execute("SET FOREIGN_KEY_CHECKS = 0;")
        librarian.db.engine.execute("DELETE FROM librarians;")
        librarian.db.engine.execute("DELETE FROM roles;")
        librarian.db.engine.execute("DELETE FROM genres;")
        librarian.db.engine.execute("DELETE FROM books;")
        librarian.db.engine.execute("DELETE FROM book_companies;")
        librarian.db.engine.execute("DELETE FROM imprints;")
        librarian.db.engine.execute("DELETE FROM book_persons;")
        librarian.db.engine.execute("DELETE FROM book_participants;")
        librarian.db.engine.execute("DELETE FROM pseudonyms;")
        librarian.db.engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
        librarian.db.session.commit()
