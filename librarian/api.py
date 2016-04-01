# -*- coding: utf-8 -*-
from datetime import datetime

from librarian import app, db
from librarian.forms import AddBooksForm
from librarian.utils import NUMERIC_REGEX
from flask import Blueprint, request
from flask.ext.login import login_required
from models import get_or_create, Book, BookCompany, BookParticipant, BookPerson, Genre, Role
from sqlalchemy.exc import IntegrityError

import config
import flask
import json
import pytz
import re
import traceback

"""
Convention:
/api/add/* - add some records to the database
/api/read/* - get data from backend
/api/util/* - for utility functions. These functions are usually generic and can
find use in any project.
"""

librarian_api = Blueprint("librarian_api", __name__)

def __create_bookperson(form_data):
    """
    Create a bookperson record from the given form_data. Return the created
    records as a list, if any. Else return None.

    form_data is expected to be a JSON list of objects. Each object should have
    the fields `last_name` and `first_name`.
    """
    from flask.ext.login import current_user
    try:
        parse = json.loads(form_data)
        persons_created = []

        for parson in parse:
            persons_created.insert(0, get_or_create(BookPerson, will_commit=True,
              firstname=parson["firstname"], lastname=parson["lastname"],
              creator=current_user.get_id()))

        return persons_created
    except ValueError:
        # For errors in pasing JSON
        return None


@librarian_api.route("/api/add/books", methods=["POST"])
@login_required
def book_adder():
    """
    Assumes that the data has been stripped clean of leading and trailing spaces.

    Possible responses:
        200 Accepted - Book was added to the database successfully.
        400 Error - The request did not validate. Client _must not_ retry.
        409 IntegrityError - Database error for possible duplicate records.
          Client _must not_ retry.
        500 - Standard server error. Client may retry after some wait period.
    """
    form = AddBooksForm(request.form)
    app.logger.info(str(form))
    app.logger.debug(form.debug_validate())

    if form.validate_on_submit():
        try:
            from flask.ext.login import current_user
            # Genre first
            genre = get_or_create(Genre, will_commit=True, name=form.genre.data,
              creator=current_user.get_id())

            # Publishing information
            publisher = get_or_create(BookCompany, will_commit=True,
              name=form.publisher.data, creator=current_user.get_id())
            printer = get_or_create(BookCompany, will_commit=True,
              name=form.printer.data, creator=current_user.get_id())

            # Book
            book = Book(isbn=form.isbn.data, title=form.title.data,
              genre=genre.id, creator=current_user.get_id(),
              publisher=publisher.id, printer=printer.id,
              publish_year=int(form.year.data))
            db.session.add(book)

            # Create the BookPersons
            authors = __create_bookperson(form.authors.data)
            illustrators = __create_bookperson(form.illustrators.data)
            editors = __create_bookperson(form.editors.data)
            translators = __create_bookperson(form.translators.data)

            author_role = Role.get_preset_role("Author")
            illus_role = Role.get_preset_role("Illustrator")
            editor_role = Role.get_preset_role("Editor")
            trans_role = Role.get_preset_role("Translator")

            # Assign participation
            for author in authors:
                author_part = BookParticipant(book_id=book.id,
                  person_id=author.id, role_id=author_role.id,
                  creator=current_user.get_id())
                db.session.add(author)
                db.session.add(author_part)

            for illustrator in illustrators:
                illus_part = BookParticipant(book_id=book.id,
                  person_id=illustrator.id, role_id=illus_role.id,
                  creator=current_user.get_id())
                db.session.add(illus_part)

            for editor in editors:
                editor_part = BookParticipant(book_id=book.id,
                  person_id=editor.id, role_id=editor_role.id,
                  creator=current_user.get_id())
                db.session.add(editor_part)

            for translator in translators:
                translator_part = BookParticipant(book_id=book.id,
                  person_id=translator.id, role_id=trans_role.id,
                  creator=current_user.get_id())
                db.session.add(translator_part)

            db.session.commit()

            return "Accepted", 200
        except IntegrityError, ierr:
            print traceback.format_exc()
            return "IntegrityError", 409
    
    return "Error", 400

@librarian_api.route("/api/util/servertime")
def servertime():
    return flask.jsonify({"now": str(datetime.now(tz=pytz.utc).isoformat())})

@librarian_api.route("/api/read/books")
def get_books():
    """
    Get a listing of books in the database.

    Specifying any one of the paramets `offset`, `limit`, or `order` will
    automatically trigger defaults for the other parameters if they are not
    specified. The defaults are as follows:

    offset = 0
    limit = 8

    NOTE: If none of them is present, this will query ALL records.

    Request parameters:
        offset - Integer. The "page number" used for pagination.
        limit - Integer. The number of records to return.

    Possible responses:
        200 - Will have accompanying JSON data of the books.
        400 - Parameters not as expected.
        500 - Standard server error.
    """
    def subq_generator(role):
        return (db.session.query(Book.id, BookPerson.lastname, BookPerson.firstname)
          .filter(BookPerson.id == BookParticipant.person_id)
          .filter(BookParticipant.role_id == Role.id)
          .filter(Role.name == role)
          .filter(Book.id == BookParticipant.book_id)
          .subqery())

    offset = request.args.get("offset")
    limit = request.args.get("limit")

    if offset and not limit:
        limit = "8"
    elif limit and not offset:
        offset = "0"

    bookq = (db.session.query(Book.isbn, Book.title, BookPerson.lastname,
      BookPerson.firstname, Role.name, Book.publisher.name).filter(Book.id == BookParticipant.book_id)
      .filter(BookParticipant.person_id == BookPerson.id)
      .filter(BookParticipant.role_id == Role.id))

    if offset and limit and NUMERIC_REGEX.match(offset) and NUMERIC_REGEX.match(limit):
        bookq = bookq.limit(limit).offset(offset)
    elif offset and limit:
        return "Error", 400
        
    books = bookq.all()
    app.logger.debug("Got these books" + str(books))
    structured_catalog = {}
    
    for book in books:
        record_exists = structured_catalog.get(book[0])
        role = book[4].lower()

        if record_exists:
            if structured_catalog[book[0]].get(role):
                structured_catalog[book[0]][role].append({"lastname": book[2],
                  "firstname": book[3]})
            else:
                structured_catalog[book[0]][role] = [{"lastname": book[2],
                  "firstname": book[3]}]
        else:
            fmt = {"title": book[1],
              role: [{"lastname": book[2], "firstname": book[3]}],
              "publisher": book[5]}

            structured_catalog[book[0]] = fmt

    return flask.jsonify(structured_catalog)

def __get_first(x):
    return x[0]

@librarian_api.route("/api/read/genres")
def list_genres():
    genres = db.session.query(Genre.name).all()
    genres = [g for g, in genres]
    app.logger.debug("Got these genres" + str(genres))
    return flask.jsonify({"data": genres})

@librarian_api.route("/api/read/companies")
def list_companies():
    companies = db.session.query(BookCompany.name).all()
    companies = [c for c, in companies]
    return flask.jsonify({"data": companies})

@librarian_api.route("/api/read/persons")
def list_persons():
    persons = db.session.query(BookPerson.lastname, BookPerson.firstname).all()
    persons = map(lambda p: {"lastname": p[0], "firstname": p[1]}, persons)
    return flask.jsonify({"data": persons})
