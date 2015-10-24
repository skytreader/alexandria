"""easier select all books

Revision ID: f6b58ebc805
Revises: 
Create Date: 2015-10-24 04:49:45.939450

"""

# revision identifiers, used by Alembic.
revision = 'f6b58ebc805'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy import Metadata, Table
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "printers",
        sa.Column("company_id", sa.Integer, sa.primary_key = True, sa.ForeignKey("book_companies.id")),
        sa.Column("book_id", sa.Integer, sa.primary_key = True, sa.ForeignKey("books.id"))
        sa.Column("creator", sa.Integer, sa.ForeignKey("librarians.id")),
        sa.Column("last_modifier", sa.Integer, sa.ForeignKey("librarians.id"))
        sa.Column("date_created", sa.DateTime, default=sa.func.current_timestamp())
        sa.Column("date_modified", sa.DateTime, default=sa.func.current_timestamp(),
          onupdate=sa.func.current_timestamp())
    )

    conn = op.get_bind()
    meta = MetaData(bind=conn)

def downgrade():
    op.drop_table("printers")
