# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm as Form
from librarian.custom.forms import JsonField
from wtforms import HiddenField, PasswordField, TextField
from wtforms.validators import Length, Required

import json

class SearchForm(Form):
    q = TextField("Search for", [Required(message="What are you looking for?")])

class LoginForm(Form):
    librarian_username = TextField("Username",
      [Required(message="Enter your username"), Length(max=50)])
    librarian_password = PasswordField("Password", [Required(message="Enter your password")])

    def __str__(self):
        return "username: %s/password: %s" % (self.librarian_username.data, self.librarian_password.data)

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

    def __str__(self):
        return json.dumps({
            "isbn": self.isbn.data.encode("ascii", "ignore").decode("ascii"),
            "title": self.title.data.encode("ascii", "ignore").decode("ascii"),
            "genre": self.genre.data.encode("ascii", "ignore").decode("ascii"),
            "authors": self.authors.data.encode("ascii", "ignore").decode("ascii"),
            "illustrators": self.illustrators.data.encode("ascii", "ignore").decode("ascii"),
            "editors": self.editors.data.encode("ascii", "ignore").decode("ascii"),
            "translators": self.translators.data.encode("ascii", "ignore").decode("ascii"),
            "publisher": self.publisher.data.encode("ascii", "ignore").decode("ascii"),
            "printer": self.printer.data.encode("ascii", "ignore").decode("ascii"),
            "year": self.year.data.encode("ascii", "ignore").decode("ascii")
        })

    def debug_validate(self):
        fields = self.__dict__
        validations = []

        for varname, val in fields.iteritems():
            try:
                validations.insert(0, ": ".join((varname, str(val.validate(self)))))
            except AttributeError:
                pass # it wasn't a form field os meh

        return "/".join(validations) + "/.validate_on_submit():" + str(self.validate_on_submit())

class EditBookForm(AddBooksForm):
    book_id = HiddenField("bookid", [Required(message="book id")])
