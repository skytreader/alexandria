# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user
from forms import AddBooksForm, LoginForm, SearchForm
from utils import route_exists

import config
import flask
import json
import librarian

librarian_bp = Blueprint('librarian', __name__)

@librarian_bp.route("/")
def index():
    form = SearchForm(request.form)
    styles = ("index.css",)
    return render_template("home.jinja", form=form, stylesheets=styles)

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
    stats = json.loads(librarian.api.quick_stats().data)
    contribs_per_book = librarian.utils.stats_adjective(stats["participants_per_book"])
    cpb_stat = ("%.2f. Your library features %.2f contributors per book. %s." %
      (stats["participants_per_book"], stats["participants_per_book"],
      contribs_per_book.title()))
    
    recent_books = stats["recent_books"]

    return render_template("dashboard.jinja", contrib_stat=cpb_stat, recent_books=recent_books)

@librarian_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("librarian.index"))

@librarian_bp.route("/books/add")
@login_required
def add_books():
    form = AddBooksForm()
    scripts = ["jquery.validate.min.js", "jquery.form.min.js", "Queue.js", "add-books/main.js",
      "add-books/types.js", "utils/visual-queue.js", "utils/misc.js", "utils/isbn-verify.js",
      "jquery-ui.min.js", "lodash.js", "alertify.js"]

    if config.DEVEL:
        scripts.insert(0, "add-books/testdata.js")

    styles = ("add_books.css", "jquery-ui.min.css", "jquery-ui.structure.min.css",
      "jquery-ui.theme.min.css", "alertify.css", "alertify-default-theme.css")
    return render_template("add_books.jinja", form=form, scripts=scripts, stylesheets=styles)

@librarian_bp.route("/books")
def show_books():
    from librarian.api import get_books

    books = json.loads(get_books().data)["data"]
    scripts = ("show-books/main.js",)
    styles = ("books.css",)
    return render_template("books.jinja", scripts=scripts, stylesheets=styles,
      books=books)

@librarian_bp.route("/search")
def search():
    from librarian.api import search
    searchq = request.args.get("q")
    books = search(searchq)
    styles = ("books.css",)
    return render_template("books.jinja", stylesheets=styles, books=books)
