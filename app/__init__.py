from controllers import librarian
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config")

db = SQLAlchemy(app)

def init_db(sql_string=None):
    if sql_string:
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_TEST_DATABASE_URI"]

    from models import Librarian
    app.register_blueprint(librarian)
    from api import librarian_api
    app.register_blueprint(librarian_api)
    db.create_all()
    db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    from models import Librarian
    return Librarian.query.filter_by(record_id=userid).first()
