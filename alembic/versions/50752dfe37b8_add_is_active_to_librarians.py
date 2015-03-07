"""add is_active to librarians

Revision ID: 50752dfe37b8
Revises: 
Create Date: 2015-03-05 19:37:35.157829

"""

# revision identifiers, used by Alembic.
revision = '50752dfe37b8'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy import MetaData, Table
import sqlalchemy as sa


def upgrade():
    op.add_column("librarians", sa.Column("is_active", sa.Boolean, nullable=False, default=True))

    conn = op.get_bind()
    meta = MetaData(bind=conn)


def downgrade():
    pass
