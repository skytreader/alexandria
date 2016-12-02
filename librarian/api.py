# -*- coding: utf-8 -*-
from __future__ import division

from datetime import datetime

from librarian import app, db
from librarian.forms import AddBooksForm, EditBookForm
from librarian.utils import BookRecord, NUMERIC_REGEX
from flask import Blueprint, request
from flask.ext.login import login_required
from models import get_or_create, Book, BookCompany, BookContribution, Contributor, Genre, Printer, Role
from sqlalchemy import desc, func
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
/api/edit/* - edit data in the database
/api/util/* - for utility functions. Functions that are usually and can find use
in any project may go here but this namespace can also house project-specific
utilities.
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
            persons_created.insert(0, get_or_create(Contributor, will_commit=True,
              firstname=parson["firstname"], lastname=parson["lastname"],
              creator=current_user))

        return persons_created
    except ValueError:
        # For errors in pasing JSON
        return []

def __insert_contributions(book, form, session):
    """
    Insert the contributions in the form to the session. No commits will take
    place.
    """
    from flask.ext.login import current_user

    # Create the Contributors
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
        author_part = BookContribution(book=book, contributor=author,
          role=author_role, creator=current_user)
        session.add(author)
        session.add(author_part)

    for illustrator in illustrators:
        illus_part = BookContribution(book=book, contributor=illustrator,
          role=illus_role, creator=current_user)
        session.add(illustrator)
        session.add(illus_part)

    for editor in editors:
        editor_part = BookContribution(book=book, contributor=editor,
          role=editor_role, creator=current_user)
        session.add(editor)
        session.add(editor_part)

    for translator in translators:
        translator_part = BookContribution(book=book, 
          contributor=translator, role=trans_role, creator=current_user)
        session.add(translator)
        session.add(translator_part)

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
              creator=current_user)

            # Publishing information
            publisher = get_or_create(BookCompany, will_commit=True,
              name=form.publisher.data, creator=current_user)
            printer = get_or_create(BookCompany, will_commit=True,
              name=form.printer.data, creator=current_user)

            # Book
            book = Book(isbn=form.isbn.data, title=form.title.data,
              genre=genre, creator=current_user,
              publisher=publisher, publish_year=int(form.year.data))
            db.session.add(book)
            db.session.flush()

            # Create printer entry
            printer_record = Printer(company=printer, book=book,
              creator=current_user)
            db.session.add(printer_record)

            __insert_contributions(book, form, db.session)

            db.session.commit()

            return "Accepted", 200
        except IntegrityError, ierr:
            app.logger.error(traceback.format_exc())
            err_str = '"%s" has been catalogued before. Ignoring.' % (form.title.data)
            return err_str, 409
    
    err_str = "Did not validate for %s. Please re-enter book to try again." % (form.title.data)
    return err_str, 400

@librarian_api.route("/api/edit/books", methods=["POST"])
@login_required
def edit_book():
    def contribution_exists(all_contribs, role_id, person_id):
        return [
            contrib for contrib in all_contribs if (
                contrib.role_id == role_if and contrib.person_id == person_id
            )]

    def edit_contrib(role_id, submitted_roles):
        pass

    from flask.ext.login import current_user

    form = EditBookForm(request.form)
    app.logger.info(str(form))
    app.logger.debug(form.debug_validate())

    if form.validate_on_submit():
        book_id = int(form.book_id.data)
        try:
            # Update records in books table
            genre = get_or_create(Genre, will_commit=False, session=db.session,
             name=form.genre.data, creator=current_user)
            publisher = get_or_create(BookCompany, will_commit=False, 
              name=form.publisher.data, creator=current_user)
            book = db.session.query(Book).filter(Book.id==book_id).first()
            book.isbn = form.isbn.data
            book.title = form.title.data
            book.publish_year = form.year.data
            book.genre_id = genre.id
            book.publisher_id = publisher.id

            # Get all the contributions for this book
            all_contribs = (
                BookContribution.query
                .filter(BookContribution.book_id == book_id)
                .all()
            )

            # Delete the book_contributions involved
            BookContribution.query.filter(BookContribution.book_id == book_id).delete()

            db.session.commit()
            return "Accepted", 200
        except IntegrityError, ierr:
            app.logger.exception(traceback.format_exc())
            return "IntegrityError", 409
        except Exception as ex:
            import traceback
            traceback.print_exc()
            app.logger.error("error except")
            return "Unknown error", 500
    else:
        app.logger.error("error else")
        return "Unknown error", 500

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
        return (db.session.query(Book.id, Contributor.lastname, Contributor.firstname)
          .filter(Contributor.id == BookContribution.contributor_id)
          .filter(BookContribution.role_id == Role.id)
          .filter(Role.name == role)
          .filter(Book.id == BookContribution.book_id)
          .subqery())

    offset = request.args.get("offset")
    limit = request.args.get("limit")

    if offset and not limit:
        limit = "8"
    elif limit and not offset:
        offset = "0"

    bookq = BookRecord.base_assembler_query()

    if offset and limit and NUMERIC_REGEX.match(offset) and NUMERIC_REGEX.match(limit):
        bookq = bookq.limit(limit).offset(offset)
    elif offset and limit:
        return "Error", 400
        
    books = bookq.all()
    book_listing = BookRecord.assembler(books, as_obj=False)
    app.logger.debug("Got these books" + str(books))
    return flask.jsonify({"data": book_listing})

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
    persons = db.session.query(Contributor.lastname, Contributor.firstname).all()
    persons = map(lambda p: {"lastname": p[0], "firstname": p[1]}, persons)
    return flask.jsonify({"data": persons})

def get_top_contributors(contrib_type, limit=4):
    top = (db.session.query(Contributor.id, Contributor.lastname,
      Contributor.firstname,
      func.count(BookContribution.book_id).label("contrib_count"))
      .filter(Contributor.id==BookContribution.contributor_id)
      .filter(BookContribution.role_id==Role.id)
      .filter(Role.name==contrib_type)
      .order_by(desc("contrib_count"))
      .group_by(Contributor.id).order_by("contrib_count").limit(limit)
      .all())

    return top

def get_recent_contributors(contrib_type, limit=4):
    top = (db.session.query(Contributor.id, Contributor.lastname,
      Contributor.firstname, BookContribution.created_at)
      .filter(Contributor.id==BookContribution.contributor_id)
      .filter(BookContribution.role_id==Role.id)
      .filter(Role.name==contrib_type)
      .order_by(desc(BookParticipant.date_created)).limit(limit).all())
    
    return top

def get_recent_books(limit=4):
    """
    Returns a list of size `limit` containing the title of the most recently
    added books.
    """
    top = db.session.query(Book.title).order_by(desc(Book.date_created)).limit(limit).all()

    return [title for title, in top]

@librarian_api.route("/api/util/stats")
def quick_stats():
    stats = {}
    books = len(db.session.query(Book).all())
    contributors = len(db.session.query(BookContribution).all())
    top_author = get_top_contributors("Author", 1)
    stats["participants_per_book"] = (contributors / books)
    stats["recent_books"] = get_recent_books()
    stats["book_count"] = books
    stats["top_author"] = top_author[0]
    return flask.jsonify(stats)

def search(searchq):
    results = (
      BookRecord.base_assembler_query()
      .filter(Book.title.like("".join(("%", searchq, "%"))))
      .all())

    book_listing = BookRecord.assembler(results, as_obj=False)

    return book_listing
