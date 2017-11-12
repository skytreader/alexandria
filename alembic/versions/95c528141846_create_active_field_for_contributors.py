"""create active field for contributors

Revision ID: 95c528141846
Revises: 09a48c35766b
Create Date: 2017-11-13 00:56:40.854453

"""

# revision identifiers, used by Alembic.
revision = '95c528141846'
down_revision = '09a48c35766b'
branch_labels = None
depends_on = None

import os
import sys

sys.path.append(os.getcwd())

from alembic import op
from librarian import db
import sqlalchemy as sa


def upgrade():
    op.add_column("contributors", sa.Column("active", sa.Boolean, nullable=False, default=True, server_default=db.false()))
    op.add_column("book_contributions", sa.Column("active", sa.Boolean, nullable=False, default=True, server_default=db.false()))


def downgrade():
    op.drop_column("contributors", "active")
    op.drop_column("book_contributions", "active")
