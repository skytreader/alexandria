from app import app, db
from app.forms import AddBooksForm
from flask import Blueprint
from flask.ext.login import current_user, login_required
from models import get_or_create, Book, BookCompany, BookParticipant, BookPerson, Genre, Role

import re

librarian_api = Blueprint("librarian_api", __name__)

def __create_bookperson(form_data):
    """
    Create a bookperson record from the given form_data. Return the created
    record, if any. Else return None.

    The record is added to the session but not committed.
    """
    parse = re.split(r",\s+", form_data)
    # FIXME What if it is a single-name pseudonym? E.g., Moebius
    if len(parse) == 2:
        return get_or_create(BookPerson, firstname=form_data[1], lastname=form_data[0],
          creator=current_user.get_id())

    return None

@librarian_api.route("/book_adder", methods=["POST"])
@login_required
def book_adder():
    """
    Assumes that the data has been stripped clean of leading and trailing spaces.
    """
    form = AddBooksForm()
    app.logger.info(str(form))

    if form.validate_on_submit():
        # Genre first
        genre = get_or_create(Genre, genre_name=form.genre.data,
          creator=current_user.get_id())

        # Publishing information
        publisher = get_or_create(BookCompany, company_name=form.publisher.data,
          creator=current_user.get_id())
        printer = get_or_create(BookCompany, company_name=form.printer.data,
          creator=current_user.get_id())

        # Book
        book = Book(isbn=form.isbn.data, title=form.title.data,
          genre=genre.record_id, creator=current_user.get_id(),
          publisher=publisher.record_id, printer=printer.record_id,
          publish_year=int(form.year.data))
        db.session.add(book)

        # Create the BookPersons
        author = __create_bookperson(form.authors.data)
        illustrator = __create_bookperson(form.illustrators.data)
        editor = __create_bookperson(form.editors.data)
        translator = __create_bookperson(form.translators.data)

        #FIXME This part is shaky
        #FIXME I think we should cache.
        author_role = Role.query.filter_by(role_name="Author").first()
        illus_role = Role.query.filter_by(role_name="Illustrator").first()
        editor_role = Role.query.filter_by(role_name="Editor").first()
        trans_role = Role.query.filter_by(role_name="Translator").first()

        # Assign participation
        if author:
            author_part = BookParticipant(book.record_id, author.record_id,
              author_role.record_id, creator=current_user.get_id())
            db.session.add(author_part)

        if illustrator:
            illus_part = BookParticipant(book.record_id, illustrator.record_id,
              illus_role.record_id, creator=current_user.get_id())
            db.session.add(illus_part)

        if editor:
            editor_part = BookParticipant(book.record_id, editor.record_id,
              editor_role.record_id, creator=current_user.get_id())
            db.session.add(editor_part)

        if translator:
            translator_part = BookParticipant(book.record_id, translator.record_id,
              trans_role.record_id, creator=current_user.get_id())
            db.session.add(translator_part)

        db.session.commit()

        return "Accepted", 200
    
    return "Error", 400
