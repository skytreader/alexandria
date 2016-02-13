"""add cache table

Revision ID: 39ccc5d35a4d
Revises: 1ac819f296cc
Create Date: 2016-02-14 04:35:39.345094

The purpose of the cache table is to have a single table aggregating all the
default data we want to show when listing all books. All FKs so there should
be no problems with stale data.

This also adds the 'is_preset' column to the roles table.
"""

# revision identifiers, used by Alembic.
revision = '39ccc5d35a4d'
down_revision = '1ac819f296cc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("roles",
      sa.Column("is_preset", sa.Boolean(), server_default=False)
    )


def downgrade():
    op.drop_column("roles", "is_preset")
