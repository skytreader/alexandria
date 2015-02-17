from api import librarian_api
from controllers import librarian
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config")

db = SQLAlchemy(app)
from models import Librarians
app.register_blueprint(librarian)
app.register_blueprint(librarian_api)
db.create_all()
db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return Librarians.query.filter_by(record_id=userid).first()
