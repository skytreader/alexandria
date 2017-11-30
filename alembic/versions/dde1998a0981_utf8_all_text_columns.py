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
    pass


def downgrade():
    pass
