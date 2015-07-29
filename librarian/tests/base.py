from librarian.models import get_or_create, Librarian, Role

import librarian
import logging
import unittest

librarian.app.config["TESTING"] = True
librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])
librarian.init_blueprints()

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = librarian.app.test_client()
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
            get_or_create(Role, will_commit=True, role_name=r, role_display="%s(s)" % r,
              creator=self.admin_user.record_id)

    def tearDown(self):
        logging.info("#######CHAD########## rollback stuff")
        librarian.db.session.rollback()
