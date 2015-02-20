from app import app, db
from app.forms import AddBooksForm
from flask import Blueprint
from flask.ext.login import current_user, login_required
from models import get_or_create, Book, BookCompany, BookPerson, Genre, Role

librarian_api = Blueprint("librarian_api", __name__)

@librarian_api.route("/book_adder", methods=["POST"])
@login_required
def book_adder():
    form = AddBooksForm()
    app.logger.info(str(form))

    if form.validate_on_submit():
        # Genre first
        genre = get_or_create(Genre, genre_name=form.genre)

        # Book
        book = Book(isbn=form.isbn.data, title=form.title.data, year=form.year.data,
        genre=genre, creator=current_user)
        db.add(book)

        # Create the BookPersons
        author_last, author_first = form.authors.data.split(", ")
        illus_last, illus_first = form.illustrators.data.split(", ")
        editor_last, editor_first = form.editors.data.split(", ")
        trans_last, trans_first = form.translators.data.split(", ")

        author = get_or_create(BookPerson, lastname=author_last,
          firstname=author_first)
        illustrator = get_or_create(BookPerson, lastname=illus_last,
          firstname=illus_first)
        editor = get_or_create(BookPerson, lastname=editor_last,
          firstname=editor_first)
        translator = get_or_create(BookPerson, lastname=trans_last,
          firstname=trans_first)

        #FIXME This part is shaky
        #FIXME I think we should cache.
        author_role = Role.query.filter_by(role_name="Author").first()
        illus_role = Role.query.filter_by(role_name="Illustrator").first()
        editor_role = Role.query.filter_by(role_name="Editor").first()
        trans_role = Role.query.filter_by(role_name="Translator").first()

        # Assign participation
        author_part = BookParticipant(book.record_id, author.record_id,
          author_role.record_id)
        illus_part = BookParticipant(book.record_id, illustrator.record_id,
          illus_role.record_id)
        editor_part = BookParticipant(book.record_id, editor.record_id,
          editor_role.record_id)
        translator_part = BookParticipant(book.record_id, translator.record_id,
          trans_role.record_id)

        db.add(author_part)
        db.add(illus_part)
        db.add(editor_part)
        db.add(translator_part)

        # Publishing information
        publisher = get_or_create(BookCompany, company_name=form.publisher.data)
        printer = get_or_create(BookCompany, company_name=form.printer.data)

        return "Accepted", 200
    
    return "Error", 400
