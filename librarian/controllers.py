# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user
from forms import AddBooksForm, EditBookForm, LoginForm, SearchForm
from librarian import api
from librarian.utils import StatsDescriptor
from utils import route_exists

import config
import flask
import json

librarian_bp = Blueprint('librarian', __name__)

@librarian_bp.route("/")
def index():
    from flask.ext.login import current_user
    form = SearchForm(request.form)
    styles = ("index.css",)
    return render_template("home.jinja", search_form=form, stylesheets=styles,
      has_current_user=current_user.get_id() is not None)

@librarian_bp.route("/login/", methods=["GET", "POST"])
def login():
    from flask.ext.login import current_user
    from models import Librarian
    form = LoginForm()

    if form.validate_on_submit():
        user = Librarian.query.filter_by(username=form.librarian_username.data, is_user_active=True).first()

        if user and user.password == form.librarian_password.data:
            login_user(user)
            # Should not matter becuase redirect is coming up but, oh well
            next_url = request.args.get("next")

            if next_url and not route_exists(next_url):
                return flask.abort(400)

            return redirect(next_url or url_for("librarian.dash"), code=302)
        else:
            flash("Wrong user credentials")
    elif not current_user.is_anonymous():
        return redirect(url_for("librarian.dash", code=302))

    return render_template("login.jinja", form=form)

@librarian_bp.route("/dashboard")
@login_required
def dash():
    stats = json.loads(api.quick_stats().data)
    contribs_per_book = StatsDescriptor.contrib_density(stats["participants_per_book"])
    cpb_stat = ("%.2f. Your library features %.2f contributors per book. %s." %
      (stats["participants_per_book"], stats["participants_per_book"],
      contribs_per_book.title()))
    
    book_count_stat = ("%d. Number of books currently in your library. %s." %
      (stats["book_count"], StatsDescriptor.book_count(stats["book_count"]).title()))
    
    _top_author = {"name": " ".join((stats["top_author"][2], stats["top_author"][1])),
      "count": stats["top_author"][3]}
    top_author = "{count}. {name} has authored the most books in your collection. Favorite.".format(**_top_author)
    
    recent_books = stats["recent_books"]

    return render_template("dashboard.jinja", contrib_stat=cpb_stat,
      recent_books=recent_books, book_count_stat=book_count_stat,
      top_author=top_author)

@librarian_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("librarian.index"))

@librarian_bp.route("/books/add")
@login_required
def add_books():
    form = AddBooksForm()
    scripts = ["jquery.validate.min.js", "jquery.form.min.js", "Queue.js",
      "add-books/main.js", "add-books/book-details.js", "add-books/types.js",
      "utils/visual-queue.js", "utils/misc.js", "utils/isbn-verify.js",
      "jquery-ui.min.js", "lodash.js", "alertify.min.js"]

    if config.DEVEL:
        scripts.insert(0, "add-books/testdata.js")

    styles = ("add_books.css", "jquery-ui.min.css", "jquery-ui.structure.min.css",
      "jquery-ui.theme.min.css", "alertify.css", "alertify-default-theme.css")
    return render_template("add_books.jinja", form=form, scripts=scripts, stylesheets=styles)

@librarian_bp.route("/books/edit")
@login_required
def edit_books():
    form = EditBookForm()
    scripts = ["jquery.validate.min.js", "jquery.form.min.js", "Queue.js",
      "add-books/main.js", "add-books/book-details.js", "add-books/types.js",
      "utils/visual-queue.js", "utils/misc.js", "utils/isbn-verify.js",
      "jquery-ui.min.js", "lodash.js", "alertify.min.js"]

    if config.DEVEL:
        scripts.insert(0, "add-books/testdata.js")

    styles = ("add_books.css", "jquery-ui.min.css", "jquery-ui.structure.min.css",
      "jquery-ui.theme.min.css", "alertify.css", "alertify-default-theme.css")
    return render_template("edit-book.jinja", form=form, scripts=scripts, stylesheets=styles)

@librarian_bp.route("/books")
def show_books():
    books = json.loads(api.get_books().data)["data"]
    scripts = ("show-books/main.js",)
    styles = ("books.css",)
    return render_template("books.jinja", scripts=scripts, stylesheets=styles,
      books=books)

@librarian_bp.route("/search")
def search():
    search_form = SearchForm(request.form)
    searchq = request.args.get("q")
    books = api.search(searchq)
    styles = ("books.css",)
    return render_template("books.jinja", stylesheets=styles, books=books,
      query=searchq, search_form=search_form)
