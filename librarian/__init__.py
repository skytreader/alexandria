# -*- coding: utf-8 -*-`
from flask import Flask
from flask.ext.cache import Cache
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)
cache = Cache(app, config=config.CACHE_CONFIG)
app.config.from_object("config")

db = SQLAlchemy(app)

def init_db(sql_string=None):
    if sql_string:
        # This is done for Flask SQLAlchemy
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_TEST_DATABASE_URI"]

    db.create_all()
    db.session.commit()

def init_blueprints():
    from controllers import librarian_bp
    app.register_blueprint(librarian_bp)
    from api import librarian_api
    app.register_blueprint(librarian_api)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "librarian.login"

@login_manager.user_loader
def load_user(userid):
    from models import Librarian
    return Librarian.query.filter_by(id=userid).first()
