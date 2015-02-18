from app import app
from app.forms import AddBooksForm
from flask import Blueprint
from flask.ext.login import login_required
from models import Books, Genres, BookCompanies, BookPersons

librarian_api = Blueprint("librarian_api", __name__)

@librarian_api.route("/book_adder")
@login_required
def book_adder():
    form = AddBooksForm()

    if form.validate_on_submit():
        # TODO add the models here

        return "Accepted", 200
    
    return "Error", 400
