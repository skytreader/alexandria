from librarian.models import get_or_create, Librarian, Role

import librarian
import unittest

librarian.app.config["TESTING"] = True
librarian.init_db(librarian.app.config["SQLALCHEMY_TEST_DATABASE_URI"])
librarian.init_blueprints()

class AppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = librarian.app.test_client()
        
        admin_user = get_or_create(Librarian, username="admin", password="admin", is_user_active=True, can_read=True, can_write=True, can_exec=True)
        roles = ("Author", "Illustrator", "Editor", "Translator")
        
        for r in roles:
            get_or_create(Role, role_name=r, role_display="%s(s)" % r,
              creator=admin_user.record_id)

