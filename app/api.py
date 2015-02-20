from app import app
from app.forms import AddBooksForm
from flask import Blueprint
from flask.ext.login import current_user, login_required
from models import get_or_create, Books, Genres, BookCompanies, BookPersons

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

        # Create the BookPersons
        author_last, author_first = form.authors.data.split(", ")
        illus_last, illus_first = form.illustrators.data.split(", ")
        editor_last, editor_first = form.editors.data.split(", ")
        trans_last, trans_first = form.translators.data.split(", ")

        return "Accepted", 200
    
    return "Error", 400
