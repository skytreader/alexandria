"""add comments field for books

Revision ID: 703b37f58578
Revises: 4f88e34f90c6
Create Date: 2016-11-04 00:47:11.125083

"""

# revision identifiers, used by Alembic.
revision = '703b37f58578'
down_revision = '4f88e34f90c6'
branch_labels = None
depends_on = None

import os
import sys

sys.path.append(os.getcwd())

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
