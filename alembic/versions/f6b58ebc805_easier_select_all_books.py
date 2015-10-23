"""easier select all books

Revision ID: f6b58ebc805
Revises: 50752dfe37b8
Create Date: 2015-10-24 04:49:45.939450

"""

# revision identifiers, used by Alembic.
revision = 'f6b58ebc805'
down_revision = '50752dfe37b8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "printers",
        sa.Column("company_id", sa.Integer, sa.primary_key = True, sa.ForeignKey("book_companies.id")),
        sa.Column("book_id", sa.Integer, sa.primary_key = True, sa.ForeignKey("books.id"),
        sa.Column("creator", sa.Integer, sa.ForeignKey("librarians.id")),
        sa.Column("last_modifier", sa.Integer, sa.ForeignKey("librarians.id"))
        sa.Column("date_created", sa.DateTime, default=sa.func.current_timestamp())
        sa.Column("date_modified", sa.DateTime, default=sa.func.current_timestamp(),
          onupdate=sa.func.current_timestamp())
    )

def downgrade():
    op.drop_table("printers")
