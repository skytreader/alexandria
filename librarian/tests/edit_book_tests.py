from base import AppTestCase
from faker import Faker
from librarian.models import (
    BookContribution, Contributor, Role
)
from librarian.tests.factories import ContributorFactory
from librarian.tests.fakers import BookFieldsProvider
from librarian.tests.utils import create_book
from librarian.utils import BookRecord, Person

import librarian
import librarian.api as api

fake = Faker()
fake.add_provider(BookFieldsProvider)

class EditBookTests(AppTestCase):

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
