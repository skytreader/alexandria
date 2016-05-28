# -*- coding: utf-8 -*-

from librarian.utils import Person

"""
Contains plain object definitions for use in testing purposes.
"""


class LibraryEntry(object):
    """
    Object with the following fields:

      - isbn
      - title
      - author*: list of dictionaries with `lastname` and `firstname` fields.
      - illustrator*: list of dictionaries with `lastname` and `firstname` fields.
      - editor*: list of dictionaries with `lastname` and `firstname` fields.
      - translator*: list of dictionaries with `lastname` and `firstname` fields.
      - publisher

    * May contain `None` if applicable.
    """
    
    def __init__(self, isbn=None, title=None, author=None, illustrator=None,
      editor=None, translator=None, publisher=None):
        self.isbn = isbn
        self.title = title
        self.author = self.__unpack_persons(author)
        self.illustrator = self.__unpack_persons(illustrator)
        self.editor = self.__unpack_persons(editor)
        self.translator = self.__unpack_persons(translator)
        self.publisher = publisher

    def __unpack_persons(self, person_list):
        if person_list:
            return frozenset([Person(**p) for p in person_list])
        else:
            return None

    def __eq__(self, le):
        return (self.isbn == le.isbn and self.title == le.title and
          self.author == le.author and self.illustrator == le.illustrator and
          self.editor == le.editor and self.translator == le.translator and
          self.publisher == le.publisher)

    def __hash__(self):
        return hash((self.isbn, self.title, self.author, self.illustrator,
          self.translator, self.publisher))

    def __str__(self):
        return str({"isbn": self.isbn, "title": self.title, "author": str(self.author),
          "illustrator": str(self.illustrator), "editor": str(self.editor),
          "translator": str(self.translator), "publisher": str(self.publisher)})
