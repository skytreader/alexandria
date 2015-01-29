from controllers import librarian

from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config")

app.register_blueprint(librarian)

db = SQLAlchemy(app)
