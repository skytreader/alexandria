"""utf8 all text columns

This is a continuation of 1748bdf1a3b2

Revision ID: dde1998a0981
Revises: 95c528141846
Create Date: 2017-11-30 22:15:16.307012

"""

# revision identifiers, used by Alembic.
revision = 'dde1998a0981'
down_revision = '95c528141846'
branch_labels = None
depends_on = None

import os
import sys

sys.path.append(os.getcwd())

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    See https://stackoverflow.com/questions/34804164/how-to-change-character-encoding-for-column-in-mysql-table
    for reference.
    """
    op.execute("ALTER TABLE librarians CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE genres CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE books CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE book_companies CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE imprints CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE contributors CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE roles CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE book_contributions CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE printers CONVERT TO CHARACTER SET utf8;")
    op.execute("ALTER TABLE pseudonyms CONVERT TO CHARACTER SET utf8;")


def downgrade():
    op.execute("ALTER TABLE librarians CONVERT TO CHARACTER SET latin1")
    op.execute("ALTER TABLE genres CONVERT TO CHARACTER SET latin1;")
    op.execute("ALTER TABLE books CONVERT TO CHARACTER SET latin1;")
    op.execute("ALTER TABLE book_companies CONVERT TO CHARACTER SET latin1;")
    op.execute("ALTER TABLE imprints CONVERT TO CHARACTER SET latin1;")
    op.execute("ALTER TABLE contributors CONVERT TO CHARACTER SET latin1;")
    op.execute("ALTER TABLE roles CONVERT TO CHARACTER SET latin1;")
    op.execute("ALTER TABLE book_contributions CONVERT TO CHARACTER SET latin1;")
    op.execute("ALTER TABLE printers CONVERT TO CHARACTER SET latin1;")
    op.execute("ALTER TABLE pseudonyms CONVERT TO CHARACTER SET latin1;")
