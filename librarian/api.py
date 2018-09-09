# -*- coding: utf-8 -*-
from __future__ import division

from datetime import datetime

from librarian import app, db
from librarian.errors import ConstraintError, InvalidRecordState
from librarian.forms import AddBooksForm, EditBookForm
from librarian.utils import BookRecord, make_equivalent_isbn, has_equivalent_isbn, ISBN_REGEX, NUMERIC_REGEX, Person
from flask import Blueprint, request
from flask_login import login_required
from models import get_or_create, Book, BookCompany, BookContribution, Contributor, Genre, Printer, Role
from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.exc import IntegrityError

import flask
import json
import pytz
import traceback

"""
Contains API endpoints or Python methods (one can be both) useful for other
parts of the app.

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
    Create a Contributor record from the given form_data. Return the created
    records as a list, if any. Else return None.

    form_data is expected to be a JSON list of objects. Each object should have
    the fields `last_name` and `first_name`.

    Raises ConstraintError if one of the persons in form_data has blank firstname
    or lastname.
    """
    from flask_login import current_user
    try:
        parse = json.loads(form_data)
        persons_created = []

        for parson in parse:
            _firstname = parson.get("firstname", "").strip()
            _lastname = parson.get("lastname", "").strip()

            if _firstname and _lastname:
                persons_created.insert(
                    0, get_or_create(
                        Contributor, will_commit=True,
                        firstname=_firstname, lastname=_lastname,
                        creator=current_user
                    )
                )
            else:
                raise ConstraintError(
                    "firstname and lastname are present",
                    str(parson)
                )

        return persons_created
    except ValueError:
        # For errors in pasing JSON
        return []

def __insert_contributions(book, form, session):
    """
    Insert the contributions in the form to the session. No commits will take
    place.
    """
    from flask_login import current_user

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
        if not author.active:
            author.active = True
        session.add(author)
        session.add(author_part)

    for illustrator in illustrators:
        illus_part = BookContribution(book=book, contributor=illustrator,
          role=illus_role, creator=current_user)
        if not illustrator.active:
            illustrator.active = True
        session.add(illustrator)
        session.add(illus_part)

    for editor in editors:
        editor_part = BookContribution(book=book, contributor=editor,
          role=editor_role, creator=current_user)
        if not editor.active:
            editor.active = True
        session.add(editor)
        session.add(editor_part)

    for translator in translators:
        translator_part = BookContribution(book=book, 
          contributor=translator, role=trans_role, creator=current_user)
        if not translator.active:
            translator.active = True
        session.add(translator)
        session.add(translator_part)

@librarian_api.route("/api/add/books", methods=["POST"])
@login_required
def book_adder():
    """
    Assumes that the data has been stripped clean of leading and trailing spaces.

    Possible responses:
        200 Accepted - Book was added to the database successfully.
        302 Error - API endpoint called while not logged in.
        400 Error - The request did not validate. Client _must not_ retry.
        409 IntegrityError - Database error for possible duplicate records.
          Client _must not_ retry.
        500 - Standard server error. Client may retry after some wait period.
    """
    form = AddBooksForm(request.form)
    app.logger.info(str(form))
    app.logger.debug(form.debug_validate())

    if has_equivalent_isbn(form.isbn.data):
        err_str = "A book with that ISBN (in another form) is already in the database."
        app.logger.error(err_str)
        return err_str, 409

    if form.validate_on_submit():
        db.session.execute("SELECT 1")
        try:
            from flask_login import current_user
            # Genre first
            genre = get_or_create(Genre, will_commit=False, name=form.genre.data,
              creator=current_user)

            # Publishing information
            publisher = get_or_create(BookCompany, will_commit=False,
              name=form.publisher.data, creator=current_user)
            has_printer = form.printer.data.strip()
            if has_printer:
                printer = get_or_create(BookCompany, will_commit=False,
                  name=form.printer.data, creator=current_user)

            # Book
            book = Book(isbn=form.isbn.data, title=form.title.data,
              genre=genre, creator=current_user,
              publisher=publisher, publish_year=int(form.year.data))
            db.session.add(book)
            db.session.flush()

            # Create printer entry
            if has_printer:
                printer_record = Printer(company=printer, book=book,
                  creator=current_user)
                db.session.add(printer_record)

            __insert_contributions(book, form, db.session)

            db.session.commit()

            return "Accepted", 200
        except IntegrityError, ierr:
            db.session.rollback()
            app.logger.error(traceback.format_exc())
            err_str = '"%s" has been catalogued before. Ignoring.' % (form.title.data)
            return err_str, 409
        except ConstraintError, cerr:
            db.session.rollback()
            app.logger.error(traceback.format_exc())
            return cerr.message, 400
        db.session.execute("select 2")
    
    err_str = "Did not validate for %s. Please re-enter book to try again." % (form.title.data)
    return err_str, 400

