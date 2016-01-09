# -*- coding: utf-8 -*-
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
      [Required(message="Genre"), Length(max=40)])

    # Hardcode for now, so this makes roles.display_text kinda pointless
    authors = JsonField("Author(s)")
    illustrators = JsonField("Illustrator(s)")
    editors = JsonField("Editor(s)")
    translators = JsonField("Translator(s)")

    publisher = HiddenField("Publisher",
      [Required(message="Publisher"), Length(max=255)])
    printer = HiddenField("Printer",
      [Length(max=255)])
    # TODO Clarify this in models!!!
    year = HiddenField("Year", [Required(message="Edition Year")])

    def encode(self):
        return u"/".join((self.isbn.data.encode("ascii", "ignore").decode("ascii"), self.title.data.encode("ascii", "ignore").decode("ascii"),
          self.genre.data.encode("ascii", "ignore").decode("ascii"), self.authors.data.encode("ascii", "ignore").decode("ascii"),
          self.illustrators.data.encode("ascii", "ignore").decode("ascii"), self.editors.data.encode("ascii", "ignore").decode("ascii"),
          self.translators.data.encode("ascii", "ignore").decode("ascii"), self.publisher.data.encode("ascii", "ignore").decode("ascii"),
          self.printer.data.encode("ascii", "ignore").decode("ascii"), self.year.data.encode("ascii", "ignore").decode("ascii")))

    def debug_validate(self):
        fields = self.__dict__
        validations = []

        for varname, val in fields.iteritems():
            try:
                validations.insert(0, ": ".join((varname, str(val.validate(self)))))
            except AttributeError:
                pass # it wasn't a form field os meh

        return "/".join(validations) + "/.validate_on_submit():" + str(self.validate_on_submit())
