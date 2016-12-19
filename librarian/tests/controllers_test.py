# -*- coding: utf-8 -*-
from base import AppTestCase

class ControllersTest(AppTestCase):
    
    def setUp(self):
        super(ControllersTest, self).setUp()

    def test_login(self):
        successful_data = {"librarian_username": "admin", "librarian_password": "admin"}
        
        success_case = self.client.post("/login/", data=successful_data)
        self.assertEqual(302, success_case.status_code)

        nonexistent_data = {"librarian_username": "nimda", "librarian_password": "nimda"}

        fail_case = self.client.post("/login/", data=nonexistent_data)
        # Should just render the login page with flash messages.
        self.assertEqual(200, fail_case.status_code)
    
    def test_logged_in_redirect(self):
        self.set_current_user(self.admin_user)
        visit_redirect = self.client.get("/login/")
        self.assertEqual(302, visit_redirect.status_code)
        
        visit_redirected = self.client.get(visit_redirect.headers["Location"])
        self.assertEqual(200, visit_redirected.status_code)

    def test_plain_login(self):
        visit = self.client.get("/login/")
        self.assertEqual(200, visit.status_code)

    def test_index(self):
        visit = self.client.get("/")
        self.assertEqual(200, visit.status_code)

    def test_edit_books(self):
        self.set_current_user(self.admin_user)
        visit = self.client.get("/books/edit?bid=1")
        self.assertEqual(200, visit.status_code)

    def test_edit_books_badreq(self):
        self.set_current_user(self.admin_user)
        visit = self.client.get("/books/edit")
        self.assertEqual(400, visit.status_code)

    def test_add_books(self):
        self.set_current_user(self.admin_user)
        visit = self.client.get("/books/add")
        self.assertEqual(200, visit.status_code)
