from flask.ext.wtf import Form
from wtforms import PasswordField, TextField
from wtforms.validators import Required

class SearchForm(Form):
    search_term = TextField("Search for", [Required(message="What are you looking for?")])

class LoginForm(Form):
    username = TextField("Username", [Required(message="Enter your username")])
    password = PasswordField("Password", [Required(message="Enter your password")])
