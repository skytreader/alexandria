# -*- coding: utf-8 -*-

"""
Contains plain object definitions for use in testing purposes.
"""

class Person(object):
    def __init__(self, lastname, firstname):
        self.lastname = lastname
        self.firstname = firstname

    def __eq__(self, p):
        return p.lastname == self.lastname and p.firstname == self.firstname

    def __hash__(self):
        return hash((self.lastname, self.firstname))
    
    def __str__(self):
        return self.lastname + ", " + self.firstname

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