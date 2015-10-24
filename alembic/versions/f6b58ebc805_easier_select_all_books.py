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
from sqlalchemy import MetaData, Table
from sqlalchemy.sql import select
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "printers",
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("book_companies.id"), primary_key = True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id"), primary_key = True),
        sa.Column("creator", sa.Integer(), sa.ForeignKey("librarians.id")),
        sa.Column("last_modifier", sa.Integer(), sa.ForeignKey("librarians.id")),
        sa.Column("date_created", sa.DateTime(), default=sa.func.current_timestamp()),
        sa.Column("date_modified", sa.DateTime(), default=sa.func.current_timestamp(),
          onupdate=sa.func.current_timestamp())
    )

    conn = op.get_bind()
    meta = MetaData(bind=conn)

    printers_table = Table("printers", meta, autoload=True)
    books_table = Table("books", meta, autoload=True)
    book_companies_table = Table("book_companies", meta, autoload=True)
    librarians_table = Table("librarians", meta, autoload=True)

    admin = conn.execute(select([librarians_table])
      .where(librarians_table.c.username == "admin")
      .limit(1)).fetchone()
    admin_id = admin[librarians_table.c.id]
    has_printers = conn.execute(select([books_table, book_companies_table])
      .where(book_companies_table.c.name == "")
      .where(books_table.c.printer == book_companies_table.c.id)).fetchall()

    for bwp in has_printers:
        book_id = bwp[books_table.c.id]
        company_id = bwp[book_companies.c.id]
        conn.execute(printers.insert(), company_id=company_id, book_id=book_id,
          creator=admin_id)


def downgrade():
    op.drop_table("printers")
