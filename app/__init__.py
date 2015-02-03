from controllers import librarian

from flask import Flask

from flask.ext.login import LoginManager

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config")

db = SQLAlchemy(app)
from models import Librarians
app.register_blueprint(librarian)
db.create_all()
db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)