@librarian_api.route("/api/edit/books", methods=["POST"])
@login_required
def edit_book():
    def contribution_exists(all_contribs, role_id, person):
        """
        Check if the given person contributed for the given role in all the
        contributions related to the present book being edited.

        Where
        
        `all_contribs` is all the BookContribution records for the book being
        edited.

        person is an instance of librarian.utils.Person.

        Returns the BookContribution object if it exists, else False.
        """
        the_contribution = [
            contrib for contrib in all_contribs if (
                contrib.role_id == role_id and
                contrib.contributor.firstname == person.firstname and
                contrib.contributor.lastname == person.lastname
            )]

        if len(the_contribution) > 1:
            raise InvalidRecordState("uniqueness of contribution role + person + book %s" % spam)

        if the_contribution:
           return the_contribution[0]
        else:
           return False

    def edit_contrib(book, all_contribs, role, submitted_persons):
        """
        Adds all new contributors to the session and deletes all removed
        contributors to the session.

        Where `submitted_persons` is the data straight out of the form (hence it
        is a JSON string), `all_contribs` are all the active contributions in
        the book as recorded in the DB (pre-edit).
        """
        app.logger.debug("considering role %s" % role)
        parsons = json.loads(submitted_persons)
        form_records = set()

        # Create or load all the contributions mentioned in the form.
        for p in parsons:
            ce = contribution_exists(all_contribs, role.id, Person(**p))
            if ce is not False:
                form_records.add(ce)
            else:
                contributor_record = get_or_create(
                    Contributor, will_commit=False, firstname=p["firstname"],
                    lastname=p["lastname"], creator=current_user
                )
                app.logger.debug("got contributor record %s" % contributor_record)
                app.logger.debug("will attach role %s" % role)

                if not contributor_record.active:
                    contributor_record.active = True

                contribution = BookContribution(
                    book=book, contributor=contributor_record, role=role,
                    creator=current_user
                )
                db.session.add(contribution)
                form_records.add(contribution)

        recorded_contribs = set([
            contrib for contrib in all_contribs
            if contrib.role.id == role.id
        ])

        app.logger.debug("recorded contribs for %s %s" % (role, recorded_contribs))
        app.logger.debug("form records %s" % form_records)
        deletables = recorded_contribs - form_records
        app.logger.debug("The deletables %s" % deletables)

        for d in deletables:
            d.active = False

            other_contrib = (
                BookContribution.query
                .filter(BookContribution.contributor_id == d.contributor_id)
                .filter(
                    or_(
                        BookContribution.book_id != book.id,
                        BookContribution.role_id != d.role_id
                    )
                )
                .filter(BookContribution.active)
                .first()
            )
            app.logger.debug(
                "Contributor %s has another contribution %s (checked from %s)" %
                (d.contributor_id, other_contrib, role.name)
            )

            if other_contrib is None:
                app.logger.debug("Deactivating %s" % d)
                d.contributor.active = False

    from flask_login import current_user

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
                .filter(BookContribution.active)
                .filter(BookContribution.contributor_id == Contributor.id)
                .filter(Contributor.active)
                .all()
            )

            edit_contrib(book, all_contribs, Role.get_preset_role("Author"),
              form.authors.data)
            r_illustrator = Role.get_preset_role("Illustrator")
            edit_contrib(book, all_contribs, r_illustrator,
              form.illustrators.data)
            edit_contrib(book, all_contribs, Role.get_preset_role("Editor"),
              form.editors.data)
            edit_contrib(book, all_contribs, Role.get_preset_role("Translator"),
              form.translators.data)

            db.session.commit()
            return "Accepted", 200
        except IntegrityError, ierr:
            db.session.rollback()
            app.logger.error("Integrity Error occurred")
            app.logger.exception(traceback.format_exc())
            return "IntegrityError", 409
        except Exception as ex:
            db.session.rollback()
            app.logger.error("error except. traceback follows:")
            import traceback
            traceback.print_exc()
            return "Unknown error", 500
    else:
        db.session.rollback()
        app.logger.error("Form does not validate.")
        return "Unknown error", 500

