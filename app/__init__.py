from flask import Flask, render_template, request

from flask.ext.sqlalchemy import SQLAlchemy

from forms import SearchForm

app = Flask(__name__)

app.config.from_object("config")

db = SQLAlchemy(app)

@app.route("/")
def index():
    form = SearchForm(request.form)
    return render_template("home.jinja", form=form)
