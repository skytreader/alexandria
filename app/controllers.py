from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user
from forms import LoginForm, SearchForm

librarian = Blueprint('librarian', __name__)

@librarian.route("/")
def index():
    form = SearchForm(request.form)
    return render_template("home.jinja", form=form)

@librarian.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        from models import Librarians
        user = Librarians.query.filter_by(username=form.username.data).first()

        if user and user.password == form.password.data:
            login_user(user)
            flash("Logged-in succesfully")
            return redirect(url_for("librarian.dash"))
        else:
            flash("Wrong user credentials")

    return render_template("login.jinja", form=form)

@librarian.route("/dashboard")
@login_required
def dash():
    return render_template("dashboard.jinja")
