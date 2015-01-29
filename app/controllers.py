from flask import Blueprint, render_template, request
from forms import SearchForm

librarian = Blueprint('librarian', __name__)

@librarian.route("/")
def index():
    form = SearchForm(request.form)
    return render_template("home.jinja", form=form)
