from flask.ext.wtf import Form
from wtforms import PasswordField, TextField
from wtforms.validators import Required

class SearchForm(Form):
    search_term = TextField("Search for", [Required(message="What are you looking for?")])

class LoginForm(Form):
    username = TextField("Username", [Required(message="Enter your username")])
    password = PasswordField("Password", [Required(message="Enter your password")])

class AddBooks(Form):
    isbn_message = "ISBN is a book's identifier and can often be found at the book's copyright page or near the barcode."
    isbn = TextField("ISBN", [Required(message=isbn_message)])
    title = TextField("Title", [Required(message="Book's Title")])
    genre = TextField("Genre", [Required(message="Genre")])

    # Hardcode for now, so this makes roles.role_display kinda pointless
    authors = TextField("Author(s)")
    illustrators = TextField("Illustrator(s)")
    editors = TextField("Editor(s)")
    translators = TextField("Translator(s):")

    publisher = TextField("Publisher", [Required(message="Publisher")])
    printer = TextField("Printer", [Required(message="Printer")])
    # TODO Clarify this in models!!!
    year = TextField("Year", [Required(message="Edition Year")])
