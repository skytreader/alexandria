"""use utf8

Revision ID: 1748bdf1a3b2
Revises: f6b58ebc805
Create Date: 2016-01-10 05:05:46.523320

"""

# revision identifiers, used by Alembic.
revision = '1748bdf1a3b2'
down_revision = 'f6b58ebc805'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("ALTER TABLE librarians DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE roles DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE genres DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE books DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE book_companies DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE imprints DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE book_persons DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE book_participants DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE printers DEFAULT CHARACTER SET utf8")
    op.execute("ALTER TABLE pseudonyms DEFAULT CHARACTER SET utf8")


def downgrade():
    op.execute("ALTER TABLE librarians DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE roles DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE genres DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE books DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE book_companies DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE imprints DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE book_persons DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE book_participants DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE printers DEFAULT CHARACTER SET latin1")
    op.execute("ALTER TABLE pseudonyms DEFAULT CHARACTER SET latin1")
