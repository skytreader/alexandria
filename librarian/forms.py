from flask.ext.wtf import Form
from wtforms import HiddenField, PasswordField, TextField
from wtforms.validators import Required

class SearchForm(Form):
    search_term = TextField("Search for", [Required(message="What are you looking for?")])

class LoginForm(Form):
    librarian_username = TextField("Username", [Required(message="Enter your username")])
    librarian_password = PasswordField("Password", [Required(message="Enter your password")])

class AddBooksForm(Form):
    isbn_message = "ISBN is a book's identifier and can often be found at the book's copyright page or near the barcode."
    isbn = HiddenField("ISBN", [Required(message=isbn_message)])
    title = HiddenField("Title", [Required(message="Book's Title")])
    genre = HiddenField("Genre", [Required(message="Genre")])

    # Hardcode for now, so this makes roles.role_display kinda pointless
    authors = HiddenField("Author(s)")
    illustrators = HiddenField("Illustrator(s)")
    editors = HiddenField("Editor(s)")
    translators = HiddenField("Translator(s):")

    publisher = HiddenField("Publisher", [Required(message="Publisher")])
    printer = HiddenField("Printer", [Required(message="Printer")])
    # TODO Clarify this in models!!!
    year = HiddenField("Year", [Required(message="Edition Year")])

    def __str__(self):
        return "".join((str(self.isbn.raw_data), str(self.title.raw_data),
          str(self.genre.raw_data), str(self.authors.raw_data),
          str(self.illustrators.raw_data), str(self.editors.raw_data),
          str(self.translators.raw_data), str(self.publisher.raw_data),
          str(self.printer.raw_data), str(self.year.raw_data)))
