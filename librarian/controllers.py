from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user
from forms import AddBooksForm, LoginForm, SearchForm

import librarian

librarian_bp = Blueprint('librarian', __name__)

@librarian_bp.route("/")
def index():
    form = SearchForm(request.form)
    return render_template("home.jinja", form=form)

@librarian_bp.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        from models import Librarian
        user = Librarian.query.filter_by(username=form.librarian_username.data, is_user_active=True).first()

        if user and user.password == form.librarian_password.data:
            login_user(user)
            next_url = flask.request.args.get("next")

            if not librarian.app.url_map.get(next_url):
                return abort(400)

            return redirect(next_url or url_for("librarian.dash"))
        else:
            flash("Wrong user credentials")

    return render_template("login.jinja", form=form)

@librarian_bp.route("/dashboard")
@login_required
def dash():
    return render_template("dashboard.jinja")

@librarian_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("librarian.index"))

@librarian_bp.route("/books/add")
@login_required
def books():
    form = AddBooksForm()
    scripts = ("jquery.validate.min.js", "jquery.form.min.js", "Queue.js", "add-books/main.js",
      "add-books/book.js", "utils/visual-queue.js", "utils/misc.js")
    styles = ("add_books.css",)
    return render_template("add_books.jinja", form=form, scripts=scripts, stylesheets=styles)