@librarian_api.route("/api/util/servertime")
def servertime():
    return flask.jsonify({"now": str(datetime.now(tz=pytz.utc).isoformat())})

@librarian_api.route("/api/read/books")
def get_books():
    """
    Get a listing of books in the database.

    Request parameters:
        offset - Integer. The "page number" used for pagination. Default 0.
        limit - Integer. The number of records to return. Default 8.
        order - String, either "desc" or "asc". The order in which to return
        records. Sorting is always alphabetical by the title of the book.
        Default "asc".

    Possible responses:
        200 - Will have accompanying JSON data of the books.
        400 - Parameters not as expected. An accompanying error message will
        specify the unexpected parameters.
        500 - Standard server error.
    """
    offset = "0"
    limit = "8"

    try:
        offset = int(request.args.get("offset", "0"))
        limit = int(request.args.get("limit", "8"))
    except ValueError:
        return (
            "offset and limit must be integers, given (offset: %s, limit: %s)" % (offset, limit),
            400
        )

    order = request.args.get("order", "asc")

    if order not in ("desc", "asc"):
        return "order can only be either 'desc' or 'asc', given %s" % order, 400

    bookq = db.session.query(Book)

    if order == "desc":
        bookq = bookq.order_by(desc("title"))
    elif order == "asc":
        bookq = bookq.order_by(asc("title"))

    bookq = bookq.limit(limit).offset(offset)
        
    books = bookq.all()
    book_listing = [BookRecord.get_bookrecord(book.id) for book in books]
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
    """
    Return the active Contributors in the database. The endpoint might be a bit
    misleading since we are filtering here. But meh, this is only used for the
    autocomplete suggestions.
    """
    persons = (
        db.session.query(Contributor.lastname, Contributor.firstname)
        .filter(Contributor.active).all()
    )
    persons = [{"lastname": p[0], "firstname": p[1]} for p in persons]
    return flask.jsonify({"data": persons})

def get_top_contributors(contrib_type, limit=4):
    top = (db.session.query(Contributor.id, Contributor.lastname,
      Contributor.firstname,
      func.count(BookContribution.book_id).label("contrib_count"))
      .filter(Contributor.id==BookContribution.contributor_id)
      .filter(BookContribution.role_id==Role.id)
      .filter(Role.name==contrib_type)
      .filter(Contributor.active)
      .filter(BookContribution.active)
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
      .filter(Contributor.active)
      .filter(BookContribution.active)
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
    contributors = len(db.session.query(BookContribution).filter(BookContribution.active).all())
    top_author = get_top_contributors("Author", 1)
    stats["participants_per_book"] = (contributors / books) if books else 0
    stats["recent_books"] = get_recent_books()
    stats["book_count"] = books
    stats["top_author"] = top_author[0] if top_author else None
    return flask.jsonify(stats)

# FIXME Slow as f*ck.
def search(searchq):
    # Will only fail if some f*cker names their book after their own ISBN.
    results = BookRecord.base_assembler_query()
    if ISBN_REGEX.match(searchq):
        alt_isbn = make_equivalent_isbn(searchq)
        results = results.filter(
            or_(
                Book.isbn == searchq,
                Book.isbn == alt_isbn
            )
        ).all()
    else:
        contrib_query = (
            db.session.query(Book.id)
            .filter(BookContribution.book_id == Book.id)
            .filter(BookContribution.contributor_id == Contributor.id)
            .filter(
                func.concat(
                    Contributor.firstname, ' ', Contributor.lastname
                ).ilike("".join(("%", searchq, "%")))
            ).all()
        )
        contribooks = [bid for bid, in contrib_query]
        results = (
            BookRecord.base_assembler_query()
            .filter(
                or_(
                    Book.title.ilike("".join(("%", searchq, "%"))),
                    and_(
                        Book.publisher_id == BookCompany.id,
                        BookCompany.name.ilike("".join(("%", searchq, "%")))
                    ),
                    Book.id.in_(contribooks) if contribooks else False
                )
            ).all()
        )

    book_listing = BookRecord.assembler(results, as_obj=False)

    return book_listing
