from flask import Blueprint, render_template, request
from forms import LoginForm, SearchForm

librarian = Blueprint('librarian', __name__)

@librarian.route("/")
def index():
    form = SearchForm(request.form)
    return render_template("home.jinja", form=form)

@librarian.route("/login/")
def login():
    form = LoginForm(request.form)
    return render_template("login.jinja", form=form)
