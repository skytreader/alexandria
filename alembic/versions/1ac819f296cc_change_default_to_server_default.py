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

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("librarians", "date_created",
      server_default=None)
    op.alter_column("librarians", "date_modified",
      server_default=None)

    op.alter_column("genres", "date_created",
      server_default=None)
    op.alter_column("genres", "date_modified",
      server_default=None)

    op.alter_column("books", "date_created",
      server_default=None)
    op.alter_column("books", "date_modified",
      server_default=None)

    op.alter_column("book_companies", "date_created",
      server_default=None)
    op.alter_column("book_companies", "date_modified",
      server_default=None)

    op.alter_column("imprints", "date_created",
      server_default=None)
    op.alter_column("imprints", "date_modified",
      server_default=None)

    op.alter_column("book_persons", "date_created",
      server_default=None)
    op.alter_column("book_persons", "date_modified",
      server_default=None)

    op.alter_column("roles", "date_created",
      server_default=None)
    op.alter_column("roles", "date_modified",
      server_default=None)

    op.alter_column("book_participants", "date_created",
      server_default=None)
    op.alter_column("book_participants", "date_modified",
      server_default=None)

    op.alter_column("printers", "date_created",
      server_default=None)
    op.alter_column("printers", "date_modified",
      server_default=None)

    op.alter_column("pseudonyms", "date_created",
      server_default=None)
    op.alter_column("pseudonyms", "date_modified",
      server_default=None)


def downgrade():
    op.alter_column("librarians", "date_created",
      server_default=None)
    op.alter_column("librarians", "date_modified",
      server_default=None)

    op.alter_column("genres", "date_created",
      server_default=None)
    op.alter_column("genres", "date_modified",
      server_default=None)

    op.alter_column("books", "date_created",
      server_default=None)
    op.alter_column("books", "date_modified",
      server_default=None)

    op.alter_column("book_companies", "date_created",
      server_default=None)
    op.alter_column("book_companies", "date_modified",
      server_default=None)

    op.alter_column("imprints", "date_created",
      server_default=None)
    op.alter_column("imprints", "date_modified",
      server_default=None)

    op.alter_column("book_persons", "date_created",
      server_default=None)
    op.alter_column("book_persons", "date_modified",
      server_default=None)

    op.alter_column("roles", "date_created",
      server_default=None)
    op.alter_column("roles", "date_modified",
      server_default=None)

    op.alter_column("book_participants", "date_created",
      server_default=None)
    op.alter_column("book_participants", "date_modified",
      server_default=None)

    op.alter_column("printers", "date_created",
      server_default=None)
    op.alter_column("printers", "date_modified",
      server_default=None)

    op.alter_column("pseudonyms", "date_created",
      server_default=None)
    op.alter_column("pseudonyms", "date_modified",
      server_default=None)
