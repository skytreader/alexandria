from flask.ext.wtf import Form
from librarian.custom.forms import JsonField
from wtforms import HiddenField, PasswordField, TextField
from wtforms.validators import Length, Required

class SearchForm(Form):
    search_term = TextField("Search for", [Required(message="What are you looking for?")])

class LoginForm(Form):
    librarian_username = TextField("Username",
      [Required(message="Enter your username"), Length(max=50)])
    librarian_password = PasswordField("Password", [Required(message="Enter your password")])

class AddBooksForm(Form):
    isbn_message = "ISBN is a book's identifier and can often be found at the book's copyright page or near the barcode."
    isbn = HiddenField("ISBN", [Required(message=isbn_message), Length(max=13)])
    title = HiddenField("Title",
      [Required(message="Book's Title"), Length(max=255)])
    genre = HiddenField("Genre",
      [Required(message="Genre"), Length(max=20)])

    # Hardcode for now, so this makes roles.role_display kinda pointless
    authors = JsonField("Author(s)")
    illustrators = JsonField("Illustrator(s)")
    editors = JsonField("Editor(s)")
    translators = JsonField("Translator(s):")

    publisher = HiddenField("Publisher",
      [Required(message="Publisher"), Length(max=255)])
    printer = HiddenField("Printer",
      [Required(message="Printer"), Length(max=255)])
    # TODO Clarify this in models!!!
    year = HiddenField("Year", [Required(message="Edition Year")])

    def __str__(self):
        return "".join((str(self.isbn.raw_data), str(self.title.raw_data),
          str(self.genre.raw_data), str(self.authors.raw_data),
          str(self.illustrators.raw_data), str(self.editors.raw_data),
          str(self.translators.raw_data), str(self.publisher.raw_data),
          str(self.printer.raw_data), str(self.year.raw_data)))
