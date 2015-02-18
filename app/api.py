from app import app
from flask import Blueprint
from flask.ext.login import login_required
from models import Books, Genres, BookCompanies, BookPersons

librarian_api = Blueprint("librarian_api", __name__)

@librarian_api.route("/book_adder")
@login_required
def book_adder():
    return "Hello there."

app.register_blueprint(librarian_api)
