"""change default to server_default

Revision ID: 1ac819f296cc
Revises: 1748bdf1a3b2
Create Date: 2016-02-14 04:55:22.623704

"""

# revision identifiers, used by Alembic.
revision = '1ac819f296cc'
down_revision = '1748bdf1a3b2'
branch_labels = None
depends_on = None

import os
import sys

sys.path.append(os.getcwd())

from alembic import op
from librarian import db
from librarian.models import ISBN_START
import sqlalchemy as sa


def upgrade():
    op.alter_column("librarians", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("librarians", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("librarians", "can_read", server_default=db.false())
    op.alter_column("librarians", "can_write", server_default=db.false())
    op.alter_column("librarians", "can_exec", server_default=db.false())
    op.alter_column("librarians", "is_user_active", server_default=db.false())

    op.alter_column("genres", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("genres", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())

    op.alter_column("books", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("books", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("books", "publish_year", server_default=str(ISBN_START))

    op.alter_column("book_companies", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("book_companies", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())

    op.alter_column("imprints", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("imprints", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())

    op.alter_column("book_persons", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("book_persons", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())

    op.alter_column("roles", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("roles", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())

    op.alter_column("book_participants", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("book_participants", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())

    op.alter_column("printers", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("printers", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())

    op.alter_column("pseudonyms", "date_created", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())
    op.alter_column("pseudonyms", "date_modified", type_=db.DateTime(True),
      server_default=sa.func.current_timestamp())


def downgrade():
    op.alter_column("librarians", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("librarians", "date_modified", type_=db.DateTime,
      server_default=None)
    op.alter_column("librarians", "can_read", server_default=None)
    op.alter_column("librarians", "can_write", server_default=None)
    op.alter_column("librarians", "can_exec", server_default=None)
    op.alter_column("librarians", "is_user_active", server_default=None)

    op.alter_column("genres", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("genres", "date_modified", type_=db.DateTime,
      server_default=None)

    op.alter_column("books", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("books", "date_modified", type_=db.DateTime,
      server_default=None)

    op.alter_column("book_companies", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("book_companies", "date_modified", type_=db.DateTime,
      server_default=None)

    op.alter_column("imprints", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("imprints", "date_modified", type_=db.DateTime,
      server_default=None)

    op.alter_column("book_persons", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("book_persons", "date_modified", type_=db.DateTime,
      server_default=None)

    op.alter_column("roles", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("roles", "date_modified", type_=db.DateTime,
      server_default=None)

    op.alter_column("book_participants", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("book_participants", "date_modified", type_=db.DateTime,
      server_default=None)

    op.alter_column("printers", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("printers", "date_modified", type_=db.DateTime,
      server_default=None)

    op.alter_column("pseudonyms", "date_created", type_=db.DateTime,
      server_default=None)
    op.alter_column("pseudonyms", "date_modified", type_=db.DateTime,
      server_default=None)
