# -*- coding: utf-8 -*-`
from flask import Flask
from flask_caching import Cache
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

import config
import os

app = Flask(__name__)
app.config.from_object(os.getenv("ALEXANDRIA_CONFIG", "config.DefaultAlexandriaConfig"))
cache = Cache(app, config=app.config["CACHE_CONFIG"])

db = SQLAlchemy(app)

def init_db():
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
