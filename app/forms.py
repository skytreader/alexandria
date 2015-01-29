from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import Required

class SearchForm(Form):
    search_term = TextField("Search for", [Required(message="What are you looking for?")])
