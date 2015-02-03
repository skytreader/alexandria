from flask import Blueprint, redirect, render_template, request
from flask.ext.login import login_required
from forms import LoginForm, SearchForm

librarian = Blueprint('librarian', __name__)

@librarian.route("/")
def index():
    form = SearchForm(request.form)
    return render_template("home.jinja", form=form)

@librarian.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        user = Librarian.query.filter_by(username=form.username.data).first()

        if user and user.password == form.password.data:
            session["user_id"] = user.id


    return render_template("login.jinja", form=form)

@librarian.route("/dashboard/")
@login_required
def dashboard():
    pass
