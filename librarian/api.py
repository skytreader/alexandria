import flask
import json
import pytz

from datetime import datetime

from librarian import app, db
from librarian.forms import AddBooksForm
from flask import Blueprint, request
from flask.ext.login import login_required
from models import get_or_create, Book, BookCompany, BookParticipant, BookPerson, Genre, Role
from sqlalchemy.exc import IntegrityError

import re
import traceback

"""
Convention:
/api/* - large methods, might take some time, usually database transactions (with
lots of writes)
/api/get/* - get a list of objects that are composite of DB tables
/api/list/* - get a list of objects from a single table in the DB.
/api/util/* - for utility functions. These functions are usually generi and can
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


@librarian_api.route("/api/book_adder", methods=["POST"])
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

            #FIXME This part is shaky
            #FIXME I think we should cache.
            author_role = Role.query.filter_by(name="Author").first()
            illus_role = Role.query.filter_by(name="Illustrator").first()
            editor_role = Role.query.filter_by(name="Editor").first()
            trans_role = Role.query.filter_by(name="Translator").first()

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

@librarian_api.route("/api/get/books")
def get_books():
    books = db.session.query(Book).all()
    app.logger.info("Got these books" + str(books))
    return flask.jsonify({})

def __get_first(x):
    return x[0]

@librarian_api.route("/api/list/genres")
def list_genres():
    genres = db.session.query(Genre.name).all()
    genres = map(__get_first, genres)
    app.logger.info("Got these genres" + str(genres))
    return flask.jsonify({"data": genres})

@librarian_api.route("/api/list/companies")
def list_companies():
    companies = db.session.query(BookCompany.name).all()
    companies = map(__get_first, companies)
    return flask.jsonify({"data": companies})

@librarian_api.route("/api/list/persons")
def list_persons():
    persons = db.session.query(BookPerson.lastname, BookPerson.firstname).all()
    persons = map(lambda p: {"lastname": p[1], "firstname": p[0]}, persons)
    return flask.jsonify({"data": persons})
