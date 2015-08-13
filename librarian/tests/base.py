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
        self.ROLE_IDS = {}
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
            _r = get_or_create(Role, will_commit=True, name=r,
              display_text="%s(s)" % r, creator=self.admin_user.id)
            self.ROLE_IDS[r] = _r.id
        librarian.db.session.flush()

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
        librarian.db.engine.execute("DELETE FROM book_persons;")
        librarian.db.engine.execute("DELETE FROM book_participants;")
        librarian.db.engine.execute("DELETE FROM pseudonyms;")
        librarian.db.engine.execute("SET FOREIGN_KEY_CHECKS = 1;")
        librarian.db.session.commit()
