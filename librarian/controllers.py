# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user
from forms import AddBooksForm, EditBookForm, LoginForm, SearchForm
from librarian import api
from librarian import app
from librarian.errors import InvalidRecordState
from librarian.utils import BookRecord, StatsDescriptor
from librarian.models import Book
from utils import route_exists

import config
import flask
import json
import time

librarian_bp = Blueprint('librarian', __name__)

@librarian_bp.route("/")
def index():
    from flask_login import current_user
    form = SearchForm(request.form)
    styles = ("index.css",)
    return render_template("home.jinja", search_form=form, stylesheets=styles,
      has_current_user=current_user.get_id() is not None)

@librarian_bp.route("/login/", methods=["GET", "POST"])
def login():
    from flask_login import current_user
    from models import Librarian
    form = LoginForm()
    app.logger.info("Got login form %s" % form)

    if form.validate_on_submit():
        user = Librarian.query.filter_by(username=form.librarian_username.data, is_user_active=True).first()

        if user and user.password == form.librarian_password.data:
            login_user(user)
            # Should not matter because redirect is coming up but, oh well
            next_url = request.args.get("next")

            if next_url and not route_exists(next_url):
                return flask.abort(400)

            return redirect(next_url or url_for("librarian.dash"), code=302)
        else:
            flash("Wrong user credentials")
    elif current_user.is_authenticated:
        return redirect(url_for("librarian.dash", code=302))

    return render_template("login.jinja", form=form)

@librarian_bp.route("/dashboard")
@login_required
def dash():
    stats = json.loads(api.quick_stats().data)
    contribs_per_book = StatsDescriptor.contrib_density(stats["participants_per_book"])

    if stats.get("pariticipants_per_book") > 0.0001:
        cpb_stat = (
            "%.2f. Your library features %.2f contributors per book. %s." %
            (stats["participants_per_book"], stats["participants_per_book"],
            contribs_per_book.title())
        )
    else:
        cpb_stat = None
    
    book_count_stat = ("%d. Number of books currently in your library. %s." %
      (stats["book_count"], StatsDescriptor.book_count(stats["book_count"]).title()))
    
    if stats.get("top_author"):
        _top_author = {"name": " ".join((stats["top_author"][2], stats["top_author"][1])),
          "count": stats["top_author"][3]}
        top_author = "{count}. {name} has authored the most books in your collection. Favorite.".format(**_top_author)
    else:
        top_author = []
    
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
      "add-books/main.js", "types/book-details.js", "add-books/types.js",
      "utils/visual-queue.js", "utils/misc.js", "utils/isbn-verify.js",
      "jquery-ui.min.js", "lodash.js", "alertify.min.js",
      "add-books/add-book-details.js", "add-books/stat-counter.js",
      "types/person.js"]

    if config.DEVEL:
        scripts.insert(0, "add-books/testdata.js")

    styles = ("add_books.css", "jquery-ui.min.css", "jquery-ui.structure.min.css",
      "jquery-ui.theme.min.css", "alertify.css", "alertify-default-theme.css")
    return render_template("add_books.jinja", form=form, scripts=scripts, stylesheets=styles)

@librarian_bp.route("/books/edit")
@login_required
def edit_books():
    form = EditBookForm()
    book_id = request.args.get("bid")

    if not book_id:
        return flask.abort(400)

    book_query = BookRecord.base_assembler_query().filter(Book.id == book_id)
    query_results = book_query.all()
    assembled = BookRecord.assembler(query_results)

    if not assembled:
        return flask.abort(400)
    elif len(assembled) > 1:
        raise InvalidRecordState("book id %s" % book_id)

    book = assembled[0]
    book_js = "var bookForEditing = JSON.parse(%s)" % json.dumps(json.dumps(book.__dict__))

    scripts = ["jquery.validate.min.js", "jquery.form.min.js", "Queue.js",
      "types/book-details.js", "edit-book/main.js", "edit-book/controller.js", 
      "utils/visual-queue.js", "utils/misc.js", "utils/isbn-verify.js",
      "jquery-ui.min.js", "lodash.js", "alertify.min.js", "types/person.js"]

    if config.DEVEL:
        scripts.insert(0, "add-books/testdata.js")

    styles = ("add_books.css", "jquery-ui.min.css", "jquery-ui.structure.min.css",
      "jquery-ui.theme.min.css", "alertify.css", "alertify-default-theme.css")
    return render_template(
        "edit-book.jinja", form=form, scripts=scripts, stylesheets=styles,
        misc_js = book_js, book_title=book.title
    )

@librarian_bp.route("/books")
def show_books():
    from flask_login import current_user
    load_start = time.time()
    books = json.loads(api.get_books().data)["data"]
    load_end = time.time()
    scripts = ("show-books/main.js",)
    styles = ("books.css",)

    user = current_user if current_user.is_authenticated else None

    return render_template("books.jinja", scripts=scripts, stylesheets=styles,
      books=books, user=user, perftime=(load_end - load_start))

@librarian_bp.route("/search")
def search():
    from flask_login import current_user
    user = current_user if current_user.is_authenticated else None
    search_form = SearchForm(request.form)
    searchq = request.args.get("q")
    search_start = time.time()
    books = api.search(searchq)
    search_end = time.time()
    styles = ("books.css",)
    return render_template("books.jinja", stylesheets=styles, books=books,
      query=searchq, search_form=search_form, user=user, perftime=(search_end - search_start))
