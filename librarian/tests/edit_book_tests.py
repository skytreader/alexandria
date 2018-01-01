from base import AppTestCase
from faker import Faker
from librarian.models import (
    Book, BookContribution, Contributor, Role
)
from librarian.tests.factories import ContributorFactory, LibrarianFactory
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.utils import create_book
from librarian.utils import BookRecord, Person

import copy
import librarian
import librarian.api as api

fake = Faker()
fake.add_provider(BookFieldsProvider)

class EditBookTests(AppTestCase):

    def test_title_edit_book(self):
        self.make_current_user()
        authors = [ContributorFactory().make_plain_person() for _ in range(3)]
        book = BookRecord(isbn=fake.isbn(), title=fake.title(),
          publisher="Mumford and Sons", author=authors, publish_year=2016,
          genre="Fiction")
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        existing = (
            librarian.db.session.query(Book)
            .filter(Book.isbn==book.isbn)
            .first()
        )
        self.assertEquals(book.title, existing.title)

        edit_data = BookRecord(isbn=book.isbn, title="This is a Ret Con",
          publisher=book.publisher, author=book.authors,
          publish_year=book.publish_year, genre=book.genre, id=book_id)
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        edited = (
            librarian.db.session.query(Book)
            .filter(Book.isbn==book.isbn)
            .first()
        )
        self.assertEquals(edit_data.title, edited.title)

    def test_edit_book_contrib_add(self):
        self.make_current_user()
        authors = [ContributorFactory().make_plain_person() for _ in range(3)]
        book = BookRecord(isbn=fake.isbn(), title=fake.title(),
          publisher="Mumford and Sons", author=authors, publish_year=2016,
          genre="Fiction")
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        additional_author = ContributorFactory().make_plain_person()
        _book_authors = copy.deepcopy(list(book.authors))
        _book_authors.append(additional_author)
        edit_data = BookRecord(isbn=book.isbn, title=book.title,
          publisher=book.publisher, author=_book_authors,
          publish_year=book.publish_year, genre=book.genre, id=book_id)
        librarian.db.session.commit()
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEqual(set(_book_authors), author_persons)

    def test_edit_book_contrib_delete_deactivate(self):
        """
        Test deleting a contribution from a book where the contributor ends up
        deactivated for lack of other contributions.
        """
        self.make_current_user()
        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors, publish_year=2016,
            genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        # The last author is the one we delete
        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            # Just for thoroughness, but in an ideal world BookContribution.active is sufficient
            .filter(Contributor.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        self.verify_inserted(Contributor, id=the_deleted.id, active=False)

    def test_edit_book_contrib_delete_keepactive(self):
        """
        Test deleting a contribution from a book where the contributor stays
        active from other books
        """
        self.make_current_user()
        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors, publish_year=2016,
            genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        # This will keep `the_deleted` alive. Get it?
        horcrux = BookRecord(
            isbn=fake.isbn(), title="Secrets of the Darkest Art",
            publisher="Scholastic", author=[the_deleted.make_plain_person()],
            publish_year=1967, genre="Black Magic"
        )
        librarian.db.session.commit()
        create_book(librarian.db.session, horcrux, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        # The last author is the one we delete
        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        # But the contributor remains active thanks to the horcrux!
        self.verify_inserted(Contributor, id=the_deleted.id, active=True)

    def test_edit_book_contrib_delete_selfkeepactive(self):
        """
        Test deleting a contribution from a book where the contributor stays
        active because it is still a contributor, in another role, for the same
        book.
        """
        self.make_current_user()
        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors,
            editor=[the_deleted.make_plain_person()],
            publish_year=2016, genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        # The last author is the one we delete
        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            editor=[the_deleted.make_plain_person()],
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        # But the contributor remains active thanks to being the editor!
        self.verify_inserted(Contributor, id=the_deleted.id, active=True)

    def test_edit_book_contrib_move(self):
        """
        Test that moving contributors between roles produce the desired effect.
        """
        self.make_current_user()
        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors, publish_year=2016,
            genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        # The last author is the one we delete
        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            editor=[the_deleted.make_plain_person()],
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        the_deleted = librarian.db.session.query(Contributor).filter(Contributor.id == the_deleted.id).first()
        self.verify_inserted(Contributor, id=the_deleted.id, active=True)

    def test_edit_book_contrib_correction(self):
        """
        Actual (unexpected) error encountered while live testing. It would seem
        that the database might have race conditions where a pending book is
        uncommitted resulting to errors when pairing a Contributor with a role.
        """
        self.set_current_user(self.admin_user)

        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory(lastname="Jill", firstname="Jack"), ContributorFactory(lastname="Stewart", firstname="John")]
        authors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", author=authors, publish_year=2016,
            genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()
        js_autobio = BookRecord(
            isbn=fake.isbn(), title="JS Autobio", publisher="Green Cross",
            author=[Person(lastname="Stewart", firstname="Jon")],
            publish_year=2016, genre="Fiction"
        )
        create_book(librarian.db.session, js_autobio, self.admin_user)
        # This is what makes this pass.
        librarian.db.session.commit()

        author_role = Role.get_preset_role("Author")
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])
        self.assertEquals(set(authors), author_persons)

        edited_book_authors = [Person(lastname="Jill", firstname="Jack"), Person(lastname="Stewart", firstname="Jon")]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, author=edited_book_authors,
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        self.verify_inserted(Contributor, id=the_deleted.id, active=False)

    def test_remove_duplicate_contributor_team(self):
        """
        Yet another actual test case encountered live.

        For some reason, Preludes and Nocturnes was saved with the same
        Contributors for both Translators and Editors (note that Preludes and
        Nocturnes is not supposed to have Translators). Deleting all
        Translators does not seem to work.

        UPDATE: Looks like it was, indeed, a side-effect of the update code.
        When editing the Translators role, the Editors field is passed, creating
        the discrepancy.
        """
        self.make_current_user()
        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory() for _ in range(3)]
        editors = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", editor=editors, translator=editors,
            publish_year=2016, genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        editor_role = Role.get_preset_role("Editor")
        translator_role = Role.get_preset_role("Translator")
        book_editors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==editor_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        book_translators = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==translator_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        editor_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_editors
        ])
        self.assertEquals(set(editors), editor_persons)
        self.assertEquals(set(book_editors), set(book_translators))

        # Delete all translators
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, editor=editors,
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_editors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==editor_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        updated_editor_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_editors
        ])
        self.assertEqual(set(editor_persons), updated_editor_persons)
        updated_book_translators = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==translator_role.id)
            .filter(BookContribution.active)
            .all()
        )
        self.assertEqual(0, len(updated_book_translators))
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        for translator in book_translators:
            self.verify_inserted(
                BookContribution, book_id=book_id, contributor_id=translator.id,
                role_id=translator_role.id, active=False
            )
            self.verify_inserted(Contributor, id=translator.id, active=True)

    def test_edit_book_contrib_correction(self):
        """
        Another actual error encountered in testing. We are modifying
        "MIlo Manara" to "Milo Manara" but it would seem that get_or_create
        fetches "MIlo Manara" when given "Milo Manara".
        """
        self.set_current_user(self.admin_user)

        # These two are always parallel arrays.
        contributor_objs = [ContributorFactory(lastname="Manara", firstname="MIlo")]
        illustrators = [co.make_plain_person() for co in contributor_objs]
        the_deleted = contributor_objs[-1]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(),
            publisher="Mumford and Sons", illustrator=illustrators, publish_year=2016,
            genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()

        illustrator_role = Role.get_preset_role("Illustrator")
        book_illustrators = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==illustrator_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        illustrator_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_illustrators
        ])
        self.assertEquals(set(illustrators), illustrator_persons)

        edited_book_illustrators = [Person(lastname="McKean", firstname="Dave"), Person(lastname="Manara", firstname="Milo")]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title,
            publisher=book.publisher, illustrator=edited_book_illustrators,
            publish_year=book.publish_year, genre=book.genre, id=book_id
        )
        librarian.db.session.commit()
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)

        updated_book_illustrators = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==illustrator_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        updated_illustrator_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_illustrators
        ])
        self.assertEqual(set(edited_book_illustrators), updated_illustrator_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=illustrator_role.id, active=False
        )
        self.verify_inserted(Contributor, id=the_deleted.id, active=False)

    def __make_book(self):
        contributor_objs = [ContributorFactory() for _ in range(3)]
        authors = [co.make_plain_person() for co in contributor_objs]
        book = BookRecord(
            isbn=fake.isbn(), title=fake.title(), publisher="somepublisher",
            author=authors, publish_year=2017, genre="Fiction"
        )
        book_id = create_book(librarian.db.session, book, self.admin_user)
        librarian.db.session.commit()
        return book_id

    def __basic_edit_test(self, book_id):
        author_role = Role.get_preset_role("Author")
        book = (
            librarian.db.session.query(Book)
            .filter(Book.id==book_id)
            .first()
        )
        book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            .filter(Contributor.active)
            .all()
        )
        authors = [co.make_plain_person() for co in book_authors]
        the_deleted = book_authors[-1]
        author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in book_authors
        ])

        edited_book_authors = authors[0:-1]
        edit_data = BookRecord(
            isbn=book.isbn, title=book.title, publisher=book.publisher,
            author=edited_book_authors, publish_year=book.publish_year,
            genre=book.genre.name, id=book_id
        )
        edit_book = self.client.post("/api/edit/books", data=edit_data.request_data())
        self.assertEqual(200, edit_book.status_code)
        updated_book_authors = (
            librarian.db.session.query(Contributor)
            .filter(BookContribution.book_id==book_id)
            .filter(BookContribution.contributor_id==Contributor.id)
            .filter(BookContribution.role_id==author_role.id)
            .filter(BookContribution.active)
            # Just for thoroughness, but in an ideal world BookContribution.active is sufficient
            .filter(Contributor.active)
            .all()
        )
        updated_author_persons = set([
            Person(firstname=a.firstname, lastname=a.lastname)
            for a in updated_book_authors
        ])
        self.assertEqual(set(edited_book_authors), updated_author_persons)
        # Verify that the BookRecord for the "deleted" contribution remains
        # but inactive.
        self.verify_inserted(
            BookContribution, book_id=book_id, contributor_id=the_deleted.id,
            role_id=author_role.id, active=False
        )
        self.verify_inserted(Contributor, id=the_deleted.id, active=False)

    def test_trigger_invalidrequesterror(self):
        self.make_current_user()
        book1 = self.__make_book()
        book2 = self.__make_book()
        self.__basic_edit_test(book1)
        self.__basic_edit_test(book2)
