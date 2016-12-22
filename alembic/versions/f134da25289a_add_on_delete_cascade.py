"""add on delete cascade

Revision ID: f134da25289a
Revises: 703b37f58578
Create Date: 2016-12-23 05:17:54.558900

"""

# revision identifiers, used by Alembic.
revision = 'f134da25289a'
down_revision = '703b37f58578'
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
